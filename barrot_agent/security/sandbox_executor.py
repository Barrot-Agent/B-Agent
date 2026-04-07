"""Sandboxed execution wrapper — run commands and Python code under resource limits."""

from __future__ import annotations

import resource
import subprocess
import sys
import textwrap
import threading
import time
from typing import Any, Dict, List, Optional


class ExecutionTimeoutError(Exception):
    """Raised when a sandboxed execution exceeds its allowed duration."""


class SandboxExecutor:
    """Execute shell commands and Python snippets with configurable resource limits.

    Resource limits (where supported by the OS) are applied to child processes
    via the ``resource`` module.  Execution statistics are tracked across calls
    so callers can audit usage.

    Example::

        executor = SandboxExecutor()
        result = executor.execute_command(["echo", "hello"], timeout=5)
        print(result["stdout"])
    """

    _DEFAULT_LIMITS: Dict[str, Any] = {
        "max_cpu_seconds": 30,
        "max_memory_bytes": 256 * 1024 * 1024,  # 256 MB
        "max_file_descriptors": 256,
        "max_processes": 10,
    }

    def __init__(self, limits: Optional[Dict[str, Any]] = None) -> None:
        self._limits: Dict[str, Any] = {**self._DEFAULT_LIMITS, **(limits or {})}
        self._stats: Dict[str, int] = {
            "commands_executed": 0,
            "python_snippets_executed": 0,
            "timeouts": 0,
            "errors": 0,
        }
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute_command(
        self,
        command: List[str],
        timeout: int = 30,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Run *command* in a subprocess with resource limits applied.

        Args:
            command:   Argument list (no shell expansion).
            timeout:   Wall-clock limit in seconds.
            env_vars:  Extra environment variables for the child process.

        Returns:
            Dict with keys ``returncode``, ``stdout``, ``stderr``,
            ``elapsed_seconds``.

        Raises:
            ExecutionTimeoutError: When the process exceeds *timeout*.
        """
        preexec = self._make_preexec()
        start = time.monotonic()
        try:
            proc = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env_vars,
                preexec_fn=preexec,
            )
        except subprocess.TimeoutExpired:
            with self._lock:
                self._stats["timeouts"] += 1
            raise ExecutionTimeoutError(
                f"Command {command!r} exceeded timeout of {timeout}s"
            )
        except Exception as exc:
            with self._lock:
                self._stats["errors"] += 1
            raise RuntimeError(f"Command execution failed: {exc}") from exc

        elapsed = time.monotonic() - start
        with self._lock:
            self._stats["commands_executed"] += 1

        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "elapsed_seconds": round(elapsed, 3),
        }

    def execute_python(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        """Execute a Python *code* string in an isolated subprocess.

        The snippet is written to the child's stdin; a fresh Python interpreter
        is spawned so that the parent's memory space is unaffected.

        Args:
            code:     Python source to execute.
            context:  (Unused in subprocess mode; reserved for future use.)
            timeout:  Wall-clock limit in seconds.

        Returns:
            Dict with keys ``returncode``, ``stdout``, ``stderr``,
            ``elapsed_seconds``.
        """
        dedented = textwrap.dedent(code)
        preexec = self._make_preexec()
        start = time.monotonic()
        try:
            proc = subprocess.run(
                [sys.executable, "-c", dedented],
                capture_output=True,
                text=True,
                timeout=timeout,
                preexec_fn=preexec,
            )
        except subprocess.TimeoutExpired:
            with self._lock:
                self._stats["timeouts"] += 1
            raise ExecutionTimeoutError(
                f"Python snippet exceeded timeout of {timeout}s"
            )
        except Exception as exc:
            with self._lock:
                self._stats["errors"] += 1
            raise RuntimeError(f"Python execution failed: {exc}") from exc

        elapsed = time.monotonic() - start
        with self._lock:
            self._stats["python_snippets_executed"] += 1

        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "elapsed_seconds": round(elapsed, 3),
        }

    def apply_resource_limits(self, limits: Dict[str, Any]) -> None:
        """Merge *limits* into the executor's active resource limit set.

        Args:
            limits: Partial dict with keys from ``_DEFAULT_LIMITS``.
        """
        with self._lock:
            self._limits.update(limits)

    def get_execution_stats(self) -> Dict[str, int]:
        """Return a copy of the execution statistics counter dict."""
        with self._lock:
            return dict(self._stats)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _make_preexec(self):  # type: ignore[return]
        """Return a callable that applies resource limits in the child process."""
        limits = dict(self._limits)

        def _apply() -> None:
            try:
                cpu = limits.get("max_cpu_seconds")
                if cpu:
                    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
                mem = limits.get("max_memory_bytes")
                if mem:
                    resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
                fds = limits.get("max_file_descriptors")
                if fds:
                    resource.setrlimit(resource.RLIMIT_NOFILE, (fds, fds))
                nproc = limits.get("max_processes")
                if nproc:
                    resource.setrlimit(resource.RLIMIT_NPROC, (nproc, nproc))
            except (ValueError, resource.error):
                # Some limits may not be lowerable below current hard limit
                pass

        return _apply
