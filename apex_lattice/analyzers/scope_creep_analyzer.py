"""
Scope Creep Analyzer.

Real production repos reject PRs that touch more than what the task
required, regardless of whether the change works (this is one of the
three dimensions FrontierCode measures that SWE-Bench ignores).

Works from actual git history rather than a single PR diff (apex_lattice
runs against the whole repo, not one PR in isolation): inspects the last
N commits and flags any commit whose changed files span an unusually
large number of unrelated top-level directories - a real, checkable
proxy for scope creep, not a judgment about whether the content was
justified (that requires reading the task that motivated it).
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from apex_lattice.analyzers.base import BaseAnalyzer

_LOOKBACK_COMMITS = 30
_DIR_SPREAD_THRESHOLD = 4
_FILE_COUNT_THRESHOLD = 15


class Analyzer(BaseAnalyzer):
    name = "scope_creep_analyzer"

    def analyze(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []

        commits = self._recent_commits()
        for sha, subject in commits:
            files = self._files_changed(sha)
            if not files:
                continue
            top_dirs = {f.split("/")[0] if "/" in f else "." for f in files}
            if len(top_dirs) >= _DIR_SPREAD_THRESHOLD or len(files) >= _FILE_COUNT_THRESHOLD:
                findings.append(
                    self._make_finding(
                        title="Wide-scope commit",
                        description=(
                            f"Commit {sha[:8]} (\"{subject[:70]}\") touches "
                            f"{len(files)} file(s) across {len(top_dirs)} top-level "
                            f"area(s): {', '.join(sorted(top_dirs)[:8])}"
                            f"{' (+more)' if len(top_dirs) > 8 else ''}. Wide spread "
                            "isn't automatically wrong, but it's exactly the pattern "
                            "production reviewers reject without a clear single reason."
                        ),
                        severity="medium" if len(top_dirs) < _DIR_SPREAD_THRESHOLD * 2 else "high",
                        evidence=[f"{sha[:8]}: {len(files)} files, {len(top_dirs)} top-level dirs"],
                        tags=["scope-creep", "commit-hygiene"],
                    )
                )
        return {"findings": findings}

    def _recent_commits(self) -> list[tuple[str, str]]:
        try:
            out = subprocess.run(
                ["git", "log", f"-{_LOOKBACK_COMMITS}", "--pretty=format:%H\t%s"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=15,
            )
        except (subprocess.SubprocessError, OSError):
            return []
        if out.returncode != 0:
            return []
        commits = []
        for line in out.stdout.splitlines():
            if "\t" in line:
                sha, subject = line.split("\t", 1)
                commits.append((sha, subject))
        return commits

    def _files_changed(self, sha: str) -> list[str]:
        try:
            out = subprocess.run(
                ["git", "show", "--name-only", "--pretty=format:", sha],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=15,
            )
        except (subprocess.SubprocessError, OSError):
            return []
        if out.returncode != 0:
            return []
        return [l for l in out.stdout.splitlines() if l.strip()]
