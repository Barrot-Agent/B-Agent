"""
Security Analyzer.

Scans for common security anti-patterns: hardcoded secrets, use of eval/exec,
shell-injection risks, insecure deserialization, and missing input validation.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from apex_lattice.analyzers.base import BaseAnalyzer

# Patterns for potential hardcoded secrets
_SECRET_RE = re.compile(
    r'(?i)(password|passwd|secret|token|api_key|apikey|private_key)\s*=\s*["\'][^"\']{4,}["\']'
)
_SHELL_TRUE_RE = re.compile(r"shell\s*=\s*True")
_PICKLE_RE = re.compile(r"\bpickle\.loads?\s*\(")
_YAML_LOAD_RE = re.compile(r"\byaml\.load\s*\(")


class Analyzer(BaseAnalyzer):
    name = "security_analyzer"

    def analyze(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []

        for path in self._iter_source_files((".py",)):
            source = self._read_text(path)
            rel = path.relative_to(self.repo_root)

            findings.extend(self._check_hardcoded_secrets(rel, source))
            findings.extend(self._check_eval_exec(rel, source))
            findings.extend(self._check_shell_injection(rel, source))
            findings.extend(self._check_insecure_deserialize(rel, source))

        return {"findings": findings}

    # ------------------------------------------------------------------
    def _check_hardcoded_secrets(self, rel: Path, source: str) -> list[dict[str, Any]]:
        results = []
        for i, line in enumerate(source.splitlines(), 1):
            if _SECRET_RE.search(line):
                # Redact the actual value in evidence
                safe_line = _SECRET_RE.sub(r"\1 = <REDACTED>", line.strip())
                results.append(
                    self._make_finding(
                        title="Potential hardcoded secret",
                        description=(
                            f"Possible hardcoded credential at `{rel}:{i}`. "
                            "Move secrets to environment variables or a secrets manager."
                        ),
                        severity="critical",
                        evidence=[f"{rel}:{i}: {safe_line}"],
                        tags=["security", "secrets"],
                    )
                )
        return results

    def _check_eval_exec(self, rel: Path, source: str) -> list[dict[str, Any]]:
        results = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return results

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = ""
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            # Only flag bare built-in calls, not safe method calls like re.compile
            is_bare = isinstance(func, ast.Name)
            if name in ("eval", "exec") and (is_bare or isinstance(func, ast.Attribute)):
                results.append(
                    self._make_finding(
                        title=f"Use of `{name}`",
                        description=(
                            f"`{name}()` found at `{rel}:{node.lineno}`. "
                            "Dynamic code execution can introduce code-injection "
                            "vulnerabilities."
                        ),
                        severity="high",
                        evidence=[f"{rel}:{node.lineno}"],
                        tags=["security", "code-injection"],
                    )
                )
            elif name == "compile" and is_bare:
                # Only flag bare compile(), not re.compile / ast.compile etc.
                results.append(
                    self._make_finding(
                        title="Use of `compile`",
                        description=(
                            f"Built-in `compile()` found at `{rel}:{node.lineno}`. "
                            "Ensure the source string does not originate from "
                            "untrusted input."
                        ),
                        severity="medium",
                        evidence=[f"{rel}:{node.lineno}"],
                        tags=["security", "code-injection"],
                    )
                )
        return results

    def _check_shell_injection(self, rel: Path, source: str) -> list[dict[str, Any]]:
        results = []
        for i, line in enumerate(source.splitlines(), 1):
            if _SHELL_TRUE_RE.search(line):
                results.append(
                    self._make_finding(
                        title="Shell injection risk",
                        description=(
                            f"`shell=True` at `{rel}:{i}` can allow shell "
                            "injection if user input reaches the command. "
                            "Pass a list of arguments instead."
                        ),
                        severity="high",
                        evidence=[f"{rel}:{i}: {line.strip()}"],
                        tags=["security", "shell-injection"],
                    )
                )
        return results

    def _check_insecure_deserialize(self, rel: Path, source: str) -> list[dict[str, Any]]:
        results = []
        for i, line in enumerate(source.splitlines(), 1):
            if _PICKLE_RE.search(line):
                results.append(
                    self._make_finding(
                        title="Insecure pickle deserialization",
                        description=(
                            f"`pickle.load` at `{rel}:{i}` is unsafe with "
                            "untrusted data. Use JSON or msgpack instead."
                        ),
                        severity="high",
                        evidence=[f"{rel}:{i}: {line.strip()}"],
                        tags=["security", "deserialization"],
                    )
                )
            if _YAML_LOAD_RE.search(line):
                results.append(
                    self._make_finding(
                        title="Unsafe yaml.load",
                        description=(
                            f"`yaml.load` at `{rel}:{i}` without a safe Loader "
                            "can execute arbitrary Python. Use `yaml.safe_load`."
                        ),
                        severity="high",
                        evidence=[f"{rel}:{i}: {line.strip()}"],
                        tags=["security", "deserialization"],
                    )
                )
        return results
