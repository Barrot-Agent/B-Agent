import hashlib
import json
import re
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T173833Z-xrp-market-etf-flow-coverage-disagreement.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_direct_market_snapshots_fail_freshness_or_timestamp_gate():
    artifact = load_artifact()
    market = artifact["market_snapshot"]

    assert market["kraken_xrp_usd"]["provider_event_timestamp"] is None
    assert market["kraken_xrp_usd"]["freshness_eligible"] is False
    assert market["okx_xrp_usdt"]["age_at_cutoff_seconds"] > 300
    assert market["okx_xrp_usdt"]["freshness_eligible"] is False
    assert market["binance_xrpusdt_perpetual"]["age_at_cutoff_seconds"] > 300
    assert market["binance_xrpusdt_perpetual"]["freshness_eligible"] is False
    assert market["model_admission"] is False


def test_etf_flow_disagreement_keeps_unlike_universes_separate():
    artifact = load_artifact()
    flows = artifact["etf_flow_reconciliation"]

    assert flows["do_not_average"] is True
    assert flows["aggregate_consensus_flow"] is None
    by_id = {item["source_id"]: item for item in flows["sources"]}

    assert by_id["xrp_insights_issuer_holdings_delta"]["nov6_net_flow_xrp"] == -663043
    assert by_id["cryptoetf_today_five_fund_creation_redemption_series"]["nov6_net_flow_usd"] == 0
    assert by_id["alpha_finance_coinglass_etf_dashboard"]["nov6_net_flow_usd"] == 0
    partial = by_id["cryptokeyhole_issuer_file_partial"]
    assert partial["nov6_partial_net_flow_xrp"] == -752048
    assert partial["nov6_funds_reported"] == 3
    assert partial["nov6_funds_expected"] == 4
    assert flows["model_admission"]["admitted"] is False


def test_canary_primary_share_count_is_disconfirming_not_a_holdings_proof():
    issuer = load_artifact()["etf_flow_reconciliation"]["primary_issuer_disconfirmation"]

    assert issuer["nov4_shares_outstanding"] == 22_990_000
    assert issuer["nov5_shares_outstanding"] == 22_990_000
    assert issuer["nov6_shares_outstanding"] == 22_990_000
    assert issuer["separate_future_holdings_section"]["excluded_as_future_dated"] is True
    assert "does not independently confirm" in issuer["interpretation"]
    assert "does not prove XRP holdings were unchanged" in issuer["interpretation"]


def test_receipts_are_sha256_and_web_excerpts_are_not_mislabeled_raw_bytes():
    artifact = load_artifact()
    for receipt in artifact["source_receipts"]:
        assert re.fullmatch(r"[0-9a-f]{64}", receipt["sha256"])
        if receipt["receipt_kind"] == "normalized_text_excerpt":
            payload = receipt["excerpt"]
        elif receipt["receipt_kind"] == "exact_response_text":
            payload = receipt["raw_response_text"]
        else:
            raise AssertionError(f"Unknown receipt kind: {receipt['receipt_kind']}")
        actual = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        assert actual == receipt["sha256"]


def test_orderbook_depth_is_missing_not_imputed_and_no_forecast_was_issued():
    artifact = load_artifact()
    depth = artifact["market_snapshot"]["order_book_depth"]

    assert depth["multi_level_depth_captured"] is False
    assert depth["model_admission"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["paper_or_real_money_actions"] == "NONE"
