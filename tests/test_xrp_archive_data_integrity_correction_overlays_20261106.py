from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "research" / "xrp_intelligence" / "20261106T201855Z-archive-data-integrity-correction-overlays.json"
EVERNORTH = ROOT / "research" / "xrp_intelligence" / "20261104T134706Z-evernorth-close-actual-capital-sbi-ownership-reconciliation.json"
KRAKEN = ROOT / "research" / "xrp_intelligence" / "20261104T113845Z-live-spot-derivatives-etf-reconciliation.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def test_overlay_source_receipts_and_preimage_bindings_are_exact():
    overlay = load(OVERLAY)
    for source in overlay["source_registry"]:
        digest = hashlib.sha256(source["normalized_excerpt"].encode("utf-8")).hexdigest()
        assert digest == source["normalized_excerpt_sha256"]
        assert source["url"].startswith("https://")
        assert source["raw_http_bytes_captured"] is False
    targets = {item["id"]: item["target_artifact"]["git_blob_sha1"] for item in overlay["overlays"]}
    assert targets["evernorth_facility_lender_and_duplicate_relationship_edge_correction"] == git_blob_sha1(EVERNORTH)
    assert targets["kraken_ticker_daily_open_field_semantics_correction"] == git_blob_sha1(KRAKEN)


def test_evernorth_lender_and_relationship_graph_corrections_apply_only_to_derived_view():
    overlay = load(OVERLAY)["overlays"][0]
    original = load(EVERNORTH)
    original_hash = git_blob_sha1(EVERNORTH)
    derived = copy.deepcopy(original)

    lender_op = overlay["corrections"][0]
    debt_row = derived["capital_reconciliation"]["additional_debt_capital"][2]
    assert debt_row["source"] == lender_op["prior_value"]
    debt_row["source"] = lender_op["corrected_value"]
    assert debt_row["source"] == "Ripple Labs Inc."

    graph = derived["ownership_and_relationship_graph"]
    for op in overlay["corrections"][1:]:
        pointer = op["target_json_pointer"].strip("/").split("/")
        index = int(pointer[-1])
        assert graph[index]["from"] == op["expected_entry"]["from"]
        assert graph[index]["to"] == op["expected_entry"]["to"]
        assert graph[index]["relation"] == op["expected_entry"]["relation"]
        assert graph[index]["status"] == op["expected_entry"]["status"]
        graph.pop(index)

    assert len(original["ownership_and_relationship_graph"]) == 14
    assert len(derived["ownership_and_relationship_graph"]) == 12
    assert git_blob_sha1(EVERNORTH) == original_hash
    edges = derived["ownership_and_relationship_graph"]
    assert sum(e["from"] == "Ripple Labs" and e["to"] == "Evernorth Holdings Inc. (Pubco)" and "Facility" in e["relation"] for e in edges) == 1
    assert sum(e["from"] == "Ripple Labs" and e["to"] == "Pathfinder Digital Assets LLC" and e["relation"] == "Company Facility revolving credit" for e in edges) == 1
    assert derived["additional_credit_facilities"][0]["lender"] == "Ripple Labs Inc."


def test_kraken_open_field_is_renamed_to_utc_daily_open_in_derived_view():
    overlay = load(OVERLAY)["overlays"][1]
    original = load(KRAKEN)
    original_hash = git_blob_sha1(KRAKEN)
    derived = copy.deepcopy(original)
    row = derived["market_snapshot"]["spot"][0]

    for op in overlay["corrections"]:
        old_key = op["target_json_pointer"].split("/")[-1]
        assert row[old_key] == op["expected_value"]
        row[op["new_key"]] = row.pop(old_key)

    assert row["daily_open_usd"] == 1.27513
    assert "open_24h_usd" not in row
    assert row["last_vs_daily_open_pct"] == 1.3387
    assert "last_vs_open_pct" not in row
    recomputed = (row["last_usd"] / row["daily_open_usd"] - 1) * 100
    assert math.isclose(recomputed, 1.3386870358316427, rel_tol=0, abs_tol=1e-12)
    assert git_blob_sha1(KRAKEN) == original_hash
