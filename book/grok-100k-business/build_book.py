#!/usr/bin/env python3
"""Assemble the Grok Bot $100K book from its TOC and chapter files.

Design rules:
- The TOC is the contract. Statements about length come from `toc.yaml`, never
  from a hand-typed total.
- Every unit is measured, not asserted: word count -> pages at `words_per_page`.
- A chapter that is short shows up as short. Nothing is padded to hit a number.
- Exit code 1 means the manuscript is structurally broken (missing file, empty
  draft, or a draft wildly outside its page budget). Missing *outlines* do not
  fail the build; they are reported.

Usage:
    python book/grok-100k-business/build_book.py
    python book/grok-100k-business/build_book.py --strict
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
TOC = ROOT / "toc.yaml"
DIST = ROOT / "dist"

DRAFT_MIN_RATIO = 0.60
DRAFT_MAX_RATIO = 1.50
COMPLETE = {"draft", "final"}


def load_toc() -> dict:
    with TOC.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def units(toc: dict) -> list[dict]:
    """Every unit in reading order, annotated with its container."""
    out: list[dict] = []
    for u in toc.get("front_matter", []):
        out.append({**u, "container": "Front Matter"})
    for part in toc.get("parts", []):
        for ch in part["chapters"]:
            out.append({**ch, "container": part["title"]})
    for part in toc.get("proposed", {}).get("parts", []):
        for ch in part["chapters"]:
            out.append({**ch, "container": part["title"], "proposed": True})
    for app in toc.get("proposed", {}).get("appendices", []):
        out.append({**app, "container": "Appendices", "proposed": True})
    return out


def count_words(text: str) -> int:
    """Prose words only: fenced code and HTML comments are excluded.

    Code samples are part of a technical book but they are not prose pages, and
    counting them would inflate the estimate.
    """
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"^\s{0,3}#{1,6}\s+.*$", " ", text, flags=re.M)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", text))


def pages_for(words: int, wpp: int) -> float:
    """Pages, to one decimal, so a half-empty chapter is visible as such."""
    if words == 0:
        return 0.0
    return round(words / wpp, 1)


def read_unit(path: Path) -> tuple[str, int]:
    if not path.exists():
        return "", 0
    text = path.read_text(encoding="utf-8")
    return text, count_words(text)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="fail on any non-final unit")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    toc = load_toc()
    wpp = int(toc["words_per_page"])
    rows = []
    missing = []
    problems = []

    for u in units(toc):
        path = ROOT / u["file"]
        text, words = read_unit(path)
        if not path.exists():
            missing.append(u["file"])
        est = pages_for(words, wpp)
        target = u["pages"]
        ratio = est / target if target else 0.0
        status = u.get("status", "draft")
        # A one-page slot is a page, not a word quota: dedications and forewords
        # are legitimately short. Only multi-page units get a word-budget check.
        if status in COMPLETE:
            if words == 0:
                problems.append(f"{u['id']}: marked {status} but empty")
            elif target < 2:
                pass
            elif ratio < DRAFT_MIN_RATIO:
                problems.append(f"{u['id']}: {est}p vs {target}p target ({ratio:.0%}) — under")
            elif ratio > DRAFT_MAX_RATIO:
                problems.append(f"{u['id']}: {est}p vs {target}p target ({ratio:.0%}) — over")
        rows.append(
            {
                "id": u["id"],
                "container": u["container"],
                "title": u["title"],
                "status": status,
                "target_pages": target,
                "words": words,
                "pages": est,
                "ratio": round(ratio, 2),
                "proposed": bool(u.get("proposed")),
                "file": u["file"],
                "missing": not path.exists(),
            }
        )

    stated = sum(r["target_pages"] for r in rows if not r["proposed"])
    delivered = sum(r["pages"] for r in rows)
    drafted_pages = sum(r["pages"] for r in rows if r["status"] in COMPLETE)
    drafted_target = sum(r["target_pages"] for r in rows if r["status"] in COMPLETE)

    report = {
        "slug": toc["slug"],
        "title": toc["title"],
        "words_per_page": wpp,
        "stated_pages": toc["stated_pages"],
        "units_in_supplied_toc": stated,
        "unaccounted_pages": toc["stated_pages"] - stated,
        "pages_present_in_repo": delivered,
        "drafted_pages": drafted_pages,
        "drafted_target_pages": drafted_target,
        "drafted_completion": round(drafted_pages / drafted_target, 3) if drafted_target else 0.0,
        "missing_files": missing,
        "problems": problems,
        "units": rows,
    }

    DIST.mkdir(parents=True, exist_ok=True)
    (DIST / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Assemble the reading order.
    chunks: list[str] = []
    current = None
    for r in rows:
        if r["container"] != current:
            current = r["container"]
            chunks.append(f"\n\n# {current}\n")
        body = (ROOT / r["file"]).read_text(encoding="utf-8") if not r["missing"] else ""
        chunks.append(f"\n\n<!-- {r['id']} | {r['status']} | {r['pages']}p/{r['target_pages']}p -->\n")
        chunks.append(body.strip() + "\n")
    (DIST / "book.md").write_text("".join(chunks).lstrip(), encoding="utf-8")

    if not args.quiet:
        print(f"{'unit':10s} {'status':9s} {'target':>7s} {'pages':>6s} {'words':>7s}  title")
        for r in rows:
            flag = "!" if r["missing"] else " "
            print(
                f"{flag}{r['id']:9s} {r['status']:9s} {r['target_pages']:7d} "
                f"{r['pages']:6.1f} {r['words']:7d}  {r['title'][:58]}"
            )
        print()
        print(f"supplied TOC units       : {stated} pages")
        print(f"source stated length     : {toc['stated_pages']} pages")
        print(f"unaccounted              : {toc['stated_pages'] - stated} pages")
        print(f"present in repo          : {delivered:.1f} pages")
        print(f"drafted / drafted target : {drafted_pages:.1f} / {drafted_target} "
              f"({report['drafted_completion']:.0%})")
        print(f"assembled                : {DIST / 'book.md'}")
        if missing:
            print(f"\nMISSING FILES ({len(missing)}):")
            for m in missing:
                print(f"  {m}")
        if problems:
            print(f"\nPROBLEMS ({len(problems)}):")
            for p in problems:
                print(f"  {p}")

    failed = bool(missing or problems)
    if args.strict:
        failed = failed or any(r["status"] not in COMPLETE for r in rows)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
