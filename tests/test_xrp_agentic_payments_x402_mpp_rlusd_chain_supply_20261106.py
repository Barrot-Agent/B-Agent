from __future__ import annotations

import json
import math
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T032000Z-xrp-agentic-payments-x402-mpp-rlusd-chain-supply.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_rlusd_chain_supply_is_multi_chain_and_rounded():
    item = load_artifact()["rlusd_chain_supply"]
    assert item["xrpl_supply_usd"] == 871_100_000
    assert item["ethereum_supply_usd"] == 1_730_000_000
    assert item["two_chain_total_usd"] == 2_600_000_000
    assert item["xrpl_share_percent"] == 34
    assert item["ethereum_share_percent"] == 66
    assert item["other_networks_excluded"] == ["Base", "Optimism", "Ink", "Unichain", "XRPL EVM Sidechain"]
    assert "not XRP collateral or XRP demand" in item["interpretation"]


def test_x402_supports_xrp_and_rlusd_with_payer_signed_settlement():
    item = load_artifact()["payment_rail_architecture"]["x402"]
    assert item["supported_assets"] == ["XRP", "XRPL issued assets such as RLUSD"]
    assert "payer signs" in item["payment_flow"].lower()
    assert "facilitator submits" in item["payment_flow"]
    assert item["network_ids"]["mainnet"] == "xrpl:0"
    assert item["network_ids"]["testnet"] == "xrpl:1"
    assert item["network_ids"]["devnet"] == "xrpl:2"


def test_x402_security_controls_cover_replay_network_expiry_and_idempotency():
    item = load_artifact()["payment_rail_architecture"]["x402"]
    joined = " ".join(item["security_controls"]).lower()
    for phrase in ["invoice binding", "networkid", "lastledgersequence", "idempotency", "no partial payments", "no cross-currency"]:
        assert phrase in joined


def test_mpp_single_charges_and_session_payments_are_distinguished():
    item = load_artifact()["payment_rail_architecture"]["machine_payments_protocol"]
    assert set(item["xrpl_single_charge_assets"]) == {"XRP", "IOU", "MPT"}
    assert item["xrpl_payment_channel_session_asset_currently_supported"] == "XRP"
    assert "Pending" in item["stablecoin_session_support"]
    assert "distinct from x402" in item["description"]


def test_t54_dashboard_value_and_transaction_count_are_not_mislabeled_as_capital():
    item = load_artifact()["agent_payment_metrics"]["t54_first_party_dashboard"]
    assert item["all_time_settled_value_usd"] == 63_129.67
    assert item["all_time_transaction_count"] == 15_196_117
    assert item["registered_merchants"] == 188
    assert item["live_services"] == 5_393
    assert math.isclose(item["implied_average_usd_per_transaction"], 63_129.67 / 15_196_117, rel_tol=1e-12)
    assert "rough ratio" in item["interpretation"]
    assert "Unverified" in item["visible_live_list_status"]


def test_payment_dashboard_disagreement_is_preserved_without_averaging():
    item = load_artifact()["agent_payment_metrics"]["cross_source_disagreement"]
    assert item["t54_vs_xrp_radar_transaction_count_difference"] == 74_393
    assert item["t54_value_usd"] == 63_129.67
    assert item["known_component_sum_usd"] == 59_465.04
    assert item["unreconciled_value_difference_usd"] == 3_664.63
    assert "no explanation is assumed" in item["interpretation"]


def test_mastercard_coinbase_ripple_t54_stripe_tempo_and_circle_edges_are_classified():
    data = load_artifact()["institutional_relationship_map"]
    partners = data["mastercard_agent_pay_for_machines"]["initial_participants_and_supporters"]
    for name in ["Coinbase", "Ripple", "RippleX", "t54 Labs", "Stripe", "Tempo"]:
        assert name in partners
    assert "not proof of a direct Coinbase-Ripple" in data["mastercard_agent_pay_for_machines"]["relationship_classification"]
    assert "technical ecosystem overlap only" in data["circle_ows"]["relationship_classification"].lower()


def test_account_reserve_is_not_equated_with_open_market_xrp_demand():
    data = load_artifact()["competing_hypotheses"]
    item = next(x for x in data if x["id"] == "H5_ACCOUNT_RESERVE_IS_NOT_MARKET_PURCHASE")
    assert "1 XRP reserve" in " ".join(item["supporting_evidence"])
    assert "does not prove an open-market XRP purchase" in item["hypothesis"]


def test_no_model_feature_forecast_or_payment_action_is_authorized():
    data = load_artifact()
    assert data["model_eligibility"]["eligible"] is False
    assert data["model_eligibility"]["forecast_issued"] is False
    assert data["source_capture_policy"]["raw_source_bytes_preserved"] is False
    assert "Do not invoke paid x402 services" in data["next_actions"][-1]
