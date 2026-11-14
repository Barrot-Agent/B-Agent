"""Live, concurrent MCP synchronization engine.

What this does (all evidence-producing, no fabrication):

1. Loads every MCP server declared in ``opencode.json`` (new ``mcp.servers``
   shape or the legacy top-level shape) and ``mcp_config.json`` (``mcpServers``).
2. Probes them *concurrently* (asyncio / threads / sequential) with a real MCP
   ``initialize`` + ``tools/list`` JSON-RPC exchange.
3. Normalizes every tool into a deterministic record (name, description,
   schema hash, inferred capability categories).
4. Merges partial/asynchronous outcomes: transient failures are retried, and
   any still-missing server is back-filled from the last known-good snapshot
   and explicitly marked ``source="cache"`` (never silently presented as live).
5. Detects capability gaps against ``CAPABILITY_TARGETS`` and proposes static
   catalogue candidates for each gap (marked ``source="static-spec"``).

Local stdio servers are *not executed* unless ``include_local_exec=True``;
``npx -y`` / ``uvx`` can install packages, so that is an explicit opt-in.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import hashlib
import json
import os
import queue
import re
import shutil
import subprocess
import threading
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from barrot_agent.mcp_targets import CAPABILITY_TARGETS, SUPPORTED_MCP_SERVERS

PROTOCOL_VERSION = "2025-06-18"
CLIENT_INFO = {"name": "barrot-mcp-sync", "version": "1.0.0"}

_ENV_RE = re.compile(r"\{env:([A-Za-z_][A-Za-z0-9_]*)\}")

# Capability inference: phrase/regex rules applied to the normalized tool name
# and description. Deliberately strict -- loose substrings (e.g. "scan" inside
# "scanned") would falsely claim coverage and hide real capability gaps.
_CATEGORY_PATTERNS: Dict[str, Tuple[str, ...]] = {
    "agent_communication": (r"agent\s+message", r"\bdelegate\b", r"\bhandoff\b", r"agent\s+communication"),
    "task_distribution": (r"task\s+queue", r"\bdispatch\b", r"schedule\s+task", r"task\s+distribution"),
    "security_scanning": (r"security\s+scan", r"vulnerabilit", r"\bcve\b", r"\bexploit\b"),
    "dependency_audit": (r"dependency\s+audit", r"\bsbom\b", r"package\s+audit", r"license\s+audit"),
    "financial_data": (r"market\s+data", r"stock\s+price", r"crypto\s+price", r"financial\s+data", r"trading\s+data"),
    "signal_generation": (r"trading\s+signal", r"generate\s+signal", r"signal\s+generation", r"\bindicator\b"),
    "observability": (r"\bmetrics?\b", r"\btraces?\b", r"\btelemetry\b", r"\bmonitor"),
    "predictive_modelling": (r"\bpredict", r"\bforecast", r"anomaly\s+detection"),
    "knowledge_graph": (r"knowledge\s+graph", r"\bmemory\b", r"\bentity\b"),
    "fact_checking": (r"fact[\s-]?check", r"\bcorroborat", r"\bverify\s+claim"),
    "vision": (r"\bvision\b", r"image\s+caption", r"object\s+detection", r"\bocr\b"),
    "media_processing": (r"\bvideo\b", r"\baudio\b", r"\btranscod", r"media\s+processing"),
    "generative_media": (
        r"generate\s+(?:an?\s+)?image",
        r"image\s+generation",
        r"edit\b[^\n.]{0,20}\bimages?\b",
        r"\bvideo\b",
        r"\baudio\b",
        r"\brender\b",
    ),
    "text_generation": (r"text\s+generation", r"\bsummariz", r"\bcompletion\b", r"generate\s+text"),
    "resource_management": (r"\bquota\b", r"\bbudget\b", r"compute\s+allocation", r"allocate\s+resource"),
    "optimisation": (r"\boptimi[sz]", r"\bminimi[sz]", r"\bmaximi[sz]", r"\btune\b"),
    # Extra categories used by live servers; harmless if no target references them.
    "web_search": (r"web\s+search", r"search\s+the\s+web", r"news\s+search"),
    "web_access": (r"\bfetch\b", r"\bbrowse\b", r"\bscrape\b", r"http\s+request"),
    "document_conversion": (r"convert\s+(?:a\s+)?document", r"\bocr\b", r"\bpdf\b", r"\bmarkdown\b"),
    "image_generation": (
        r"generate\s+(?:an?\s+)?image",
        r"image\s+generation",
        r"edit\b[^\n.]{0,20}\bimages?\b",
    ),
    "version_control": (r"\bgit\b", r"\bcommit\b", r"\bbranch\b", r"\bdiff\b"),
    "ci_cd": (r"\bworkflow\b", r"pull\s+request", r"github\s+actions"),
    "file_management": (r"file\s*system", r"\bdirectory\b", r"upload\s+(?:an?\s+)?image", r"read\s+file"),
}
_COMPILED_PATTERNS: Dict[str, Tuple["re.Pattern[str]", ...]] = {
    category: tuple(re.compile(pattern, re.IGNORECASE) for pattern in patterns)
    for category, patterns in _CATEGORY_PATTERNS.items()
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class MCPServerConfig:
    name: str
    transport: str  # "remote" | "stdio"
    url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    command: List[str] = field(default_factory=list)
    enabled: bool = True
    source: str = ""
    missing_env: List[str] = field(default_factory=list)


@dataclass
class ToolRecord:
    server: str
    name: str
    description: str = ""
    input_schema: Dict[str, Any] = field(default_factory=dict)
    categories: List[str] = field(default_factory=list)
    source: str = "live"  # live | cache | static-spec
    schema_hash: str = ""

    def __post_init__(self) -> None:
        if not self.schema_hash:
            raw = json.dumps(self.input_schema, sort_keys=True, separators=(",", ":"))
            self.schema_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass
class ServerProbe:
    name: str
    transport: str
    status: str  # connected | auth_missing | unreachable | timeout | error | cached | disabled
    url: str = ""
    protocol_version: str = ""
    server_info: Dict[str, Any] = field(default_factory=dict)
    tools: List[ToolRecord] = field(default_factory=list)
    latency_ms: float = 0.0
    attempts: int = 0
    error: str = ""
    source: str = "live"  # live | cache | static
    missing_env: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


def _resolve_value(value: str) -> Tuple[str, List[str]]:
    """Substitute ``{env:VAR}`` placeholders, reporting any that are unset."""
    missing: List[str] = []

    def repl(match: "re.Match[str]") -> str:
        var = match.group(1)
        val = os.environ.get(var)
        if val is None:
            missing.append(var)
            return ""
        return val

    return _ENV_RE.sub(repl, value), missing


def _resolve_headers(raw: Dict[str, Any]) -> Tuple[Dict[str, str], List[str]]:
    headers: Dict[str, str] = {}
    missing: List[str] = []
    for key, value in raw.items():
        text, miss = _resolve_value(str(value))
        headers[str(key)] = text
        missing.extend(miss)
    return headers, sorted(set(missing))


def _load_opencode_servers(path: Path) -> List[MCPServerConfig]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    mcp = data.get("mcp") or {}
    if not isinstance(mcp, dict):
        return []

    entries: Dict[str, Any] = {}
    servers = mcp.get("servers")
    if isinstance(servers, dict):
        entries.update(servers)
    # Legacy shape: mcp.<name> directly.
    for key, value in mcp.items():
        if key == "servers" or not isinstance(value, dict):
            continue
        if "url" in value or "command" in value or value.get("type") in ("remote", "local"):
            entries.setdefault(key, value)

    out: List[MCPServerConfig] = []
    for name, cfg in entries.items():
        if not isinstance(cfg, dict):
            continue
        enabled = cfg.get("enabled", True) is not False and cfg.get("disabled", False) is not True
        if "url" in cfg:
            headers, missing = _resolve_headers(cfg.get("headers") or {})
            out.append(
                MCPServerConfig(
                    name=str(name),
                    transport="remote",
                    url=str(cfg.get("url", "")),
                    headers=headers,
                    enabled=enabled,
                    source=str(path),
                    missing_env=missing,
                )
            )
        elif "command" in cfg:
            cmd = cfg.get("command")
            command = [str(c) for c in cmd] if isinstance(cmd, list) else [str(cmd)]
            out.append(
                MCPServerConfig(
                    name=str(name),
                    transport="stdio",
                    command=command,
                    enabled=enabled,
                    source=str(path),
                )
            )
    return out


def _load_mcp_config_servers(path: Path) -> List[MCPServerConfig]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    out: List[MCPServerConfig] = []
    for name, cfg in (data.get("mcpServers") or {}).items():
        if not isinstance(cfg, dict):
            continue
        if "url" in cfg:
            headers, missing = _resolve_headers(cfg.get("headers") or {})
            out.append(
                MCPServerConfig(
                    name=str(name),
                    transport="remote",
                    url=str(cfg.get("url", "")),
                    headers=headers,
                    source=str(path),
                    missing_env=missing,
                )
            )
        elif "command" in cfg:
            command = [str(cfg["command"])] + [str(a) for a in cfg.get("args", [])]
            out.append(
                MCPServerConfig(
                    name=str(name),
                    transport="stdio",
                    command=command,
                    source=str(path),
                )
            )
    return out


def load_configs(repo_root: Path) -> List[MCPServerConfig]:
    """Load and de-duplicate all declared MCP servers (first declaration wins)."""
    candidates: List[MCPServerConfig] = []
    for filename, loader in (
        ("opencode.json", _load_opencode_servers),
        ("mcp_config.json", _load_mcp_config_servers),
    ):
        path = repo_root / filename
        if path.is_file():
            candidates.extend(loader(path))

    seen: set = set()
    unique: List[MCPServerConfig] = []
    for cfg in candidates:
        if cfg.name in seen:
            continue
        seen.add(cfg.name)
        unique.append(cfg)
    return unique


# ---------------------------------------------------------------------------
# Capability inference / gap analysis
# ---------------------------------------------------------------------------


def infer_categories(text: str) -> List[str]:
    """Infer primary capability categories from a tool name/description.

    Names are normalized (``generate_image`` -> ``generate image``) before
    matching, and only the compiled phrase rules above are used.
    """
    haystack = re.sub(r"[_\-]+", " ", text.lower())
    found = [
        category
        for category, patterns in _COMPILED_PATTERNS.items()
        if any(pattern.search(haystack) for pattern in patterns)
    ]
    return sorted(set(found))


def _tool_record(server: str, raw: Dict[str, Any], source: str = "live") -> ToolRecord:
    name = str(raw.get("name", ""))
    description = str(raw.get("description", ""))
    schema = raw.get("inputSchema") or raw.get("input_schema") or {}
    return ToolRecord(
        server=server,
        name=name,
        description=description,
        input_schema=schema if isinstance(schema, dict) else {},
        categories=infer_categories(name + " " + description),
        source=source,
    )


def compute_gaps(targets: Sequence[Any], tools: Iterable[ToolRecord]) -> List[Dict[str, Any]]:
    covered: set = set()
    for tool in tools:
        covered.update(tool.categories)

    gaps: List[Dict[str, Any]] = []
    for target in targets:
        required = set(getattr(target, "required_tool_categories", []) or [])
        # A target is covered only when *all* required categories are present.
        if required and required <= covered:
            continue
        gaps.append(
            {
                "target_id": getattr(target, "id", ""),
                "name": getattr(target, "name", ""),
                "priority": getattr(target, "priority", ""),
                "required_tool_categories": sorted(required),
                "covered_categories": sorted(required & covered),
                "missing_categories": sorted(required - covered),
                "covered_by": [],
                "candidates": [],
                "filled": False,
                "reason": "not all required categories have a live tool",
            }
        )
    return gaps


def fill_gaps(gaps: List[Dict[str, Any]], specs: Sequence[Any] = SUPPORTED_MCP_SERVERS) -> List[Dict[str, Any]]:
    """Back-fill each gap with static catalogue candidates (clearly labelled).

    ``filled`` is only true when a candidate covers *every* required category.
    Partial candidates are still reported for human review.
    """
    for gap in gaps:
        required = set(gap["required_tool_categories"])
        candidates = []
        for spec in specs:
            categories = set(getattr(spec, "tool_categories", []) or [])
            overlap = required & categories
            if not overlap:
                continue
            candidates.append(
                {
                    "server_id": getattr(spec, "server_id", ""),
                    "name": getattr(spec, "name", ""),
                    "matched_categories": sorted(overlap),
                    "full_match": required <= categories,
                    "license": getattr(spec, "license", ""),
                    "requires_auth": bool(getattr(spec, "requires_auth", False)),
                    "source": "static-spec",
                }
            )
        gap["candidates"] = candidates
        gap["filled"] = any(c["full_match"] for c in candidates)
    return gaps


# ---------------------------------------------------------------------------
# MCP transports
# ---------------------------------------------------------------------------


def _post_json(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: float) -> Tuple[int, str, str]:
    body = json.dumps(payload).encode("utf-8")
    request_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    request_headers.update(headers)
    req = urllib.request.Request(url, data=body, headers=request_headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        content_type = resp.headers.get("Content-Type", "")
        raw = resp.read().decode("utf-8", "replace")
        return resp.status, content_type, raw


def _parse_rpc(raw: str, content_type: str) -> Dict[str, Any]:
    if "text/event-stream" in content_type.lower():
        for line in raw.splitlines():
            if not line.startswith("data:"):
                continue
            payload = line[len("data:") :].strip()
            if payload and payload != "[DONE]":
                try:
                    return json.loads(payload)
                except json.JSONDecodeError:
                    continue
        raise ValueError("no JSON-RPC payload found in SSE response")
    return json.loads(raw)


def _rpc(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: float) -> Dict[str, Any]:
    _, content_type, raw = _post_json(url, headers, payload, timeout)
    message = _parse_rpc(raw, content_type)
    if isinstance(message, dict) and message.get("error"):
        raise RuntimeError(json.dumps(message["error"])[:300])
    return message


def _initialize_payload() -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": CLIENT_INFO,
        },
    }


def probe_remote(cfg: MCPServerConfig, timeout: float = 20.0, retries: int = 1) -> ServerProbe:
    start = time.perf_counter()
    if cfg.missing_env:
        return ServerProbe(
            name=cfg.name,
            transport=cfg.transport,
            status="auth_missing",
            url=cfg.url,
            error=f"unset environment variable(s): {', '.join(cfg.missing_env)}",
            missing_env=list(cfg.missing_env),
            latency_ms=0.0,
        )

    last_error = ""
    attempts = 0
    for attempt in range(retries + 1):
        attempts += 1
        try:
            init = _rpc(cfg.url, cfg.headers, _initialize_payload(), timeout)
            result = init.get("result") or {}
            # Best-effort initialized notification; some servers are stateless.
            try:
                _rpc(
                    cfg.url,
                    cfg.headers,
                    {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
                    timeout,
                )
            except Exception:  # noqa: BLE001 - notification is optional
                pass

            listed = _rpc(
                cfg.url,
                cfg.headers,
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
                timeout,
            )
            raw_tools = (listed.get("result") or {}).get("tools") or []
            tools = [_tool_record(cfg.name, t) for t in raw_tools if isinstance(t, dict)]
            return ServerProbe(
                name=cfg.name,
                transport=cfg.transport,
                status="connected",
                url=cfg.url,
                protocol_version=str(result.get("protocolVersion", "")),
                server_info=result.get("serverInfo") or {},
                tools=tools,
                latency_ms=round((time.perf_counter() - start) * 1000, 1),
                attempts=attempts,
            )
        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", "replace")[:300]
            except Exception:  # noqa: BLE001
                pass
            last_error = f"HTTP {exc.code}: {body}"
            if exc.code in (401, 403):
                return ServerProbe(
                    name=cfg.name,
                    transport=cfg.transport,
                    status="auth_missing",
                    url=cfg.url,
                    error=last_error,
                    latency_ms=round((time.perf_counter() - start) * 1000, 1),
                    attempts=attempts,
                    missing_env=list(cfg.missing_env),
                )
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = str(exc)
        except Exception as exc:  # noqa: BLE001
            last_error = f"{exc.__class__.__name__}: {exc}"
        if attempt < retries:
            time.sleep(0.25 * (attempt + 1))

    status = "timeout" if "timed out" in last_error.lower() else "unreachable"
    return ServerProbe(
        name=cfg.name,
        transport=cfg.transport,
        status=status,
        url=cfg.url,
        error=last_error,
        latency_ms=round((time.perf_counter() - start) * 1000, 1),
        attempts=attempts,
        missing_env=list(cfg.missing_env),
    )


def _readline_with_timeout(stream: Any, timeout: float) -> str:
    result: "queue.Queue[str]" = queue.Queue()

    def reader() -> None:
        try:
            result.put(stream.readline())
        except Exception as exc:  # noqa: BLE001
            result.put(f"__ERROR__{exc}")

    threading.Thread(target=reader, daemon=True).start()
    try:
        line = result.get(timeout=timeout)
    except queue.Empty as exc:
        raise TimeoutError(f"no stdio response within {timeout}s") from exc
    if line.startswith("__ERROR__"):
        raise RuntimeError(line[len("__ERROR__") :])
    if not line:
        raise RuntimeError("server closed stdout")
    return line


def probe_stdio(cfg: MCPServerConfig, timeout: float = 20.0, allow_exec: bool = False) -> ServerProbe:
    start = time.perf_counter()
    if not cfg.command:
        return ServerProbe(name=cfg.name, transport=cfg.transport, status="error", error="empty command")
    executable = shutil.which(cfg.command[0])
    if executable is None:
        return ServerProbe(
            name=cfg.name,
            transport=cfg.transport,
            status="unreachable",
            error=f"command not found: {cfg.command[0]}",
            latency_ms=round((time.perf_counter() - start) * 1000, 1),
        )
    if not allow_exec:
        return ServerProbe(
            name=cfg.name,
            transport=cfg.transport,
            status="unreachable",
            error="local stdio execution disabled (pass include_local_exec=True to opt in)",
            latency_ms=round((time.perf_counter() - start) * 1000, 1),
        )

    proc: Optional[subprocess.Popen[str]] = None
    try:
        proc = subprocess.Popen(  # noqa: S603 - command comes from local config
            [executable] + cfg.command[1:],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        assert proc.stdin is not None and proc.stdout is not None
        proc.stdin.write(json.dumps(_initialize_payload()) + "\n")
        proc.stdin.flush()
        init = json.loads(_readline_with_timeout(proc.stdout, timeout))
        proc.stdin.write(
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}) + "\n"
        )
        proc.stdin.write(
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}) + "\n"
        )
        proc.stdin.flush()
        listed = json.loads(_readline_with_timeout(proc.stdout, timeout))
        result = init.get("result") or {}
        raw_tools = (listed.get("result") or {}).get("tools") or []
        return ServerProbe(
            name=cfg.name,
            transport=cfg.transport,
            status="connected",
            protocol_version=str(result.get("protocolVersion", "")),
            server_info=result.get("serverInfo") or {},
            tools=[_tool_record(cfg.name, t) for t in raw_tools if isinstance(t, dict)],
            latency_ms=round((time.perf_counter() - start) * 1000, 1),
            attempts=1,
        )
    except Exception as exc:  # noqa: BLE001
        return ServerProbe(
            name=cfg.name,
            transport=cfg.transport,
            status="error",
            error=f"{exc.__class__.__name__}: {exc}",
            latency_ms=round((time.perf_counter() - start) * 1000, 1),
            attempts=1,
        )
    finally:
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:  # noqa: BLE001
                try:
                    proc.kill()
                except Exception:  # noqa: BLE001
                    pass


def probe_server(
    cfg: MCPServerConfig,
    timeout: float = 20.0,
    retries: int = 1,
    include_local_exec: bool = False,
) -> ServerProbe:
    if not cfg.enabled:
        return ServerProbe(
            name=cfg.name, transport=cfg.transport, status="disabled", url=cfg.url
        )
    if cfg.transport == "remote":
        return probe_remote(cfg, timeout=timeout, retries=retries)
    return probe_stdio(cfg, timeout=timeout, allow_exec=include_local_exec)


def probe_all(
    servers: Sequence[MCPServerConfig],
    mode: str = "threads",
    timeout: float = 20.0,
    retries: int = 1,
    include_local_exec: bool = False,
) -> List[ServerProbe]:
    """Probe all servers using one of three strategies: sequential, threads, async."""
    if not servers:
        return []
    if mode == "sequential":
        return [probe_server(s, timeout, retries, include_local_exec) for s in servers]
    if mode == "threads":
        workers = min(16, len(servers))
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [
                pool.submit(probe_server, s, timeout, retries, include_local_exec) for s in servers
            ]
            return [f.result() for f in futures]
    if mode == "async":
        async def run() -> List[ServerProbe]:
            return await asyncio.gather(
                *[
                    asyncio.to_thread(probe_server, s, timeout, retries, include_local_exec)
                    for s in servers
                ]
            )

        return asyncio.run(run())
    raise ValueError(f"unknown mode: {mode}")


# ---------------------------------------------------------------------------
# Snapshot merge / cache back-fill
# ---------------------------------------------------------------------------


def load_cache(cache_path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        return data.get("servers", {}) if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def merge_cached(probes: Sequence[ServerProbe], cached: Dict[str, Any]) -> List[ServerProbe]:
    """Back-fill non-connected servers from the last known-good snapshot."""
    for probe in probes:
        if probe.status == "connected":
            continue
        entry = cached.get(probe.name)
        if not isinstance(entry, dict) or not entry.get("tools"):
            continue
        tools = []
        for raw in entry["tools"]:
            if not isinstance(raw, dict):
                continue
            tools.append(
                ToolRecord(
                    server=probe.name,
                    name=str(raw.get("name", "")),
                    description=str(raw.get("description", "")),
                    input_schema=raw.get("input_schema") or {},
                    categories=list(raw.get("categories") or []),
                    source="cache",
                )
            )
        if not tools:
            continue
        probe.tools = tools
        probe.source = "cache"
        probe.status = "cached"
        probe.error = (probe.error + " | served from last-known-good cache").strip(" |")
    return list(probes)


def _tool_as_dict(tool: ToolRecord) -> Dict[str, Any]:
    return {
        "server": tool.server,
        "name": tool.name,
        "description": tool.description,
        "categories": tool.categories,
        "schema_hash": tool.schema_hash,
        "input_schema": tool.input_schema,
        "source": tool.source,
    }


def build_snapshot(probes: Sequence[ServerProbe], elapsed_ms: float, mode: str) -> Dict[str, Any]:
    all_tools = [tool for probe in probes for tool in probe.tools]
    gaps = fill_gaps(compute_gaps(CAPABILITY_TARGETS, all_tools))
    statuses: Dict[str, int] = {}
    for probe in probes:
        statuses[probe.status] = statuses.get(probe.status, 0) + 1
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "elapsed_ms": round(elapsed_ms, 1),
        "summary": {
            "servers_total": len(probes),
            "servers_reachable": sum(
                1 for p in probes if p.status in ("connected", "cached")
            ),
            "servers_live": sum(1 for p in probes if p.status == "connected"),
            "tools_total": len(all_tools),
            "tools_live": sum(1 for t in all_tools if t.source == "live"),
            "gaps_total": len(gaps),
            "gaps_filled_static": sum(1 for g in gaps if g["filled"]),
            "statuses": statuses,
        },
        "servers": {
            probe.name: {
                "transport": probe.transport,
                "status": probe.status,
                "source": probe.source,
                "url": probe.url,
                "protocol_version": probe.protocol_version,
                "server_info": probe.server_info,
                "latency_ms": probe.latency_ms,
                "attempts": probe.attempts,
                "error": probe.error,
                "missing_env": probe.missing_env,
                "tools": [_tool_as_dict(t) for t in sorted(probe.tools, key=lambda t: t.name)],
            }
            for probe in sorted(probes, key=lambda p: p.name)
        },
        "gaps": gaps,
    }


def write_outputs(snapshot: Dict[str, Any], out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = out_dir / "snapshot.json"
    cache_path = out_dir / "last_good.json"
    log_path = out_dir / "sync_log.jsonl"

    snapshot_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")

    existing = load_cache(cache_path)
    for name, server in snapshot["servers"].items():
        if server["status"] == "connected" and server["tools"]:
            existing[name] = server
    cache_path.write_text(
        json.dumps({"generated_at": snapshot["generated_at"], "servers": existing}, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "generated_at": snapshot["generated_at"],
                    "mode": snapshot["mode"],
                    "elapsed_ms": snapshot["elapsed_ms"],
                    "summary": snapshot["summary"],
                },
                sort_keys=True,
            )
            + "\n"
        )
    return {
        "snapshot": str(snapshot_path),
        "cache": str(cache_path),
        "log": str(log_path),
    }


def synchronize(
    repo_root: Path,
    mode: str = "threads",
    timeout: float = 20.0,
    retries: int = 1,
    include_local_exec: bool = False,
    cache_path: Optional[Path] = None,
) -> Dict[str, Any]:
    servers = load_configs(repo_root)
    start = time.perf_counter()
    probes = probe_all(servers, mode=mode, timeout=timeout, retries=retries, include_local_exec=include_local_exec)
    cached = load_cache(cache_path) if cache_path else {}
    probes = merge_cached(probes, cached)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return build_snapshot(probes, elapsed_ms, mode)
