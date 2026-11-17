"""TRACE-5 applied to Hodge: quotes verified, one assertion excluded."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.re_v2 import validate

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "data" / "millennium" / "claims" / "hodge_conjecture.json"
LEDGER = ROOT / "data" / "millennium" / "ledger.json"


def payload() -> dict:
    return json.loads(CLAIMS.read_text(encoding="utf-8"))


def by_id(record_id: str) -> dict:
    return next(r for r in payload()["records"] if r["id"] == record_id)


def test_offline_validator_passes():
    assert validate(CLAIMS) == []


def test_grades_and_usable_count_differ():
    records = payload()["records"]
    grades = {}
    for record in records:
        grades[record["status"]] = grades.get(record["status"], 0) + 1
    assert grades == {"Q": 4, "E": 1}
    usable = [r for r in records if r["status"] == "Q" and not r["excluded_from_evidence"]]
    assert len(usable) == 3


def test_every_q_quote_is_in_the_stored_source_text():
    for record in payload()["records"]:
        if record["status"] != "Q":
            continue
        assert record["quotes"]
        for quote in record["quotes"]:
            assert quote in record["evidence"]["abstract"], (record["id"], quote)


def test_paywalled_record_is_existence_only_and_not_affirmed():
    record = by_id("integral-hodge-atiyah-hirzebruch")
    assert record["status"] == "E"
    assert record["affirmed"] is False
    assert record["evidence"]["abstract"] == ""


def test_unrefereed_assertion_is_quoted_but_excluded():
    record = by_id("hypersurface-assertion")
    assert record["status"] == "Q"
    assert record["excluded_from_evidence"] is True
    assert "unrefereed" in record["exclusion_reason"]
    assert "whether the argument is correct" in record["does_not_show"]


def test_no_memory_narrated_row_is_unlabelled():
    for record in payload()["records"]:
        assert record["single_source"] is True
        assert record["falsifier"].strip()
        assert record["does_not_show"].strip()


def test_ledger_shows_both_evidence_blocks_and_hodge_counts():
    problems = json.loads(LEDGER.read_text(encoding="utf-8"))["problems"]
    with_evidence = {p["name"] for p in problems if "evidence" in p}
    assert with_evidence == {"P vs NP", "Hodge Conjecture"}
    hodge = next(p for p in problems if p["name"] == "Hodge Conjecture")
    assert hodge["evidence"]["usable_claims"] == 3
    assert hodge["evidence"]["excluded_claims"] == 1
    assert hodge["evidence"]["unsourced_fields"] == ["blocking_gap", "transmuted_approach"]
