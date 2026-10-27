#!/usr/bin/env python3
"""Authoritative, machine-readable repository-state manifest.

Designed to extend the existing repo_snapshot()/reference-loading workflow.
The filesystem and Git state are authoritative; model claims are not.
"""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
}

KEY_FILES = {
    "scripts/barrot_task_allocator.py",
    "scripts/ask_barrot.py",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def iter_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        yield rel


def python_symbols(path: Path) -> dict:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    result = {}

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result.setdefault("functions", {})[node.name] = {
                "signature": _signature(node),
                "line": node.lineno,
            }
        elif isinstance(node, ast.ClassDef):
            result.setdefault("classes", {})[node.name] = {
                "line": node.lineno,
            }

    return result


def _signature(node) -> str:
    args = []

    positional = list(node.args.posonlyargs) + list(node.args.args)
    defaults = [None] * (
        len(positional) - len(node.args.defaults)
    ) + list(node.args.defaults)

    for arg, default in zip(positional, defaults):
        value = arg.arg
        if default is not None:
            value += "=" + ast.unparse(default)
        args.append(value)

    if node.args.vararg:
        args.append("*" + node.args.vararg.arg)
    elif node.args.kwonlyargs:
        args.append("*")

    for arg, default in zip(
        node.args.kwonlyargs,
        node.args.kw_defaults,
    ):
        value = arg.arg
        if default is not None:
            value += "=" + ast.unparse(default)
        args.append(value)

    if node.args.kwarg:
        args.append("**" + node.args.kwarg.arg)

    return f"{node.name}({', '.join(args)})"


def build_manifest() -> dict:
    files = sorted(str(p).replace("\\", "/") for p in iter_files())

    file_hashes = {}
    for rel in files:
        path = ROOT / rel
        try:
            file_hashes[rel] = sha256_file(path)
        except OSError:
            pass

    entrypoints = {}
    for rel in sorted(KEY_FILES):
        path = ROOT / rel
        if path.exists() and path.suffix == ".py":
            entrypoints[rel] = python_symbols(path)

    workflows = sorted(
        str(p.relative_to(ROOT)).replace("\\", "/")
        for p in (ROOT / ".github" / "workflows").glob("*")
        if p.is_file()
    ) if (ROOT / ".github" / "workflows").exists() else []

    recent = git(
        "log", "-10", "--date=iso-strict",
        "--pretty=format:%H%x09%ad%x09%s"
    )

    commits = []
    for line in recent.splitlines():
        parts = line.split("\t", 2)
        if len(parts) == 3:
            commits.append({
                "commit": parts[0],
                "date": parts[1],
                "subject": parts[2],
            })

    manifest = {
        "schema_version": "1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(ROOT),
        "repo": git("config", "--get", "remote.origin.url"),
        "git": {
            "head": git("rev-parse", "HEAD"),
            "branch": git(
                "symbolic-ref", "--short", "-q", "HEAD"
            ),
            "dirty": bool(git("status", "--porcelain")),
            "recent_commits": commits,
        },
        "tree": {
            "file_count": len(files),
            "files": files,
        },
        "file_hashes": file_hashes,
        "entrypoints": entrypoints,
        "workflows": workflows,
    }

    canonical = json.dumps(
        manifest,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    manifest["manifest_id"] = (
        "sha256:" + hashlib.sha256(canonical).hexdigest()
    )

    return manifest


def main() -> int:
    manifest = build_manifest()

    output = ROOT / ".barrot" / "repo_state_manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "status": "VERIFIED",
        "manifest_id": manifest["manifest_id"],
        "head": manifest["git"]["head"],
        "branch": manifest["git"]["branch"],
        "dirty": manifest["git"]["dirty"],
        "file_count": manifest["tree"]["file_count"],
        "output": str(output),
    }, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
