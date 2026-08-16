"""
MCP Discovery Layer – Step 2
=============================
Read-only inventory of available MCP tools, their schemas, versions,
licenses, dependencies, and security posture.

All operations here are *read-only* and produce plain data structures.
No upstream code is modified and no writes are performed.
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from barrot_agent.mcp_targets import SUPPORTED_MCP_SERVERS, MCPServerSpec

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Discovery data structures
# ---------------------------------------------------------------------------


@dataclass
class ToolSchema:
    """JSON-schema representation of a single MCP tool."""

    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityPosture:
    """Security assessment derived from static analysis of a server spec."""

    requires_auth: bool
    exposed_env_vars: List[str]
    known_cves: List[str] = field(default_factory=list)
    last_scanned: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    risk_level: str = "unknown"  # "low" | "medium" | "high" | "critical"


@dataclass
class ServerInventory:
    """Full inventory record for one discovered MCP server."""

    server_id: str
    name: str
    description: str
    version: str
    license: str
    homepage: str
    tool_categories: List[str]
    tools: List[ToolSchema]
    dependencies: List[str]
    security: SecurityPosture
    discovered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_hash: str = ""

    def __post_init__(self) -> None:
        if not self.schema_hash:
            raw = json.dumps(
                [{"name": t.name, "schema": t.input_schema} for t in self.tools],
                sort_keys=True,
            )
            self.schema_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Discovery engine
# ---------------------------------------------------------------------------


class MCPDiscovery:
    """
    Read-only MCP discovery layer.

    Iterates over :data:`SUPPORTED_MCP_SERVERS` and builds an in-memory
    inventory without making any modifications to the file-system,
    repositories, or running services.
    """

    def __init__(
        self,
        mcp_config_path: Optional[Path] = None,
        pip_executable: str = sys.executable,
    ) -> None:
        self._config_path = mcp_config_path or Path("mcp_config.json")
        self._pip_exec = pip_executable
        self._inventory: Dict[str, ServerInventory] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def discover_all(self) -> Dict[str, ServerInventory]:
        """
        Run discovery against all entries in SUPPORTED_MCP_SERVERS.

        Returns a mapping of ``server_id -> ServerInventory``.
        """
        logger.info("MCP discovery: scanning %d server specs", len(SUPPORTED_MCP_SERVERS))
        for spec in SUPPORTED_MCP_SERVERS:
            try:
                inv = self._discover_server(spec)
                self._inventory[spec.server_id] = inv
                logger.debug("Discovered: %s (%d tools)", spec.server_id, len(inv.tools))
            except Exception as exc:  # noqa: BLE001
                logger.warning("Discovery failed for %s: %s", spec.server_id, exc)
        return dict(self._inventory)

    def get_inventory(self, server_id: str) -> Optional[ServerInventory]:
        """Return the cached inventory record for a server, or None."""
        return self._inventory.get(server_id)

    def to_json(self) -> str:
        """Serialise the full inventory to a JSON string (read-only export)."""
        output: Dict[str, Any] = {}
        for sid, inv in self._inventory.items():
            output[sid] = {
                "server_id": inv.server_id,
                "name": inv.name,
                "version": inv.version,
                "license": inv.license,
                "homepage": inv.homepage,
                "tool_categories": inv.tool_categories,
                "tools": [{"name": t.name, "description": t.description} for t in inv.tools],
                "dependencies": inv.dependencies,
                "security": {
                    "requires_auth": inv.security.requires_auth,
                    "exposed_env_vars": inv.security.exposed_env_vars,
                    "known_cves": inv.security.known_cves,
                    "risk_level": inv.security.risk_level,
                    "last_scanned": inv.security.last_scanned,
                },
                "schema_hash": inv.schema_hash,
                "discovered_at": inv.discovered_at,
            }
        return json.dumps(output, indent=2)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _discover_server(self, spec: MCPServerSpec) -> ServerInventory:
        """Build an inventory record from static spec data + optional live probe."""
        version = self._probe_package_version(spec.name)
        deps = self._probe_package_deps(spec.name)
        security = self._assess_security(spec, deps)
        tools = self._infer_tools(spec)
        return ServerInventory(
            server_id=spec.server_id,
            name=spec.name,
            description=spec.description,
            version=version,
            license=spec.license,
            homepage=spec.homepage,
            tool_categories=list(spec.tool_categories),
            tools=tools,
            dependencies=deps,
            security=security,
        )

    def _probe_package_version(self, package_name: str) -> str:
        """
        Ask pip for the installed version of *package_name*.

        Returns ``"unknown"`` if the package is not installed or pip
        cannot be reached – this is a read-only probe and never installs
        anything.
        """
        try:
            result = subprocess.run(
                [self._pip_exec, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()
        except Exception:  # noqa: BLE001
            pass
        return "unknown"

    def _probe_package_deps(self, package_name: str) -> List[str]:
        """
        Return the list of declared Requires for *package_name* from pip.

        Read-only; never installs anything.
        """
        try:
            result = subprocess.run(
                [self._pip_exec, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in result.stdout.splitlines():
                if line.startswith("Requires:"):
                    raw = line.split(":", 1)[1].strip()
                    return [d.strip() for d in raw.split(",") if d.strip()]
        except Exception:  # noqa: BLE001
            pass
        return []

    def _assess_security(self, spec: MCPServerSpec, deps: List[str]) -> SecurityPosture:
        """Derive a static security posture from spec metadata."""
        risk = "low"
        if spec.requires_auth:
            risk = "medium"
        if len(deps) > 15:
            risk = "medium"
        if any(
            kw in spec.description.lower() for kw in ("write", "exec", "shell", "run", "deploy")
        ):
            risk = "high"
        return SecurityPosture(
            requires_auth=spec.requires_auth,
            exposed_env_vars=list(spec.env_vars),
            risk_level=risk,
        )

    # Static tool inference from well-known server categories
    _TOOL_CATALOGUE: Dict[str, List[Dict[str, str]]] = {
        "version_control": [
            {"name": "git_status", "description": "Show working-tree status"},
            {"name": "git_log", "description": "Show commit history"},
            {"name": "git_diff", "description": "Show changes between commits"},
            {"name": "git_read_file", "description": "Read a file at a given ref"},
        ],
        "ci_cd": [
            {"name": "list_workflows", "description": "List GitHub Actions workflows"},
            {"name": "get_workflow_run", "description": "Get a specific workflow run"},
            {"name": "list_pull_requests", "description": "List pull requests"},
        ],
        "file_management": [
            {"name": "read_file", "description": "Read a file from the filesystem"},
            {"name": "list_directory", "description": "List a directory"},
            {"name": "search_files", "description": "Search for files by pattern"},
        ],
        "web_access": [
            {"name": "fetch_url", "description": "Fetch a URL and return its content"},
        ],
        "web_search": [
            {"name": "brave_web_search", "description": "Search the web via Brave"},
            {"name": "brave_news_search", "description": "Search news via Brave"},
        ],
        "knowledge_graph": [
            {"name": "memory_store", "description": "Store a fact in the knowledge graph"},
            {"name": "memory_query", "description": "Query the knowledge graph"},
        ],
        "database": [
            {"name": "sql_query", "description": "Execute a read-only SQL query"},
        ],
        "longevity_research": [
            {"name": "search_papers", "description": "Search cited longevity research records"},
            {"name": "search_trials", "description": "Search cited clinical-trial updates"},
            {"name": "ingest_research", "description": "Normalize research in memory without persistence"},
            {"name": "generate_mmi_payload", "description": "Generate a provenance-rich MMI payload"},
        ],
        "biomarker_analysis": [
            {"name": "track_biomarker", "description": "Analyze a consented biomarker trajectory"},
        ],
        "trial_analysis": [
            {"name": "compare_treatment_arms", "description": "Compare de-identified treatment arms"},
            {"name": "detect_signals", "description": "Detect efficacy and safety research signals"},
        ],
    }

    def _infer_tools(self, spec: MCPServerSpec) -> List[ToolSchema]:
        """Build a static list of likely tools based on the server's categories."""
        tools: List[ToolSchema] = []
        seen: set = set()
        for cat in spec.tool_categories:
            for entry in self._TOOL_CATALOGUE.get(cat, []):
                if entry["name"] not in seen:
                    seen.add(entry["name"])
                    tools.append(
                        ToolSchema(
                            name=entry["name"],
                            description=entry["description"],
                        )
                    )
        return tools
