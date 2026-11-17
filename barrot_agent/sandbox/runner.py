"""Isolated experiment runner.

A run gets its own directory, copied inputs and modules, a fresh interpreter
(``python -I``), a wall-clock timeout, CPU/memory/file-size limits, and a
captured stdout/stderr.  A passing run is kept; a failing run is deleted after
its log line is written.

This is process isolation, not a security boundary.  It does not use
containers, namespaces or a separate user.  It is only meant to keep a failed
experiment away from the live repository and from the operator's environment.

Experiment contract:

* the script runs with its own directory as the working directory;
* the parent directory is **not** on ``sys.path`` (the script can add it, and
  should, when importing a copied module);
* on pass, the script should leave ``result.json`` with a ``metrics`` object
  and ``"passed": true``; exit code 0 is also required;
* on fail, exit non-zero or write ``"passed": false``.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SANDBOX_ROOT = PROJECT_ROOT / "data" / "sandbox"
DEFAULT_TIMEOUT_S = 60
DEFAULT_MEMORY_MB = 512
# Android's bionic linker reserves address space at interpreter start. With
# RLIMIT_AS below this floor the child dies inside the loader with
# "MapShadow CHECK 'p != MAP_FAILED'" before any user code runs, so the limit
# would measure the loader, not the experiment. Callers may still pass 0 to
# disable the address-space limit entirely.
MIN_MEMORY_MB = 3072 if sys.platform == "android" else 0
DEFAULT_CPU_SECONDS = 60
DEFAULT_MAX_OUTPUT_CHARS = 20_000
DEFAULT_MAX_FILE_BYTES = 64 * 1024 * 1024


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug(text: str) -> str:
    clean = "".join(character if character.isalnum() else "-" for character in text.lower())
    return "-".join(part for part in clean.split("-") if part)[:48] or "experiment"


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... [{len(text) - limit} chars clipped]"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _preexec(memory_mb: int, cpu_seconds: int, max_file_bytes: int):
    """Build a POSIX pre-exec hook; ignored on platforms without ``resource``."""

    def apply() -> None:  # pragma: no cover - exercised in a child process
        try:
            import resource
        except ImportError:
            return
        if cpu_seconds:
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        if memory_mb:
            limit = memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
        if max_file_bytes:
            resource.setrlimit(
                resource.RLIMIT_FSIZE, (max_file_bytes, max_file_bytes)
            )

    return apply


@dataclass
class SandboxResult:
    """Outcome of one sandboxed run."""

    run_id: str
    name: str
    passed: bool
    kept: bool
    exit_code: int | None
    timed_out: bool
    duration_s: float
    stdout: str
    stderr: str
    run_dir: str
    log_path: str
    metrics: dict = field(default_factory=dict)
    script_sha256: str = ""

    def summary(self) -> str:
        """One-line result for logs and CLI output."""
        state = "PASS/kept" if self.passed else "FAIL/discarded"
        return (
            f"{self.run_id} {state} exit={self.exit_code} "
            f"timed_out={self.timed_out} {self.duration_s:.2f}s"
        )

    def as_dict(self) -> dict:
        """JSON-safe representation for the log and PHOENIX state."""
        return {
            "run_id": self.run_id,
            "name": self.name,
            "at": _utc_now(),
            "passed": self.passed,
            "kept": self.kept,
            "exit_code": self.exit_code,
            "timed_out": self.timed_out,
            "duration_s": round(self.duration_s, 4),
            "stdout": self.stdout,
            "stderr": self.stderr,
            "run_dir": self.run_dir,
            "log_path": self.log_path,
            "metrics": self.metrics,
            "script_sha256": self.script_sha256,
        }


class SandboxRunner:
    """Run one experiment in a fresh, disposable directory.

    Args:
        root: Sandbox root; runs live in ``root/runs/<run_id>``.
        python: Interpreter used for the child (defaults to this interpreter).
        timeout: Wall-clock limit in seconds.
        memory_mb: Address-space limit for the child (POSIX only).
        cpu_seconds: CPU-time limit for the child (POSIX only).
        max_output_chars: stdout/stderr retained in the log.
        max_file_bytes: Largest file the child may write.
        keep_on_fail: Keep the directory even when the experiment fails.
    """

    def __init__(
        self,
        root: str | Path = DEFAULT_SANDBOX_ROOT,
        python: str = sys.executable,
        timeout: float = DEFAULT_TIMEOUT_S,
        memory_mb: int = DEFAULT_MEMORY_MB,
        cpu_seconds: int = DEFAULT_CPU_SECONDS,
        max_output_chars: int = DEFAULT_MAX_OUTPUT_CHARS,
        max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
        keep_on_fail: bool = False,
    ):
        self.root = Path(root)
        self.python = python
        self.timeout = timeout
        requested_memory_mb = int(memory_mb or 0)
        self.memory_mb = (
            max(requested_memory_mb, MIN_MEMORY_MB) if requested_memory_mb else 0
        )
        self.cpu_seconds = cpu_seconds
        self.max_output_chars = max_output_chars
        self.max_file_bytes = max_file_bytes
        self.keep_on_fail = keep_on_fail
        self.runs_dir = self.root / "runs"
        self.log_path = self.root / "runs.jsonl"

    def run(
        self,
        *,
        name: str,
        script: str | None = None,
        script_path: str | Path | None = None,
        inputs: dict[str, str | Path] | None = None,
        modules: dict[str, str | Path] | None = None,
        run_id: str | None = None,
    ) -> SandboxResult:
        """Execute ``script`` (or ``script_path``) and keep only a passing run."""
        if bool(script) == bool(script_path):
            raise ValueError("pass exactly one of script or script_path")
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        run_id = run_id or f"{_utc_now().replace(':', '').replace('-', '')}-{_slug(name)}"
        run_dir = self.runs_dir / run_id
        work = run_dir / "work"
        if run_dir.exists():
            shutil.rmtree(run_dir)
        work.mkdir(parents=True)

        target = work / "experiment.py"
        if script_path is not None:
            source = Path(script_path)
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            target.write_text(script or "", encoding="utf-8")

        for destination, source in (inputs or {}).items():
            self._copy_into(work, destination, source)
        for destination, source in (modules or {}).items():
            self._copy_into(work, destination, source)

        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONHASHSEED": "0",
            "HOME": str(work),
            "TMPDIR": str(work),
        }
        command = [self.python, "-I", str(target)]
        started = _now_monotonic()
        timed_out = False
        exit_code: int | None = None
        stdout = ""
        stderr = ""
        try:
            process = subprocess.Popen(
                command,
                cwd=work,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
                preexec_fn=_preexec(self.memory_mb, self.cpu_seconds, self.max_file_bytes),
            )
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                if os.name == "posix":
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        process.kill()
                else:  # pragma: no cover - non-POSIX fallback
                    process.kill()
                stdout, stderr = process.communicate()
            exit_code = process.returncode
        except OSError as exc:
            stderr = f"{type(exc).__name__}: {exc}"
        duration = _now_monotonic() - started

        payload = self._read_result(work / "result.json")
        passed = (
            not timed_out
            and exit_code == 0
            and payload.get("passed", True) is True
        )
        kept = passed or self.keep_on_fail
        result = SandboxResult(
            run_id=run_id,
            name=name,
            passed=passed,
            kept=kept,
            exit_code=exit_code,
            timed_out=timed_out,
            duration_s=duration,
            stdout=_clip(stdout, self.max_output_chars),
            stderr=_clip(stderr, self.max_output_chars),
            run_dir=str(run_dir.relative_to(self.root)) if kept else "",
            log_path=str(self.log_path.relative_to(self.root)),
            metrics=payload.get("metrics", payload) if isinstance(payload, dict) else {},
            script_sha256=_sha256(target),
        )
        self._append_log(result, payload)
        if not kept:
            shutil.rmtree(run_dir, ignore_errors=True)
        return result

    # -- helpers ---------------------------------------------------------

    def _copy_into(self, work: Path, destination: str, source: str | Path) -> None:
        source_path = Path(source)
        if not source_path.is_file():
            raise FileNotFoundError(f"sandbox input not found: {source_path}")
        target = work / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target)

    def _read_result(self, path: Path) -> dict:
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def _append_log(self, result: SandboxResult, payload: dict) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        line = result.as_dict()
        line["result"] = payload
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(line, ensure_ascii=False) + "\n")


def _now_monotonic() -> float:
    import time

    return time.monotonic()
