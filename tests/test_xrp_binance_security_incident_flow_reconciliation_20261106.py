import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T052215Z-binance-security-incident-xrp-flow-and-withdrawal-recovery.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_fbi_and_binance_incident_attributions_remain_distinct():
    data = load_artifact()
    sources = {item["id"]: item for item in data["source_registry"]}
    assert sources["BINANCE_SECURITY_INCIDENT_INITIAL_20261030"]["independence_group"] == "binance_official"
    assert sources["FBI_TRADERTRAITOR_ADVISORY_20261031"]["independence_group"] == "us_federal_law_enforcement"
    assert "TraderTraitor" in sources["FBI_TRADERTRAITOR_ADVISORY_20261031"]["claims"][0]
    assert any("no evidence" in x.lower() for x in sources["BINANCE_SECURITY_INCIDENT_INITIAL_20261030"]["claims"])


def test_initial_xrp_hot_wallet_transfer_hash_and_scope_are_preserved():
    data = load_artifact()
    source = next(x for x in data["source_registry"] if x["id"] == "WHALE_ALERT_INITIAL_XRP_TRANSFER_20261029")
    assert source["transaction_hash"] == "78E31E7BB06ADABE2322FDD0553533873C1D90664AEDE0C12DE06208F50BFA6A"
    assert source["amount_xrp"] == 185017485
    assert source["sender"] == "rDAE53VfMvftPB4ogpWGWvzkQxfht6JPxr"
    assert source["receiver"] == "rK21t6nGLy4MNDqhvy3pGwcLFy25qgfzMx"
    assert data["xrp_flow_analysis"]["initial_reported_incident_amount_xrp"] == 233460000
    assert data["xrp_flow_analysis"]["individually_observed_initial_transfer_xrp"] < data["xrp_flow_analysis"]["initial_reported_incident_amount_xrp"]


def test_nov2_transfers_keep_hash_and_recipient_limitations():
    data = load_artifact()
    sources = {x["id"]: x for x in data["source_registry"]}
    first = sources["WHALE_ALERT_XRP_TRANSFER_20261102_A"]
    second = sources["WHALE_ALERT_XRP_TRANSFER_20261102_B"]
    assert first["amount_xrp"] == 40000000
    assert second["amount_xrp"] == 40000000
    assert first["event_timestamp_utc"] == "2026-11-02T03:56:21Z"
    assert second["event_timestamp_utc"] == "2026-11-02T03:55:31Z"
    assert second["receiver"] is None
    assert "not accessible" in second["limitations"][0]
    assert data["xrp_flow_analysis"]["nov2_two_transfer_total_xrp"] == 80000000
    assert data["xrp_flow_analysis"]["nov2_transfer_interval_seconds"] == 50


def test_wallet_control_disagreement_is_not_resolved_by_secondary_reporting():
    data = load_artifact()
    sources = {x["id"]: x for x in data["source_registry"]}
    assert sources["CRYPTO_BASIC_BINANCE_XRP_TRANSFER_REPORT_20261102"]["independence_group"] == "secondary_reporting_whale_alert_based"
    assert sources["UTODAY_BINANCE_XRP_WALLET_INTERPRETATION_20261105"]["independence_group"] == "secondary_reporting_whale_alert_and_explorer_labels"
    assert "unknown" in " ".join(sources["CRYPTO_BASIC_BINANCE_XRP_TRANSFER_REPORT_20261102"]["limitations"]).lower()
    assert "conflicts" in " ".join(sources["UTODAY_BINANCE_XRP_WALLET_INTERPRETATION_20261105"]["limitations"]).lower()
    assert data["xrp_flow_analysis"]["recipient_attribution_status"] == "UNRESOLVED"


def test_separate_nov1_binance_withdrawal_is_not_linked_to_hack():
    data = load_artifact()
    assert data["xrp_flow_analysis"]["separate_nov1_binance_labeled_transfer_xrp"] == 50000000
    assert data["xrp_flow_analysis"]["separate_nov1_transfer_linked_to_incident"] is False
    assert "not linked" in data["source_registry"][8]["limitations"][0].lower() or any(
        "not linked" in x.lower()
        for source in data["source_registry"]
        for x in source.get("limitations", [])
    )


def test_binance_replenishment_is_not_mislabeled_as_stolen_asset_recovery():
    data = load_artifact()
    recovery = data["withdrawal_and_reserve_analysis"]
    assert recovery["binance_replenished_affected_assets_percent_as_of_2026_11_04"] == 98
    assert recovery["funds_set_aside_percent_of_required_cover"] == "more_than_100%"
    assert "not the same as recovering" in recovery["limitations"][1]
    assert recovery["xrp_100_percent_backed_statement"].startswith("Binance's November 2")


def test_nov6_xrp_withdrawal_is_network_scoped_not_native_xrpl_confirmation():
    data = load_artifact()
    status = data["withdrawal_and_reserve_analysis"]["nov6_withdrawal_update"]
    assert status["asset"] == "XRP"
    assert status["network_label"] == "ETH"
    assert status["scheduled_start_utc"] == "2026-11-06T04:00:00Z"
    assert status["progressive_rollout"] is True
    assert status["native_xrpl_withdrawal_confirmed"] is False
    assert status["live_status_confirmed"] is False


def test_transfers_are_not_treated_as_exchange_sell_flow_or_forecast():
    data = load_artifact()
    flow = data["xrp_flow_analysis"]
    assert flow["confirmed_exchange_deposit_from_nov2_transfers"] is False
    assert flow["confirmed_sale_or_swap_from_nov2_transfers"] is False
    assert "not sell pressure" in flow["market_impact_boundary"]
    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["issued"] is False


def test_source_capture_limits_and_hypothesis_counterevidence_are_preserved():
    data = load_artifact()
    assert data["capture"]["exact_per_source_retrieval_timestamp_utc"] is None
    assert data["capture"]["raw_http_wire_bytes_captured"] is False
    assert len(data["competing_hypotheses"]) >= 3
    assert all(x["supporting_evidence"] and x["disconfirming_evidence"] for x in data["competing_hypotheses"])
