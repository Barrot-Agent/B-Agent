#!/usr/bin/env python3
"""Pull small, licensed workflow components with pinning and attribution.

Rules enforced here, not in prose:
  * the repository licence must be in ALLOWED, otherwise the component is refused
  * the file is fetched at a pinned commit SHA, so the pull is reproducible
  * an attribution header is prepended: repo, path, commit, licence, source URL
  * only workflow YAML is pulled; no repository is cloned

Usage: python3 scripts/pull_components.py
Writes: vendor/workflow-patterns/<name>.yml and data/harvest/components.json
"""

from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "vendor" / "workflow-patterns"
INDEX = ROOT / "data" / "harvest" / "components.json"

ALLOWED = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "CC0-1.0", "Unlicense", "0BSD"}

COMPONENTS = [
    {
        "name": "pytest-matrix",
        "repo": "Panniantong/Agent-Reach",
        "path": ".github/workflows/pytest.yml",
        "why": "python version matrix with a macos include entry and fail-fast false",
    },
    {
        "name": "concurrency-paths-ignore",
        "repo": "D4Vinci/Scrapling",
        "path": ".github/workflows/code-quality.yml",
        "why": "workflow-level concurrency group plus paths-ignore so doc edits do not run CI",
    },
    {
        "name": "mcp-registry-publish",
        "repo": "upstash/context7",
        "path": ".github/workflows/mcp-registry.yml",
        "why": "the only correct way to publish an MCP server to the registry: OIDC, server.json, mcp-publisher",
    },
]


def gh(args: list[str]) -> str:
    completed = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=90)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip()[:160])
    return completed.stdout


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    for component in COMPONENTS:
        repo = component["repo"]
        spdx = gh(["api", f"repos/{repo}", "--jq", '.license.spdx_id // "NONE"']).strip()
        if spdx not in ALLOWED:
            records.append({**component, "license": spdx, "status": "BLOCKED-LICENSE"})
            print(f"REFUSED {repo}: {spdx}")
            continue
        commit = gh(["api", f"repos/{repo}/commits?per_page=1", "--jq", ".[0].sha"]).strip()
        content = gh(["api", f"repos/{repo}/contents/{component['path']}?ref={commit}", "--jq", ".content"]).strip()
        text = base64.b64decode(content).decode("utf-8", "ignore")
        header = (
            f"# Vendored workflow pattern: {component['name']}\n"
            f"# Source: https://github.com/{repo}/blob/{commit}/{component['path']}\n"
            f"# Repository: {repo}\n"
            f"# Commit: {commit}\n"
            f"# Licence: {spdx}\n"
            f"# Pulled: 2026-11-17 by scripts/pull_components.py\n"
            f"# Why: {component['why']}\n"
            f"# This file is a reference copy. It is not executed by this repository.\n\n"
        )
        target = OUT_DIR / f"{component['name']}.yml"
        target.write_text(header + text, encoding="utf-8")
        records.append({
            **component,
            "license": spdx,
            "commit": commit,
            "source_url": f"https://github.com/{repo}/blob/{commit}/{component['path']}",
            "bytes": len(text),
            "local_path": str(target.relative_to(ROOT)),
            "status": "Q",
        })
        print(f"PULLED {component['name']} from {repo} ({spdx}) at {commit[:8]}, {len(text)} bytes")

    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps({
        "built_at": "2026-11-17",
        "allowed_licenses": sorted(ALLOWED),
        "components": records,
        "pulled": sum(1 for r in records if r["status"] == "Q"),
        "blocked": sum(1 for r in records if r["status"] == "BLOCKED-LICENSE"),
    }, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
