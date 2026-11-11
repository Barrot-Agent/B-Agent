import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T175346Z-xrp-insights-nov4-settled-vintage-correction.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_direct_json_metadata_supersedes_stale_search_vintage():
    data = load()
    current = data["corrected_current_vintage"]
    assert current["data_as_of"] == "2026-11-04"
    assert current["generated_at_utc"] == "2026-11-05T17:30:10.730Z"
    assert current["provisional_row_date"] is None
    assert current["net_flow_xrp_nov2_to_nov4"] == -259_701
    assert current["settled_trading_days"] == 3


def test_nov4_holdings_and_aggregate_are_preserved():
    current = load()["corrected_current_vintage"]
    assert current["total_holdings_xrp_nov4"] == 1_196_340_485
    assert current["approx_net_flow_usd"] == -334_000


def test_earlier_nov2_to_nov3_snapshot_is_retained_as_historical_not_current():
    data = load()
    old = data["earlier_stale_snapshot_preserved"]
    assert old["net_flow_xrp_nov2_to_nov3"] == -194_875
    assert old["status"] == "HISTORICAL_RETRIEVAL_VINTAGE_NOT_CURRENT"
    assert data["reconciliation"]["difference_in_displayed_total_holdings_xrp"] == -64_826


def test_crypto_keyhole_vintage_is_not_averaged_with_xrp_insights():
    data = load()
    cross = data["source_registry"][2]
    assert cross["data_as_of"] == "2026-11-03"
    assert cross["funds_covered"] == 4
    assert data["reconciliation"]["source_disagreement"].startswith("CryptoKeyhole remains")


def test_flow_method_and_model_admission_limits_are_explicit():
    data = load()
    method = data["methodology_and_limits"]
    assert "not a direct issuer/AP cash" in method["flow_definition"]
    assert "multi-asset index fund" in method["bitw"]
    assert "held indirectly" in method["xrpr"]
    assert data["source_capture_policy"]["model_eligible"] is False
    assert data["source_capture_policy"]["forecast_issued"] is False
