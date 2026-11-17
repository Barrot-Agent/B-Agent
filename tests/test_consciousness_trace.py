"""The consciousness claims file must be internally consistent and offline-valid."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.re_v2 import validate

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "data" / "research" / "consciousness_gr_qm.json"


def payload() -> dict:
    return json.loads(CLAIMS.read_text(encoding="utf-8"))


def test_claims_file_exists_and_validates_offline():
    assert CLAIMS.exists()
    assert validate(CLAIMS) == []


def test_nine_records_and_no_mismatch():
    data = payload()
    assert len(data["records"]) == 9
    assert data["grades"] == {"Q": 8, "E": 1}
    assert "X" not in data["grades"]


def test_every_q_quote_is_a_literal_substring_of_the_stored_abstract():
    for record in payload()["records"]:
        if record["status"] != "Q":
            continue
        assert record["quotes"], f"{record['id']} is Q with no quote"
        for quote in record["quotes"]:
            assert quote in record["evidence"]["abstract"], record["id"]


def test_usable_count_excludes_the_interpretive_preprint():
    data = payload()
    excluded = [r for r in data["records"] if r["excluded_from_evidence"]]
    assert [r["id"] for r in excluded] == ["causal-set-time-assertion"]
    assert data["usable_claims"] == 7
    # The excluded record is still quoted; exclusion is not deletion.
    assert excluded[0]["status"] == "Q"
    assert excluded[0]["quotes"]


def test_only_the_bridge_adjacent_record_is_bridge_adjacent():
    bridge = [r for r in payload()["records"] if r["problem"] == "Consciousness bridge"]
    assert [r["id"] for r in bridge] == ["causal-set-time-assertion"]
    assert bridge[0]["excluded_from_evidence"] is True


def test_every_record_carries_a_falsifier_and_a_limit():
    for record in payload()["records"]:
        assert record["falsifier"], record["id"]
        assert record["does_not_show"], record["id"]


def test_verdict_is_c_and_documents_the_upgrade_condition():
    doc = (ROOT / "docs" / "research" / "CONSCIOUSNESS-BRIDGE.md").read_text(encoding="utf-8")
    assert "**C: Unsupported / contradicted.**" in doc
    assert "This verdict would become A if" in doc
    assert "Why not A" in doc and "Why not B" in doc and "Why not D" in doc


def test_inventory_covers_all_fourteen_terms():
    inventory = json.loads((ROOT / "data" / "research" / "inventory.json").read_text(encoding="utf-8"))
    assert len(inventory["terms"]) == 14
    assert set(inventory["hits"]) == set(inventory["terms"])
    assert inventory["files_scanned"] > 0
