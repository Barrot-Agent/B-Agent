"""
MCP Adapters – Step 4
======================
Adapts selected MCP server components for use inside Barrot's framework
*without* modifying upstream code directly.

Each adapter wraps a server's tool list behind a stable, versioned
interface.  If the upstream tool schema changes the adapter is updated
here, isolating the rest of Barrot from upstream churn.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from barrot_agent.mcp_discovery import ServerInventory, ToolSchema

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Adapter base
# ---------------------------------------------------------------------------


@dataclass
class AdapterResult:
    """Unified return type for every adapted tool call."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    tool_name: str = ""
    server_id: str = ""


class BaseMCPAdapter(ABC):
    """
    Abstract base for all MCP server adapters.

    Subclasses MUST implement :meth:`supported_tools` and
    :meth:`call_tool`.  They MUST NOT modify upstream server code.
    """

    adapter_version: str = "1.0.0"

    def __init__(self, inventory: ServerInventory) -> None:
        self._inventory = inventory
        self._tool_map: Dict[str, ToolSchema] = {t.name: t for t in inventory.tools}

    @property
    def server_id(self) -> str:
        return self._inventory.server_id

    @abstractmethod
    def supported_tools(self) -> List[str]:
        """Return the list of tool names this adapter exposes."""

    @abstractmethod
    def call_tool(self, tool_name: str, **kwargs: Any) -> AdapterResult:
        """
        Call *tool_name* with the given keyword arguments.

        Adapters translate between Barrot's internal calling convention and
        whatever the upstream tool expects.  They never modify upstream code.
        """

    def validate_tool(self, tool_name: str) -> bool:
        """Return True if *tool_name* is supported by this adapter."""
        return tool_name in self.supported_tools()

    def _wrap_call(
        self,
        tool_name: str,
        fn: Callable[..., Any],
        **kwargs: Any,
    ) -> AdapterResult:
        """Execute *fn* and wrap the result in :class:`AdapterResult`."""
        try:
            result = fn(**kwargs)
            return AdapterResult(
                success=True,
                data=result,
                tool_name=tool_name,
                server_id=self.server_id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Adapter call failed: server=%s tool=%s error=%s",
                self.server_id,
                tool_name,
                exc,
            )
            return AdapterResult(
                success=False,
                error=str(exc),
                tool_name=tool_name,
                server_id=self.server_id,
            )


# ---------------------------------------------------------------------------
# Git server adapter
# ---------------------------------------------------------------------------


