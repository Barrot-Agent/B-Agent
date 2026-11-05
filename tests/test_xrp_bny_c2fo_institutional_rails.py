import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T062720Z-bny-c2fo-ripple-institutional-rails-update.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def edge(data, edge_id):
    return next(item for item in data["relationships"] if item["id"] == edge_id)


def test_bny_xrp_custody_capability_is_reported_live_but_has_no_disclosed_balance():
    data = load()
    custody = edge(data, "bny_digital_asset_custody_xrp_20261027")
    assert custody["status"] == "LIVE_REPORTED_CAPABILITY"
    assert custody["instrument"] == "XRP"
    assert custody["quantified_assets_under_custody"] is None
    assert "XRP assets under custody" in custody["not_established"]
    assert "XRP collateral acceptance or posted balances" in custody["not_established"]


def test_bny_future_rlusd_mint_redeem_and_trade_finance_are_not_live():
    data = load()
    mint = edge(data, "bny_ripple_rlusd_direct_mint_redeem")
    trade_finance = edge(data, "bny_ripple_tokenized_trade_finance_xrpl")
    assert mint["status"] == "FUTURE_SUBJECT_TO_FINAL_BNY_AND_REGULATORY_APPROVALS"
    assert trade_finance["status"] == "EXPLORATORY_SUBJECT_TO_CLIENT_REQUIREMENTS"
    assert "production issuance" in trade_finance["not_established"]


def test_c2fo_instant_pay_is_rlusd_settlement_and_waitlist_not_verified_production_volume():
    data = load()
    instant_pay = edge(data, "c2fo_instant_pay_xrpl_rlusd")
    assert instant_pay["status"] == "ANNOUNCED_WAITLIST_NO_PRODUCTION_VOLUME_VERIFIED"
    assert instant_pay["network"] == "XRPL"
    assert instant_pay["settlement_asset"] == "RLUSD"
    assert instant_pay["amount_funded_usd"] is None
    assert "XRP bridge-asset use" in instant_pay["not_established"]
    assert "XRP collateral" in instant_pay["not_established"]


def test_historical_early_pay_volume_is_not_counted_as_instant_pay_capital():
    data = load()
    capital = data["capital_reconciliation"]
    early_pay = capital["c2fo_existing_early_pay_working_capital_usd"]
    assert early_pay["c2fo_release_lower_bound"] == 525_000_000_000
    assert early_pay["ripple_release_lower_bound"] == 520_000_000_000
    assert early_pay["source_difference_usd"] == 5_000_000_000
    assert early_pay["status"] == "HISTORICAL_EXISTING_EARLY_PAY_PROGRAMS_NOT_C2FO_INSTANT_PAY"
    assert capital["c2fo_instant_pay"]["funded_amount_usd"] is None
    assert capital["c2fo_instant_pay"]["status"] == "ANNOUNCED_WAITLIST_NO_PRODUCTION_FUNDING_RECEIPT"


def test_bny_total_assets_are_not_mislabeled_as_xrp_assets_under_custody():
    data = load()
    capital = data["capital_reconciliation"]
    assert capital["bny_total_assets_under_custody_or_administration_usd"] == 63_400_000_000_000
    assert capital["bny_total_assets_as_of"] == "2026-09-30"
    assert "not XRP assets under custody" in capital["bny_metric_scope"]
    assert edge(data, "bny_digital_asset_custody_xrp_20261027")["quantified_assets_under_custody"] is None


def test_rlusd_distribution_and_custody_do_not_establish_xrp_demand_or_forecast():
    data = load()
    assert data["model_eligible"] is False
    assert data["predictions"]["issued"] is False
    assert data["predictions"]["status"] == "NOT_ISSUED"
    assert data["data_quality"]["raw_source_bytes_captured"] is False
    assert data["data_quality"]["sha256_receipts_verified"] is False
    assert all(source["model_eligible"] is False for source in data["source_registry"])
    assert all(item["disconfirming_or_missing"] for item in data["competing_hypotheses"])


def test_every_relationship_has_resolvable_primary_source_provenance():
    data = load()
    source_ids = {item["id"] for item in data["source_registry"]}
    assert len(source_ids) == len(data["source_registry"])
    for relationship in data["relationships"]:
        assert relationship["source_ids"]
        assert set(relationship["source_ids"]) <= source_ids


def test_ripple_c2fo_reposts_are_not_counted_as_independent_source_groups():
    data = load()
    sources = {item["id"]: item for item in data["source_registry"]}
    ripple = sources["ripple_c2fo_xrpl_instant_pay_20261027"]
    c2fo = sources["c2fo_ripple_xrpl_instant_pay_20261027"]
    assert ripple["independence_group"] == c2fo["independence_group"]
    assert ripple["independence_group"] == "ripple_c2fo_joint_instant_pay_announcement"


