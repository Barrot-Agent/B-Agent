#!/usr/bin/env python3
"""Regenerate docs/INDEX.md from the markdown files actually present."""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    docs_dir = root / "docs"
    docs = sorted(p for p in docs_dir.rglob("*.md") if p.name != "INDEX.md")
    groups: dict[str, list[tuple[str, str]]] = {}
    for path in docs:
        key = str(path.parent.relative_to(root)) if path.parent != docs_dir else "docs"
        title = "(no heading)"
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        groups.setdefault(key, []).append((str(path.relative_to(root)), title))
    out = [
        "# Docs index",
        "",
        "Generated. Every file under docs/, grouped by folder.",
        "Regenerate after adding a doc: python3 scripts/build_docs_index.py",
        "",
    ]
    for key in sorted(groups):
        out.append(f"## {key}")
        out.append("")
        out.extend(f"- {path} - {title}" for path, title in groups[key])
        out.append("")
    (docs_dir / "INDEX.md").write_text("\n".join(out), encoding="utf-8")
    print(f"indexed {len(docs)} docs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
