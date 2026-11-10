import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T190139Z-xrp-etf-issuer-holdings-vs-provider-flow-disagreement.json"

def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))

def test_xrp_insights_metadata_is_point_in_time_and_source_defined():
    data = load()["findings"]["xrp_insights"]
    assert data["generated_at_utc"] == "2026-11-08T16:27:58.895Z"
    assert data["data_as_of"] == "2026-11-06"
    assert data["rows"] == 1597
    assert data["nov6_combined_flow_xrp"] == -663043
    assert data["fund_tickers"] == ["XRPC", "XRP", "XRPR", "XRPZ", "GXRP", "TOXR", "BITW"]

def test_xrp_insights_capture_gap_and_bitw_rebalancing_are_preserved():
    data = load()["findings"]["xrp_insights"]
    assert any("GXRP flow is withheld" in item for item in data["limitations"])
    assert any("BITW" in item and "rebalancing" in item for item in data["limitations"])

def test_cryptokeyhole_nov6_is_partial_and_future_timestamp_is_quarantined():
    data = load()["findings"]["cryptokeyhole"]
    assert data["nov6_reporting_count"] == 3
    assert data["nov6_partial_flow_xrp"] == -752048
    assert data["nov6_missing_fund"] == "XRPZ Franklin Templeton"
    assert data["latest_issuer_file_timestamp_status"] == "QUARANTINED_IMPOSSIBLE_FUTURE_DATE"

def test_alpha_finance_zero_is_preserved_as_an_affirmative_provider_result():
    data = load()["findings"]["alpha_finance"]
    assert data["funds_reporting_nov6"] == 5
    assert data["nov6_reported_flow_usd"] == 0
    assert data["upstream_feed"] == "CoinGlass commercial API"

def test_fund_universe_and_flow_definitions_are_not_averaged():
    data = load()["reconciliation"]
    assert "UNRESOLVED" in data["status"]
    assert len(data["why_the_numbers_are_not_comparable"]) >= 4
    assert len(data["competing_hypotheses"]) >= 3
    assert len(data["disconfirming_evidence"]) >= 3

def test_scrapers_are_not_misrepresented_as_independent_issuer_sources():
    data = load()["reconciliation"]["source_independence"]
    assert "overlap" in data["cryptokeyhole"].lower()
    assert "CoinGlass" in data["alpha_finance"]

def test_actual_capital_is_not_inferred_from_holdings_delta():
    data = load()["model_admission"]
    assert data["admitted"] is False
    assert data["prohibited_inference"].startswith("Do not call this actual capital")
    assert data["forecast_status"] == "NOT_ISSUED"

def test_normalized_source_hashes_are_well_formed_and_scoped():
    for source in load()["provenance"]["sources"]:
        digest = source["excerpt_sha256"]
        assert len(digest) == 64
        int(digest, 16)
        assert "normalized" in source["hash_scope"]
    assert load()["provenance"]["retrieval_limits"]
