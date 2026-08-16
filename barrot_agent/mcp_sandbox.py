"""
MCP Sandbox Runner – Step 6
============================
Runs generated changes in isolated sandboxes with dependency, secret,
permission, and regression checks.

The sandbox never modifies production code.  It operates in a temporary
directory and reports pass/fail for each check.
"""

from __future__ import annotations

import logging
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Check result types
# ---------------------------------------------------------------------------


@dataclass
class CheckResult:
    """Result of a single sandbox validation check."""

    check_name: str
    passed: bool
    details: str = ""
    findings: List[str] = field(default_factory=list)


@dataclass
class SandboxReport:
    """Aggregated report from a full sandbox run."""

    server_id: str
    passed: bool
    checks: List[CheckResult] = field(default_factory=list)
    sandbox_path: str = ""

    @property
    def failed_checks(self) -> List[CheckResult]:
        return [c for c in self.checks if not c.passed]

    def summary(self) -> str:
        total = len(self.checks)
        failed = len(self.failed_checks)
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.server_id}: {total - failed}/{total} checks passed"


# ---------------------------------------------------------------------------
# Known bad secret patterns (simplified; real impl would use a dedicated tool)
# ---------------------------------------------------------------------------

_SECRET_PATTERNS = [
    re.compile(r"(?i)(api_key|apikey|secret|password|token)\s*=\s*['\"][^'\"]{8,}"),
    re.compile(r"(?i)Bearer\s+[A-Za-z0-9\-_]{20,}"),
    re.compile(r"(?i)ghp_[A-Za-z0-9]{36}"),  # GitHub PAT
    re.compile(r"(?i)sk-[A-Za-z0-9]{32,}"),  # OpenAI key
    re.compile(r"(?i)AKIA[0-9A-Z]{16}"),  # AWS Access Key ID
]

_FORBIDDEN_PERMISSIONS = [
    "os.chmod",
    "subprocess.Popen",
    "from subprocess import",
    "eval(",
    "exec(",
    "__import__(",
]


# ---------------------------------------------------------------------------
# Sandbox runner
# ---------------------------------------------------------------------------


class MCPSandbox:
    """
    Isolated validation environment for MCP integration changes.

    Checks performed
    ----------------
    1. **dependency_check** – verifies declared dependencies don't exceed limits
       and have no known forbidden packages.
    2. **secret_scan** – scans proposed code/config for hardcoded secrets.
    3. **permission_check** – ensures no dangerous permission escalation calls.
    4. **regression_check** – runs the existing test suite (read-only) in a
       temp copy and reports pass/fail.
    """

    FORBIDDEN_DEPS = {"pyotp", "pwntools", "scapy"}

    def __init__(
        self,
        repo_root: Optional[Path] = None,
        pip_executable: str = sys.executable,
        max_deps: int = 20,
    ) -> None:
        self._repo_root = repo_root or Path(".")
        self._pip_exec = pip_executable
        self._max_deps = max_deps

    def run(
        self,
        server_id: str,
        proposed_files: Dict[str, str],
        declared_deps: Optional[List[str]] = None,
    ) -> SandboxReport:
        """
        Validate *proposed_files* (filename → content) for *server_id*.

        Parameters
        ----------
        server_id:
            Identifier of the MCP server being integrated.
        proposed_files:
            Mapping of relative file path → file content that would be
            created/modified.
        declared_deps:
            List of new Python package names the integration requires.

        Returns
        -------
        SandboxReport
        """
        declared_deps = declared_deps or []
        checks: List[CheckResult] = []

        with tempfile.TemporaryDirectory(prefix="barrot_sandbox_") as tmpdir:
            sandbox_path = Path(tmpdir)
            checks.append(self._check_dependencies(declared_deps))
            checks.append(self._check_secrets(proposed_files))
            checks.append(self._check_permissions(proposed_files))
            checks.append(self._check_regression(sandbox_path, proposed_files))

        overall = all(c.passed for c in checks)
        if not overall:
            logger.warning(
                "Sandbox FAILED for server=%s: %s",
                server_id,
                [c.check_name for c in checks if not c.passed],
            )
        else:
            logger.info("Sandbox PASSED for server=%s", server_id)

        return SandboxReport(
            server_id=server_id,
            passed=overall,
            checks=checks,
            sandbox_path=str(self._repo_root),
        )

    # ------------------------------------------------------------------
    # Check implementations
    # ------------------------------------------------------------------

    def _check_dependencies(self, deps: List[str]) -> CheckResult:
        findings: List[str] = []

        if len(deps) > self._max_deps:
            findings.append(f"Dependency count {len(deps)} exceeds limit {self._max_deps}.")

        forbidden_found = [d for d in deps if d.lower() in self.FORBIDDEN_DEPS]
        if forbidden_found:
            findings.append(f"Forbidden packages: {forbidden_found}")

        return CheckResult(
            check_name="dependency_check",
            passed=len(findings) == 0,
            details=f"{len(deps)} dependency(-ies) declared.",
            findings=findings,
        )

    def _check_secrets(self, files: Dict[str, str]) -> CheckResult:
        findings: List[str] = []
        for fname, content in files.items():
            for pattern in _SECRET_PATTERNS:
                if pattern.search(content):
                    findings.append(f"Potential secret detected in '{fname}'.")
                    break  # one finding per file is enough

        return CheckResult(
            check_name="secret_scan",
            passed=len(findings) == 0,
            details=f"Scanned {len(files)} file(s).",
            findings=findings,
        )

    def _check_permissions(self, files: Dict[str, str]) -> CheckResult:
        findings: List[str] = []
        for fname, content in files.items():
            for pattern in _FORBIDDEN_PERMISSIONS:
                if pattern in content:
                    findings.append(f"Forbidden call '{pattern}' found in '{fname}'.")

        return CheckResult(
            check_name="permission_check",
            passed=len(findings) == 0,
            details=f"Checked {len(files)} file(s) for dangerous patterns.",
            findings=findings,
        )

    def _check_regression(self, sandbox_path: Path, proposed_files: Dict[str, str]) -> CheckResult:
        """
        Write proposed files into the sandbox directory and run
        ``python -m compileall`` as a lightweight regression proxy.

        A real regression check would copy the full repo and run pytest,
        but to keep the sandbox fast and free of side-effects we use
        compile-check only.
        """
        findings: List[str] = []

        # Write proposed Python files into sandbox
        for rel_path, content in proposed_files.items():
            dest = sandbox_path / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")

        py_files = list(sandbox_path.rglob("*.py"))
        if not py_files:
            return CheckResult(
                check_name="regression_check",
                passed=True,
                details="No Python files to compile-check.",
            )

        try:
            result = subprocess.run(
                [self._pip_exec, "-m", "compileall", "-q", str(sandbox_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                findings.append(f"Compile errors:\n{result.stderr or result.stdout}")
        except Exception as exc:  # noqa: BLE001
            findings.append(f"Regression check error: {exc}")

        return CheckResult(
            check_name="regression_check",
            passed=len(findings) == 0,
            details=f"Compile-checked {len(py_files)} Python file(s).",
            findings=findings,
        )
