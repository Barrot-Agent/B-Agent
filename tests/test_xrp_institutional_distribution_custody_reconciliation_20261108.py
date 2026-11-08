import hashlib
import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research/xrp_intelligence/20261108T121411Z-sbi-ripple-coinbase-circle-bny-xrp-distribution-reconciliation.json"
)


def _load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_source_excerpt_receipts_verify():
    data = _load()
    sources = data["sources"]
    assert data["source_count"] == len(sources) == 16
    assert len({item["source_id"] for item in sources}) == len(sources)
    for item in sources:
        assert item["raw_http_bytes_captured"] is False
        assert item["hash_scope"].startswith("SHA-256 of")
        actual = hashlib.sha256(item["excerpt"].encode("utf-8")).hexdigest()
        assert actual == item["excerpt_sha256"], item["source_id"]
        assert item["model_eligible"] is False


def test_rlusd_issuer_is_sctc_not_ripple_national_trust_bank():
    data = _load()
    entities = data["entity_disambiguation"]
    assert entities["rlusd_issuer"].startswith("Standard Custody & Trust Company")
    assert "Separate Ripple-affiliated national trust bank" in entities["ripple_national_trust_bank"]
    assert data["collateral_and_custody_status"]["sctc_remains_rlusd_issuer"] is True
    assert data["collateral_and_custody_status"]["ripple_ntb_final_approval"].startswith(
        "ISSUER_REPORTED_NOT_INDEPENDENTLY_VERIFIED"
    )


def test_collateral_and_custody_capability_is_not_misreported_as_live_usage():
    data = _load()
    status = data["collateral_and_custody_status"]
    assert status["coinbase_global_exchange_rlusd_collateral"].startswith("FUTURE_AT_")
    assert status["standard_chartered_lmax_rlusd_collateral"].startswith("PLANNED")
    assert status["standard_chartered_rlusd_xrpl_custody"] == "LIVE"
    assert "actual client balances undisclosed" in status["bny_xrp_rlusd_custody_platform"]


def test_sbi_promotions_are_not_classified_as_actual_capital():
    data = _load()
    promotions = data["promotional_xrp_channels"]
    assert promotions["sbi_shinsei_deposit_voucher"]["maximum_jpy"] == 20000
    assert promotions["sbi_shinsei_deposit_voucher"]["redemption_volume_disclosed"] is False
    assert promotions["sbi_shareholder_coupon"]["aggregate_redemption_disclosed"] is False
    assert promotions["sbi_visa_crypto_card"]["xrp_conversion_volume_disclosed"] is False
    capital = data["actual_capital_classification"]
    assert capital["issuer_defined_actual_capital_metric_found"] is False
    assert capital["direct_sbi_xrp_open_market_purchase_disclosed"] is False
    assert capital["xrp_vouchers_and_reward_points"].startswith("Retail distribution/marketing")


def test_coinbase_and_circle_financial_metrics_are_not_netted():
    data = _load()
    circle = data["financial_metrics"]["circle_q3_2026"]
    coinbase = data["financial_metrics"]["coinbase_q3_2026"]
    comparison = data["financial_metrics"]["accounting_comparison"]
    assert circle["distribution_costs_to_coinbase_q3_usd_m"] == 331.3
    assert coinbase["stablecoin_revenue_q3_usd_m"] == 306.905
    assert comparison["circle_distribution_costs_and_coinbase_stablecoin_revenue_are_not_same_accounting_measure"] is True
    assert comparison["netting_or_profit_split_inference_permitted"] is False


def test_eba_usdc_significant_emt_effective_date_is_preserved():
    data = _load()
    event = next(item for item in data["event_timeline"] if item["date"] == "2026-11-12")
    assert "dual supervision" in event["event"]
    source = next(item for item in data["sources"] if item["source_id"] == "eba_usdc_significant_emt_20261014")
    assert source["source_type"] == "primary_regulator_press_release"


def test_alpha_finance_etf_flow_is_secondary_and_not_comparable_to_holdings_delta():
    data = _load()
    source = next(item for item in data["sources"] if item["source_id"] == "alpha_finance_xrp_etf_dashboard_20261106")
    assert source["source_type"] == "secondary_market_data_aggregator"
    comparison = next(item for item in data["source_disagreements"] if item["topic"] == "XRP ETF flows versus holdings deltas")
    assert comparison["comparable"] is False
    assert "zero" in comparison["source_a"].lower()
    assert "812,529" in comparison["source_b"]


def test_sbi_and_sbic_entities_remain_distinct():
    entities = _load()["entity_disambiguation"]
    assert "parent of SBI VC Trade" in entities["sbi_holdings"]
    assert "distinct from SBI Holdings" in entities["sbic_east_central_west"]
    assert "no relationship to SBI Holdings or OpenAI" in entities["sbic_chatgpt_phrase"]


def test_model_admission_and_forecast_remain_fail_closed():
    data = _load()
    assert data["model_admission"]["eligible"] is False
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["xrp_impact_assessment"]["direct_xrp_demand_proven"] is False
    assert data["xrp_impact_assessment"]["direct_xrp_purchase_amount_disclosed"] is False