class GitMCPAdapter(BaseMCPAdapter):
    """
    Adapter for ``mcp-server-git``.

    Provides a stable interface to git read operations.  Write operations
    (commit, push) are blocked at the adapter layer and always require
    human approval via :mod:`barrot_agent.mcp_approval`.
    """

    _WRITE_TOOLS = {"git_commit", "git_push", "git_create_branch"}

    def supported_tools(self) -> List[str]:
        return ["git_status", "git_log", "git_diff", "git_read_file"]

    def call_tool(self, tool_name: str, **kwargs: Any) -> AdapterResult:
        if tool_name in self._WRITE_TOOLS:
            return AdapterResult(
                success=False,
                error=f"Write tool '{tool_name}' blocked: human approval required.",
                tool_name=tool_name,
                server_id=self.server_id,
            )
        if not self.validate_tool(tool_name):
            return AdapterResult(
                success=False,
                error=f"Unknown tool '{tool_name}' for adapter {self.server_id}.",
                tool_name=tool_name,
                server_id=self.server_id,
            )
        # Delegate to internal implementation
        impl = getattr(self, f"_impl_{tool_name}", None)
        if impl is None:
            return AdapterResult(
                success=False,
                error=f"No implementation for '{tool_name}' in {self.__class__.__name__}.",
                tool_name=tool_name,
                server_id=self.server_id,
            )
        return self._wrap_call(tool_name, impl, **kwargs)

    # ---- Implementations --------------------------------------------------

    def _impl_git_status(self, repo_path: str = ".") -> Dict[str, Any]:
        import subprocess

        r = subprocess.run(
            ["git", "-C", repo_path, "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return {"output": r.stdout, "returncode": r.returncode}

    def _impl_git_log(self, repo_path: str = ".", n: int = 10) -> Dict[str, Any]:
        import subprocess

        r = subprocess.run(
            ["git", "-C", repo_path, "log", f"-{n}", "--oneline"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return {"output": r.stdout, "returncode": r.returncode}

    def _impl_git_diff(self, repo_path: str = ".", ref: str = "HEAD") -> Dict[str, Any]:
        import subprocess

        r = subprocess.run(
            ["git", "-C", repo_path, "diff", ref],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return {"output": r.stdout, "returncode": r.returncode}

    def _impl_git_read_file(
        self, repo_path: str = ".", file_path: str = "", ref: str = "HEAD"
    ) -> Dict[str, Any]:
        import subprocess

        r = subprocess.run(
            ["git", "-C", repo_path, "show", f"{ref}:{file_path}"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return {"output": r.stdout, "returncode": r.returncode}


# ---------------------------------------------------------------------------
# Filesystem adapter (read-only)
# ---------------------------------------------------------------------------


class FilesystemMCPAdapter(BaseMCPAdapter):
    """
    Adapter for ``mcp-server-filesystem``.

    Restricted to read-only operations within an allowed root path.
    """

    def __init__(
        self,
        inventory: ServerInventory,
        allowed_root: str = ".",
    ) -> None:
        super().__init__(inventory)
        self._allowed_root = allowed_root

    def supported_tools(self) -> List[str]:
        return ["read_file", "list_directory", "search_files"]

    def call_tool(self, tool_name: str, **kwargs: Any) -> AdapterResult:
        if not self.validate_tool(tool_name):
            return AdapterResult(
                success=False,
                error=f"Unknown tool '{tool_name}'.",
                tool_name=tool_name,
                server_id=self.server_id,
            )
        impl = getattr(self, f"_impl_{tool_name}", None)
        if impl is None:
            return AdapterResult(
                success=False,
                error=f"No implementation for '{tool_name}'.",
                tool_name=tool_name,
                server_id=self.server_id,
            )
        return self._wrap_call(tool_name, impl, **kwargs)

    def _impl_read_file(self, path: str) -> Dict[str, Any]:
        from pathlib import Path

        p = Path(self._allowed_root) / path
        p = p.resolve()
        allowed = Path(self._allowed_root).resolve()
        if not p.is_relative_to(allowed):
            raise PermissionError(f"Path '{p}' is outside allowed root '{allowed}'.")
        return {"content": p.read_text(encoding="utf-8")}

    def _impl_list_directory(self, path: str = ".") -> Dict[str, Any]:
        from pathlib import Path

        p = Path(self._allowed_root) / path
        p = p.resolve()
        allowed = Path(self._allowed_root).resolve()
        if not p.is_relative_to(allowed):
            raise PermissionError(f"Path '{p}' is outside allowed root '{allowed}'.")
        return {"entries": [e.name for e in p.iterdir()]}

    def _impl_search_files(self, pattern: str, root: str = ".") -> Dict[str, Any]:
        from pathlib import Path

        base = Path(self._allowed_root) / root
        base = base.resolve()
        allowed = Path(self._allowed_root).resolve()
        if not base.is_relative_to(allowed):
            raise PermissionError(f"Search root '{base}' is outside allowed root '{allowed}'.")
        matches = [str(p.relative_to(allowed)) for p in base.rglob(pattern)]
        return {"matches": matches}


class LongevityMCPAdapter(BaseMCPAdapter):
    """Adapter for the local, read-only longevity MCP service."""

    def __init__(self, inventory: ServerInventory, **kwargs: Any) -> None:
        super().__init__(inventory)
        from longevity_mcp import LongevityMCPServer

        self._service = LongevityMCPServer(**kwargs)

    def supported_tools(self) -> List[str]:
        return self._service.supported_tools()

    def call_tool(self, tool_name: str, **kwargs: Any) -> AdapterResult:
        if tool_name in {"apply_protocol", "write_dataset", "store_participant"}:
            return AdapterResult(
                success=False,
                error="Write operation blocked: human approval required.",
                tool_name=tool_name,
                server_id=self.server_id,
            )
        if not self.validate_tool(tool_name):
            return AdapterResult(
                success=False,
                error=f"Unknown tool '{tool_name}'.",
                tool_name=tool_name,
                server_id=self.server_id,
            )
        return self._wrap_call(
            tool_name,
            lambda **call_kwargs: self._service.call_tool(tool_name, **call_kwargs),
            **kwargs,
        )

    def read_resource(self, resource: str) -> Dict[str, Any]:
        return self._service.read_resource(resource)


# ---------------------------------------------------------------------------
# Adapter registry
# ---------------------------------------------------------------------------

_ADAPTER_CLASSES: Dict[str, type] = {
    "barrot-core-repository": GitMCPAdapter,
    "filesystem": FilesystemMCPAdapter,
    "longevity-research": LongevityMCPAdapter,
}


def build_adapter(inventory: ServerInventory, **kwargs: Any) -> Optional[BaseMCPAdapter]:
    """
    Factory function: return the appropriate adapter for *inventory*, or
    ``None`` if no adapter is registered for that server.
    """
    cls = _ADAPTER_CLASSES.get(inventory.server_id)
    if cls is None:
        logger.debug("No adapter registered for server_id=%s", inventory.server_id)
        return None
    return cls(inventory, **kwargs)
