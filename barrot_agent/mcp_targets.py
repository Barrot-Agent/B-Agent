"""
MCP Targets – Step 1
====================
Defines Barrot's capability targets, supported MCP servers, and compatibility
requirements.  All definitions are *data-only* (no network calls here).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Capability targets
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CapabilityTarget:
    """A single capability gap that Barrot wants to fill via MCP tooling."""

    id: str
    name: str
    priority: str  # "low" | "medium" | "high" | "critical"
    description: str
    required_tool_categories: List[str] = field(default_factory=list)
    min_maturity: str = "stable"  # "experimental" | "beta" | "stable"


CAPABILITY_TARGETS: List[CapabilityTarget] = [
    CapabilityTarget(
        id="cap-001",
        name="Multi-agent coordination",
        priority="high",
        description="Orchestrate specialised sub-agents to tackle complex tasks in parallel.",
        required_tool_categories=["agent_communication", "task_distribution"],
    ),
    CapabilityTarget(
        id="cap-002",
        name="Real-time security monitoring",
        priority="critical",
        description="Detect anomalies, scan dependencies, and surface CVEs automatically.",
        required_tool_categories=["security_scanning", "dependency_audit"],
    ),
    CapabilityTarget(
        id="cap-003",
        name="Market analysis and trading recommendations",
        priority="medium",
        description="Ingest financial data and surface actionable signals.",
        required_tool_categories=["financial_data", "signal_generation"],
    ),
    CapabilityTarget(
        id="cap-004",
        name="System degradation prediction",
        priority="medium",
        description="Model performance drift and pre-emptively flag failures.",
        required_tool_categories=["observability", "predictive_modelling"],
    ),
    CapabilityTarget(
        id="cap-005",
        name="Data contradiction resolution",
        priority="medium",
        description="Detect and reconcile conflicting facts across knowledge sources.",
        required_tool_categories=["knowledge_graph", "fact_checking"],
    ),
    CapabilityTarget(
        id="cap-006",
        name="Video analysis and autofix",
        priority="medium",
        description="Parse video content and propose automated corrections.",
        required_tool_categories=["vision", "media_processing"],
    ),
    CapabilityTarget(
        id="cap-007",
        name="Creative content production",
        priority="medium",
        description="Generate scripts, images, and audio for the Stupid Sindy pipeline.",
        required_tool_categories=["generative_media", "text_generation"],
    ),
    CapabilityTarget(
        id="cap-008",
        name="Resource allocation engine",
        priority="medium",
        description="Optimise compute and budget allocation across workloads.",
        required_tool_categories=["resource_management", "optimisation"],
    ),
]


# ---------------------------------------------------------------------------
# Supported MCP server catalogue
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MCPServerSpec:
    """Static specification for a known MCP server."""

    name: str
    server_id: str
    description: str
    tool_categories: List[str]
    homepage: str
    license: str
    min_python: str = "3.10"
    requires_auth: bool = False
    env_vars: List[str] = field(default_factory=list)


SUPPORTED_MCP_SERVERS: List[MCPServerSpec] = [
    MCPServerSpec(
        name="mcp-server-git",
        server_id="barrot-core-repository",
        description="Read/write access to Git repositories via MCP.",
        tool_categories=["version_control", "code_review"],
        homepage="https://github.com/modelcontextprotocol/servers/tree/main/src/git",
        license="MIT",
    ),
    MCPServerSpec(
        name="mcp-server-github",
        server_id="github",
        description="GitHub API operations (issues, PRs, Actions).",
        tool_categories=["version_control", "ci_cd"],
        homepage="https://github.com/modelcontextprotocol/servers/tree/main/src/github",
        license="MIT",
        requires_auth=True,
        env_vars=["GITHUB_PERSONAL_ACCESS_TOKEN"],
    ),
    MCPServerSpec(
        name="mcp-server-filesystem",
        server_id="filesystem",
        description="Read/write local filesystem with path restrictions.",
        tool_categories=["file_management"],
        homepage="https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
        license="MIT",
    ),
    MCPServerSpec(
        name="mcp-server-fetch",
        server_id="fetch",
        description="HTTP fetch for read-only web content retrieval.",
        tool_categories=["web_access"],
        homepage="https://github.com/modelcontextprotocol/servers/tree/main/src/fetch",
        license="MIT",
    ),
    MCPServerSpec(
        name="mcp-server-brave-search",
        server_id="brave-search",
        description="Web and news search via Brave Search API.",
        tool_categories=["web_search", "information_retrieval"],
        homepage="https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search",
        license="MIT",
        requires_auth=True,
        env_vars=["BRAVE_API_KEY"],
    ),
    MCPServerSpec(
        name="mcp-server-memory",
        server_id="memory",
        description="Persistent knowledge-graph memory for agent sessions.",
        tool_categories=["knowledge_graph", "fact_checking"],
        homepage="https://github.com/modelcontextprotocol/servers/tree/main/src/memory",
        license="MIT",
    ),
    MCPServerSpec(
        name="mcp-server-postgres",
        server_id="postgres",
        description="Read-only SQL queries against a PostgreSQL database.",
        tool_categories=["database", "data_access"],
        homepage="https://github.com/modelcontextprotocol/servers/tree/main/src/postgres",
        license="MIT",
        requires_auth=True,
        env_vars=["POSTGRES_URL"],
    ),
]


# ---------------------------------------------------------------------------
# Compatibility requirements
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CompatibilityRequirements:
    """System-wide compatibility constraints for MCP components."""

    min_mcp_spec_version: str = "2024-11-05"
    min_python_version: str = "3.10"
    allowed_licenses: List[str] = field(
        default_factory=lambda: ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause"]
    )
    forbidden_env_vars: List[str] = field(
        default_factory=lambda: ["AWS_SECRET_ACCESS_KEY", "DATABASE_URL"]
    )
    max_dependency_count: int = 20
    require_provenance_record: bool = True
    require_human_approval_for_writes: bool = True


COMPATIBILITY_REQUIREMENTS = CompatibilityRequirements()


def get_targets_by_priority(priority: str) -> List[CapabilityTarget]:
    """Return capability targets filtered by priority level."""
    return [t for t in CAPABILITY_TARGETS if t.priority == priority]


def get_server_by_id(server_id: str) -> Optional[MCPServerSpec]:
    """Look up a supported server spec by its server_id."""
    for srv in SUPPORTED_MCP_SERVERS:
        if srv.server_id == server_id:
            return srv
    return None
