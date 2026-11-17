"""Structural and governance tests for the Grok Bot $100K book project.

These do not judge the prose. They enforce the contract:

- the TOC is complete and internally consistent;
- every unit has a file;
- drafted units are inside their page budget;
- no placeholder text ships in a drafted unit;
- the page-count gap between the supplied TOC and the stated book length is
  carried explicitly instead of being hidden;
- the foreword is not publishable under a real person's name without sign-off.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1] / "book" / "grok-100k-business"
TOC_PATH = ROOT / "toc.yaml"
BUILD = ROOT / "build_book.py"

COMPLETE = {"draft", "final"}
PLACEHOLDERS = ("TODO", "TBD", "lorem ipsum", "XXX", "[insert", "FIXME")
BANNED = (
    "SHRM",
    "Willowchip",
    "Aethel",
    "144-agent council",
    "quantum chronodynamics",
    "bio-computing",
    "SEANIFOLD",
    "Cognition Fusion",
)


@pytest.fixture(scope="module")
def toc() -> dict:
    return yaml.safe_load(TOC_PATH.read_text(encoding="utf-8"))


def all_units(toc: dict) -> list[dict]:
    units = [{**u, "proposed": False} for u in toc.get("front_matter", [])]
    for part in toc.get("parts", []):
        units += [{**ch, "proposed": False} for ch in part["chapters"]]
    for part in toc.get("proposed", {}).get("parts", []):
        units += [{**ch, "proposed": True} for ch in part["chapters"]]
    units += [{**a, "proposed": True} for a in toc.get("proposed", {}).get("appendices", [])]
    return units


def test_toc_is_wellformed(toc):
    assert toc["slug"] == "grok-100k-business"
    assert toc["words_per_page"] > 0
    assert toc["stated_pages"] == 297
    units = all_units(toc)
    ids = [u["id"] for u in units]
    assert len(ids) == len(set(ids)), "duplicate unit ids"
    for u in units:
        assert u["title"].strip()
        assert u["file"].endswith(".md")
        assert isinstance(u["pages"], int) and u["pages"] > 0
        assert u["status"] in {"draft", "final", "outline", "proposed"}


def test_front_matter_matches_supplied_toc(toc):
    fm = toc["front_matter"]
    assert len(fm) == 7
    assert [u["id"] for u in fm] == [
        "dedication",
        "acknowledgement",
        "foreword",
        "preface",
        "what-this-guide-is",
        "how-to-use",
        "tldr",
    ]


def test_part_chapter_counts(toc):
    counts = {p["number"]: len(p["chapters"]) for p in toc["parts"]}
    assert counts == {1: 6, 2: 6, 3: 6, 4: 6, 5: 5}
    numbers = [ch["number"] for p in toc["parts"] for ch in p["chapters"]]
    assert numbers == list(range(1, 30))


def test_every_unit_has_a_file(toc):
    missing = [u["file"] for u in all_units(toc) if not (ROOT / u["file"]).is_file()]
    assert missing == []


def test_page_gap_is_documented_not_hidden(toc):
    supplied = sum(u["pages"] for u in all_units(toc) if not u["proposed"])
    proposed = sum(u["pages"] for u in all_units(toc) if u["proposed"])
    assert supplied == 216
    gap = toc["stated_pages"] - supplied
    assert gap == 81
    assert proposed == gap, "the proposed block must close the gap exactly"


def test_build_runs_clean(toc):
    proc = subprocess.run(
        [sys.executable, str(BUILD), "--quiet"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads((ROOT / "dist" / "build_report.json").read_text(encoding="utf-8"))
    assert report["missing_files"] == []
    assert report["problems"] == []


def test_drafted_units_are_inside_budget(toc):
    wpp = toc["words_per_page"]
    offenders = []
    for u in all_units(toc):
        if u["status"] not in COMPLETE or u["pages"] < 2:
            continue
        text = (ROOT / u["file"]).read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", " ", text, flags=re.S)
        text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
        words = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", text))
        ratio = (words / wpp) / u["pages"]
        if not 0.60 <= ratio <= 1.50:
            offenders.append((u["id"], round(ratio, 2)))
    assert offenders == []


def test_no_placeholders_in_drafted_units(toc):
    bad = []
    for u in all_units(toc):
        if u["status"] not in COMPLETE:
            continue
        body = (ROOT / u["file"]).read_text(encoding="utf-8")
        for marker in PLACEHOLDERS:
            if marker.lower() in body.lower():
                bad.append((u["id"], marker))
    assert bad == []


def test_no_unsupported_vocabulary(toc):
    hits = []
    for u in all_units(toc):
        body = (ROOT / u["file"]).read_text(encoding="utf-8").lower()
        for term in BANNED:
            if term.lower() in body:
                hits.append((u["id"], term))
    assert hits == []


def test_provenance_is_recorded(toc):
    sources = toc["verified_against"]
    assert any("docs.x.ai" in s for s in sources)
    assert len(sources) >= 4
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", toc["verified_on"])


def test_outline_units_carry_beats(toc):
    thin = []
    for u in all_units(toc):
        if u["status"] != "outline":
            continue
        body = (ROOT / u["file"]).read_text(encoding="utf-8")
        beats = re.findall(r"^\d+\.\s+\S", body, flags=re.M)
        if "## Beats" not in body or len(beats) < 3:
            thin.append(u["id"])
    assert thin == []


def test_foreword_is_not_publishable_without_signoff():
    body = (ROOT / "manuscript" / "00-front-matter" / "02-foreword.md").read_text(
        encoding="utf-8"
    )
    assert "ATTRIBUTION PENDING" in body
