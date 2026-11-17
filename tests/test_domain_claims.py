"""Eight domains under TRACE-5: every domain must stand on a quoted record."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.re_v2 import validate

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "domains" / "eight_domains.json"
EXPECTED = {
    "Ternary logic",
    "Quantum mechanics",
    "Algorithms",
    "Logarithms",
    "Transformers",
    "Transistors",
    "Photolithography",
    "3D printing",
}


def payload() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def test_offline_validator_passes():
    assert validate(DATA) == []


def test_all_eight_domains_present_and_labelled():
    domains = payload()["domains"]
    assert {d["domain"] for d in domains} == EXPECTED
    for domain in domains:
        assert domain["what_it_is"].startswith("ANALYSIS")
        assert domain["mechanism"].startswith("QUOTED BELOW")
        assert domain["limit"].strip()
        assert domain["transmute"].strip()


def test_every_domain_has_at_least_one_quoted_claim():
    records = payload()["records"]
    for name in EXPECTED:
        grades = [r["status"] for r in records if r["problem"] == name]
        assert "Q" in grades, name


def test_no_rejected_records_and_two_existence_only():
    records = payload()["records"]
    assert all(r["status"] != "X" for r in records)
    existence = [r["id"] for r in records if r["status"] == "E"]
    assert sorted(existence) == ["moore-paper-existence", "setun-existence"]
    for record in records:
        if record["status"] == "E":
            assert record["affirmed"] is False
            assert record["evidence"]["abstract"] == ""


def test_quotes_are_literal_substrings():
    for record in payload()["records"]:
        if record["status"] != "Q":
            continue
        assert record["quotes"], record["id"]
        for quote in record["quotes"]:
            assert quote in record["evidence"]["abstract"], (record["id"], quote[:40])


def test_every_record_states_a_falsifier_and_a_limit():
    for record in payload()["records"]:
        assert record["falsifier"].strip()
        assert record["does_not_show"].strip()


def test_analysis_is_not_quoted():
    for domain in payload()["domains"]:
        assert "ANALYSIS" in domain["what_it_is"]
        assert "QUOTED" in domain["mechanism"]
