import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261117T120307Z-run213-xrp-market-and-entity-reconciliation.json"


def test_sbic_east_central_west_are_distinct_statutory_companies_not_sbi_holdings():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    law = data["law_and_entities"]["sbic_law"]
    entities = data["law_and_entities"]["entities"]
    assert law["law_id"] == "338AC0000000101"
    assert law["articles"]["2"].startswith("enumerates Tokyo, Nagoya and Osaka")
    assert entities["sbic_east"]["designation"] == "SBIC East Japan"
    assert entities["sbic_central"]["designation"] == "SBIC Central Japan"
    assert entities["sbic_west"]["designation"] == "SBIC West Japan"
    assert len({entities[key]["legal_name_ja"] for key in ("sbic_east", "sbic_central", "sbic_west")}) == 3
    assert entities["sbi_holdings"]["legal_name"] == "SBI Holdings, Inc."
    assert "no sbi holdings ownership or group affiliation" in data["law_and_entities"]["relationship_conclusion"].lower()


def test_institutional_relationship_edges_are_dated_and_nonexclusive():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    edges = data["institutional_relationships"]
    assert any(edge["from"] == "Circle" and edge["to"] == "SBI Holdings" for edge in edges)
    assert any(edge["from"] == "Ripple" and edge["to"] == "SBI Holdings and SBI VC Trade" for edge in edges)
    assert any(edge["from"] == "Ripple" and edge["to"] == "Coinbase" for edge in edges)
    assert any(edge["from"] == "Circle" and edge["to"] == "XRPL" for edge in edges)
    assert not any("SBIC" in edge["from"] or "SBIC" in edge["to"] for edge in edges)


def test_market_observations_preserve_vendor_cutoffs_and_do_not_create_forecasts():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    observations = data["market_observations"]
    assert len(observations) >= 8
    assert all(item["model_eligible"] is False for item in observations)
    assert all(item["raw_source_sha256"] is None for item in observations)
    assert all(item["receipt_status"] == "not_captured_from_raw_http" for item in observations)
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["model_admission"]["eligible_observations"] == 0
    assert "Do not average" in data["market_interpretation"]["leverage"]
    assert "not directly comparable" in data["market_interpretation"]["etf_flows"]