def test_bny_primary_rlusd_reserve_custody_is_not_native_xrp_custody():
    data = load()
    reserve = edge(data, "bny_primary_rlusd_reserve_custody")
    xrp_custody = edge(data, "bny_digital_asset_custody_xrp_20261027")
    assert reserve["instrument"] == "RLUSD reserves"
    assert reserve["status"] == "EXISTING_ROLE_REAFFIRMED_BY_BNY_2026_10_27"
    assert xrp_custody["instrument"] == "XRP"
    assert "native XRP custody under the 2025 reserve appointment" in reserve["not_established"]


def test_event_timeline_separates_live_custody_from_future_collateral_and_settlement():
    data = load()
    events = data["event_timeline"]
    classes = {item["classification"] for item in events}
    assert any(
        item["event_date"] == "2026-10-12"
        and item["classification"] == "CUSTODY_LIVE_REPORTED_COLLATERAL_PLANNED"
        for item in events
    )
    assert any(
        item["event_date"] == "2026-10-27"
        and item["classification"] == "ANNOUNCED_WAITLIST_NO_PRODUCTION_VOLUME_VERIFIED"
        for item in events
    )
    assert any(
        item["event_date"] == "2026-10-28"
        and item["classification"] == "DISTRIBUTION_LIVE_REPORTED_COLLATERAL_FUTURE"
        for item in events
    )
    assert "ANNOUNCED_WITHOUT_XRPL_VOLUME" in classes

SHARED_NODE_ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T074200Z-bny-shared-circle-ripple-stablecoin-custody-node.json"


def load_shared_node():
    return json.loads(SHARED_NODE_ARTIFACT.read_text(encoding="utf-8"))


def test_bny_shared_service_provider_links_circle_and_ripple_without_direct_issuer_deal():
    data = load_shared_node()
    relationships = {item["id"]: item for item in data["relationships"]}
    assert relationships["circle_bny_usdc_reserve_custody"]["status"] == "PRIMARY_RESERVE_CUSTODY_REPORTED"
    assert relationships["ripple_bny_rlusd_reserve_custody"]["status"] == "PRIMARY_RESERVE_CUSTODY_ROLE_REPORTED"
    shared = relationships["circle_ripple_shared_bny_service_provider"]
    assert shared["status"] == "INDIRECT_SHARED_SERVICE_PROVIDER_NETWORK_EDGE_ONLY"
    assert shared["direct_circle_ripple_partnership_established"] is False


def test_bny_usdc_mint_burn_capability_is_not_xrpl_or_xrp_bridge_evidence():
    data = load_shared_node()
    edge = next(item for item in data["relationships"] if item["id"] == "bny_circle_usdc_institutional_platform")
    assert edge["status"] == "LIVE_REPORTED_CLIENT_CAPABILITY"
    assert set(edge["capabilities"]) == {"store", "transfer", "mint through Circle instruction", "burn through Circle instruction"}
    assert edge["actual_mint_burn_volume_usd"] is None
    assert "XRPL deployment" in edge["not_established"]
    assert "XRP bridge-asset use" not in edge["not_established"]


def test_bny_native_xrp_and_rlusd_custody_has_no_asset_specific_balance_or_purchase_claim():
    data = load_shared_node()
    edge = next(item for item in data["relationships"] if item["id"] == "bny_digital_asset_custody_xrp_rlusd")
    assert edge["status"] == "LIVE_REPORTED_CUSTODY_CAPABILITY"
    assert edge["xrp_assets_under_custody_units"] is None
    assert edge["rlusd_assets_under_custody_usd"] is None
    assert edge["new_xrp_purchases_established"] is False
    assert edge["xrp_collateral_acceptance_established"] is False


def test_bny_custody_and_c2fo_exploration_are_not_actual_xrp_capital_deployment():
    data = load_shared_node()
    capital = data["actual_capital_classification"]
    assert capital["bny_xrp_purchase_amount_usd"] is None
    assert capital["bny_xrp_purchases_established"] is False
    assert capital["cash_capital_deployed_into_xrp_by_bny"] == "not established"
    c2fo = next(item for item in data["relationships"] if item["id"] == "bny_ripple_c2fo_xrpl_trade_finance")
    assert c2fo["status"] == "EXPLORATORY_SUBJECT_TO_CLIENT_REQUIREMENTS"
    assert c2fo["production_receivables_funded"] is False
    assert c2fo["funded_amount_usd"] is None
    assert c2fo["xrp_bridge_asset_established"] is False


def test_bny_shared_custody_network_artifact_preserves_source_groups_and_blocks_forecast_admission():
    data = load_shared_node()
    source_ids = {item["id"] for item in data["source_registry"]}
    groups = {item["independence_group"] for item in data["source_registry"]}
    assert len(source_ids) == len(data["source_registry"])
    assert data["independence_assessment"]["source_group_count"] == len(data["independence_assessment"]["groups"])
    assert data["independence_assessment"]["source_group_count"] == len(groups)
    assert data["independence_assessment"]["joint_release_copies_are_independent"] is False
    for relationship in data["relationships"]:
        assert relationship["source_ids"]
        assert set(relationship["source_ids"]) <= source_ids
    assert data["model_eligible"] is False
    assert data["source_capture_policy"]["raw_http_bytes_captured"] is False
    assert data["forecast"]["issued"] is False
    assert data["paper_trade_executed"] is False

