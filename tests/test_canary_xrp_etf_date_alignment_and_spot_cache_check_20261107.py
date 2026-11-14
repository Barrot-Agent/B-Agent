import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T131719Z-canary-xrp-etf-date-alignment-and-spot-cache-check.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_canary_nov6_net_assets_are_separate_from_future_holdings_table():
    data = load_artifact()["issuer_date_alignment"]["canary_xrpc"]
    assert data["nov6_net_assets_usd"] == 286858926.41
    assert data["nov6_shares_outstanding"] == 22990000
    assert data["accessible_holdings_section_as_of"] == "2026-11-09"
    assert data["nov6_xrp_holdings_quantity"] is None


def test_hold_hub_canary_net_assets_match_nov5_not_nov6():
    data = load_artifact()["issuer_date_alignment"]
    canary = data["canary_xrpc"]
    secondary = data["hold_hub_secondary_table"]
    assert secondary["reported_canary_net_assets_usd"] == canary["historical_daily_rows"]["2026-11-05"]
    assert secondary["reported_canary_net_assets_usd"] != canary["historical_daily_rows"]["2026-11-06"]
    assert secondary["xrp_quantity_status"] == "SECONDARY_ONLY_NOT_VALIDATED_AGAINST_PRIMARY_NOV6_HOLDINGS"


def test_canary_secondary_xrp_quantity_is_not_in_primary_subtotal():
    data = load_artifact()["aggregation_rules"]
    assert data["excluded_secondary_canary_quantity"] == 243714802
    assert data["primary_verified_xrp_subtotal"] == 790633753.6793
    assert data["subtotal_status"] == "INCOMPLETE_NON_SYNCHRONIZED_NOT_TOTAL"


def test_bitwise_market_value_and_net_assets_remain_distinct_fields():
    data = load_artifact()["issuer_date_alignment"]["bitwise_field_alignment"]
    assert data["xrp_market_value_usd"] == 488726918.14
    assert data["net_assets_aum_usd"] == 488684299
    assert data["xrp_market_value_usd"] != data["net_assets_aum_usd"]


def test_franklin_and_grayscale_values_keep_issuer_cutoffs():
    data = load_artifact()["issuer_date_alignment"]
    assert data["franklin_xrpz"]["as_of_date"] == "2026-11-04"
    assert data["grayscale_gxrp"]["as_of_date"] == "2026-11-06"
    assert data["franklin_xrpz"]["xrp_in_fund"] == 310430333.34
    assert data["grayscale_gxrp"]["xrp_in_fund"] == 64838291.2993


def test_identical_market_recheck_is_not_treated_as_new_observation():
    data = load_artifact()["market_retrieval_recheck"]
    assert data["kraken_payload_sha256"] == data["recheck_payload_sha256"]
    assert data["result"].startswith("Both public ticker URLs returned byte-identical")
    assert "Do not treat the recheck as a fresh independent market observation" in data["treatment"]


def test_flow_and_forecast_remain_fail_closed():
    data = load_artifact()
    assert data["aggregation_rules"]["daily_flow"] == "NOT_VERIFIED_FROM_ISSUER_PAGES"
    assert data["model_admission"]["admitted_to_price_or_flow_features"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
