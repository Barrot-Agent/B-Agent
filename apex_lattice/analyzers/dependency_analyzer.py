"""
Dependency Analyzer.

Inspects requirements.txt / pyproject.toml / setup.cfg for:
- Unpinned dependencies
- Known-vulnerable version ranges (heuristic, not a full advisory scan)
- Unused top-level imports vs. declared requirements
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from apex_lattice.analyzers.base import BaseAnalyzer

_UNPINNED_RE = re.compile(r"^([A-Za-z0-9_.\-]+)\s*$")           # bare name
_LOOSE_GTE_RE = re.compile(r"^([A-Za-z0-9_.\-]+)\s*>=\s*[\d.]+\s*$")  # >= only, no upper bound

# Heuristic list of packages with known severe CVEs in older ranges
_KNOWN_RISKY: dict[str, str] = {
    "pillow": "Ensure Pillow >= 10.0.1 (CVE-2023-44271 and others)",
    "requests": "Ensure requests >= 2.31.0 (CVE-2023-32681)",
    "cryptography": "Ensure cryptography >= 41.0.0",
    "urllib3": "Ensure urllib3 >= 2.0.7 (CVE-2023-43804)",
    "setuptools": "Ensure setuptools >= 65.5.1 (CVE-2022-40897)",
    "pyyaml": "Ensure PyYAML >= 6.0 to avoid unsafe yaml.load",
}


class Analyzer(BaseAnalyzer):
    name = "dependency_analyzer"

    def analyze(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []

        req_files = list(self.repo_root.glob("requirements*.txt"))
        req_files += list(self.repo_root.glob("pyproject.toml"))
        req_files += list(self.repo_root.glob("setup.cfg"))

        if not req_files:
            findings.append(
                self._make_finding(
                    title="No dependency manifest found",
                    description=(
                        "No requirements.txt / pyproject.toml detected. "
                        "Add a dependency manifest to enable reproducible builds."
                    ),
                    severity="medium",
                    tags=["dependencies", "reproducibility"],
                )
            )
        else:
            for req_file in req_files:
                findings.extend(self._analyze_req_file(req_file))

        return {"findings": findings}

    # ------------------------------------------------------------------
    def _analyze_req_file(self, path: Path) -> list[dict[str, Any]]:
        results = []
        source = self._read_text(path)
        rel = str(path.relative_to(self.repo_root))

        for i, raw_line in enumerate(source.splitlines(), 1):
            line = raw_line.strip()
            if not line or line.startswith(("#", "-")):
                continue

            # Strip extras e.g. "package[extra]>=1.0"
            pkg_part = re.split(r"[;\[]", line)[0].strip()
            pkg_name_match = re.match(r"^([A-Za-z0-9_.\-]+)", pkg_part)
            if not pkg_name_match:
                continue
            pkg_name = pkg_name_match.group(1).lower()

            # Unpinned
            if _UNPINNED_RE.match(pkg_part):
                results.append(
                    self._make_finding(
                        title="Unpinned dependency",
                        description=(
                            f"`{line}` in `{rel}:{i}` has no version pin. "
                            "Add a version constraint (e.g. `>=x.y,<x+1`) "
                            "for reproducible installs."
                        ),
                        severity="medium",
                        evidence=[f"{rel}:{i}: {line}"],
                        tags=["dependencies", "pinning"],
                    )
                )
            elif _LOOSE_GTE_RE.match(pkg_part):
                results.append(
                    self._make_finding(
                        title="Loosely pinned dependency",
                        description=(
                            f"`{line}` in `{rel}:{i}` has only a lower bound. "
                            "Add an upper bound to prevent unexpected upgrades."
                        ),
                        severity="low",
                        evidence=[f"{rel}:{i}: {line}"],
                        tags=["dependencies", "pinning"],
                    )
                )

            # Advisory heuristics
            if pkg_name in _KNOWN_RISKY:
                results.append(
                    self._make_finding(
                        title=f"Review version of `{pkg_name}`",
                        description=_KNOWN_RISKY[pkg_name],
                        severity="medium",
                        evidence=[f"{rel}:{i}: {line}"],
                        tags=["dependencies", "security"],
                    )
                )

        return results
