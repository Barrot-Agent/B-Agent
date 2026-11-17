"""RE v2 must refuse to record content it did not quote."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.re_v2 import validate

CLAIMS = Path(__file__).resolve().parents[1] / "data" / "millennium" / "claims" / "p_vs_np.json"
LEDGER = Path(__file__).resolve().parents[1] / "data" / "millennium" / "ledger.json"


def payload() -> dict:
    return json.loads(CLAIMS.read_text(encoding="utf-8"))


def by_id(record_id: str) -> dict:
    return next(r for r in payload()["records"] if r["id"] == record_id)


def test_offline_validator_passes():
    assert validate(CLAIMS) == []


def test_grades_are_counted_and_claims_are_few():
    grades = {}
    for record in payload()["records"]:
        grades[record["status"]] = grades.get(record["status"], 0) + 1
    assert grades == {"Q": 3, "E": 1, "X": 2}


def test_quotes_are_substrings_of_the_stored_source_text():
    for record in payload()["records"]:
        if record["status"] != "Q":
            continue
        assert record["quotes"], record["id"]
        for quote in record["quotes"]:
            assert quote in record["evidence"]["abstract"], (record["id"], quote)


def test_existence_only_record_is_not_affirmed():
    record = by_id("natural-proofs-barrier")
    assert record["status"] == "E"
    assert record["affirmed"] is False


def test_negative_controls_prove_the_title_check_fires():
    arxiv_control = by_id("negative-control-arxiv-id-from-memory")
    doi_control = by_id("negative-control-doi-from-memory")
    assert arxiv_control["status"] == "X"
    assert doi_control["status"] == "X"
    assert arxiv_control["evidence"]["title"] != "Algebrization"
    assert doi_control["evidence"]["title"] != "Algebrization"


def test_both_relativization_directions_are_in_the_stored_abstract():
    abstract = by_id("relativization-barrier")["evidence"]["abstract"]
    assert "\\mathcal{P}^A = \\mathcal{NP}^A" in abstract
    assert "\\mathcal{P}^B \\ne \\mathcal{NP}^B" in abstract


def test_ledger_carries_the_evidence_and_only_quoted_claims_are_usable():
    problems = json.loads(LEDGER.read_text(encoding="utf-8"))["problems"]
    pnp = next(p for p in problems if p["name"] == "P vs NP")
    assert pnp["evidence"]["usable_claims"] == 3
    assert pnp["evidence"]["grades"]["E"] == 1
    assert "only Q" in pnp["evidence"]["rule"]
    assert {p["name"] for p in problems if "evidence" in p} == {"P vs NP", "Hodge Conjecture"}
