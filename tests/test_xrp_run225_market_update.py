import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261117T203422Z-run225-market-microstructure-flow-reconciliation.json"

def test_run225_provenance_and_prediction_boundary():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    cutoff = datetime.fromisoformat(data["data_cutoff_utc"].replace("Z", "+00:00"))
    captured = datetime.fromisoformat(data["captured_at_utc"].replace("Z", "+00:00"))
    assert captured >= cutoff
    sources = {item["id"]: item for item in data["source_registry"]}
    assert len(sources) == 19
    for source in sources.values():
        assert source["raw_content_sha256"] is None
        assert source["raw_receipt_id"] is None
        assert source["raw_capture_status"] == "web_rendered_extract_only"
        assert source["model_eligible"] is False
    for item in data["observations"]:
        assert item["evidence"] and set(item["evidence"]) <= set(sources)
        assert item["model_eligible"] is False
    assert data["predictions"]["issued"] is False
    assert data["predictions"]["status"] == "NOT_ISSUED"

def test_run225_keeps_spot_perpetual_oi_and_funding_scopes_separate():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    market = data["market_snapshot"]
    assert market["spot"]["market_type"] == "spot_daily_reference"
    assert market["perp_book"]["market_type"] == "perpetual_futures"
    assert market["open_interest"][0]["open_interest_usd"] != market["open_interest"][1]["open_interest_usd"]
    assert market["funding"][0]["typical_pct_per_8h"] < 0
    assert market["funding"][1]["binance_pct_per_8h"] > 0

def test_run225_preserves_etf_universe_disagreement():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    etf = data["market_snapshot"]["etf_flows"]
    assert etf[0]["partial"] is True and etf[0]["reported"] < etf[0]["expected"]
    assert etf[0]["partial_flow_xrp"] < 0
    assert etf[1]["coverage_complete"] is False and etf[1]["flow_xrp"] > 0

def test_run225_limits_exchange_wallet_and_institutional_claims():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    wallet = data["market_snapshot"]["exchange_wallets"]
    assert wallet["wallets"] == 707 and wallet["exchanges"] == 24
    assert "not tradable float" in wallet["limitation"]
    assert "cbXRP" in wallet["limitation"] and "Binance-Peg XRP" in wallet["limitation"]
    bny = data["market_snapshot"]["bny_custody"]
    assert set(bny["assets"]) == {"XRP", "RLUSD"}
    assert bny["model_eligible"] is False
    escrow = data["market_snapshot"]["escrow"]
    assert escrow["ledger_index"] == 108395459
    assert escrow["re_escrowed_pct_last_12_releases"] == 70
    assert escrow["net_release_estimate_xrp_per_month"] == 300000000
    latest_oi = [x for x in data["market_snapshot"]["open_interest"] if x.get("as_of_utc") == "2026-11-17T20:22:00Z"]
    assert latest_oi and latest_oi[0]["open_interest_usd"] == 956000000
    assert len(data["market_snapshot"]["spot"]["locale_snapshots"]) == 2

def test_run225_nine_platform_map_does_not_overstate_authentication():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    platforms = data["platform_map"]
    assert len(platforms) == 9
    assert next(x for x in platforms if x["platform"] == "ChatGPT")["status"] == "tested_current_runtime"
    assert all(x["status"] != "tested_current_runtime" for x in platforms if x["platform"] != "ChatGPT")
