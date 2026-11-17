"""The Millennium ledger may not record progress it cannot evidence."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

LEDGER = Path(__file__).resolve().parents[1] / "data" / "millennium" / "ledger.json"
FORBIDDEN = ("proved", "proof complete", "solved by barrot", "breakthrough")


def ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def test_all_seven_problems_present_with_status():
    data = ledger()
    names = [p["name"] for p in data["problems"]]
    assert len(names) == 7, names
    assert "Poincare Conjecture" in names
    statuses = {p["name"]: p["status"] for p in data["problems"]}
    assert statuses["Poincare Conjecture"] == "resolved"
    assert sum(1 for s in statuses.values() if s == "open") == 6


def test_open_problems_carry_a_gap_and_a_transmuted_approach():
    for problem in ledger()["problems"]:
        assert problem["blocking_gap"].strip()
        assert problem["transmuted_approach"].strip()
        assert problem["kpi_gate"].strip()


def test_no_record_claims_an_unverified_result():
    text = LEDGER.read_text(encoding="utf-8").lower()
    for phrase in FORBIDDEN:
        assert phrase not in text, phrase


def test_resolved_is_supported_by_a_fetched_citation():
    sources = json.loads((LEDGER.parent / "poincare_sources.json").read_text(encoding="utf-8"))
    verified = [s for s in sources["preprints"] if s.get("fetched_status") == 200 and s.get("title")]
    assert len(verified) >= 3, verified
    assert sources["verification_event"]["independent_check"] == "Kleiner-Lott and Morgan-Tian, 2006"
