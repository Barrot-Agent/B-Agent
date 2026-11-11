from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T012448Z-xrp-market-depth-and-derivatives-provider-reconciliation.json"

def test_market_depth_snapshot_preserves_venue_coverage_and_not_model_eligible():
    data=json.loads(ARTIFACT.read_text(encoding="utf-8"))
    market=data["market_snapshot"]
    assert market["reference_price_usd"] == 1.1598
    assert market["orderbook_depth_usd"]["within_1pct"] == {"bids":14400000,"asks":9500000,"bid_share_pct":60.3,"venues":6}
    assert market["orderbook_depth_usd"]["within_10pct"]["venues"] == 5
    assert "Binance and Bitget" in market["limitations"][0]
    assert data["feature_policy"]["current_model_eligible"] is False

def test_provider_disagreement_does_not_treat_missing_derivatives_as_zero():
    data=json.loads(ARTIFACT.read_text(encoding="utf-8"))
    cg=data["provider_disagreement"]["coinGlass"]
    assert cg["opened_page_open_interest_usd"] == 0
    assert cg["search_variant_open_interest_usd_range"] == [2740000000,2750000000]
    assert "Treat $0/-- as unavailable" in cg["interpretation"]
    assert data["provider_disagreement"]["coinMarketCap"]["indexed_24h_volume_usd_range"] == [1380000000,1540000000]

def test_future_timestamp_anomaly_and_competing_hypotheses_are_quarantined():
    data=json.loads(ARTIFACT.read_text(encoding="utf-8"))
    swiftedge=data["provider_disagreement"]["swiftedge"]
    assert "later than this 01:24 UTC capture" in swiftedge["timestamp_anomaly"]
    assert len(data["competing_hypotheses"]) == 3
    assert all(item["status"] == "unresolved" for item in data["competing_hypotheses"])
    assert data["classification"] == "research_only_model_ineligible"

def test_source_receipts_are_excerpt_hashes_not_raw_hashes():
    data=json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["provenance_policy"]["raw_http_bytes_captured"] is False
    for source in data["source_receipts"]:
        assert source["raw_bytes_captured"] is False
        digest=source["normalized_excerpt_sha256"]
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)
