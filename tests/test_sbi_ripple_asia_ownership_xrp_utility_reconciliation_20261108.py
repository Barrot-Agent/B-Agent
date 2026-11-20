from __future__ import annotations

import hashlib
import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261108T213528Z-sbi-ripple-asia-ownership-xrp-utility-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_official_sbi_source_receipts_are_reproducible() -> None:
    artifact = load_artifact()
    assert len(artifact["source_receipts"]) == 9
    for receipt in artifact["source_receipts"]:
        assert len(receipt["excerpt"].split()) <= 25
        assert hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest() == receipt["sha256"]


def test_sbi_ripple_asia_ownership_is_group_aggregate_not_parent_direct() -> None:
    asia = load_artifact()["entity_relationships"]["sbi_ripple_asia"]
    assert asia["relationship"] == "joint_venture_between_SBI_Holdings_and_Ripple"
    assert asia["sbi_group_voting_rights_pct"] == 60
    assert asia["ownership_scope"].startswith("SBI Group aggregate")
    assert asia["direct_parent_ownership_pct"] is None
    assert asia["remaining_voting_rights_holder_not_identified"] is True


def test_historical_odl_announcements_explicitly_use_xrp_as_bridge_currency() -> None:
    artifact = load_artifact()
    events = artifact["event_timeline"]
    odl = [event for event in events if event["date"] in {"2021-07-28", "2023-09-06"}]
    assert len(odl) == 2
    assert all(event["classification"] == "announced_operational_launch" or event["classification"] == "announced_service_expansion" for event in odl)
    assert "XRP as bridge currency" in odl[0]["event"]
    assert "XRP bridge-currency" in odl[1]["event"]


def test_2026_tokenized_deposit_poc_does_not_imply_xrp_bridge_demand() -> None:
    artifact = load_artifact()
    event = next(e for e in artifact["event_timeline"] if e["date"] == "2026-02-26")
    assert event["classification"] == "conceptual_poc_not_production"
    assert "XRPL contemplated" in event["event"]
    assert artifact["source_independence_and_disagreement"]["xrp_vs_xrpl_caveat"].find("do not establish XRP as a bridge asset") >= 0
    assert artifact["entity_relationships"]["moneytap"]["xrp_use_proven"] is False


def test_dsrv_japan_korea_research_is_not_a_commercial_launch() -> None:
    artifact = load_artifact()
    event = next(e for e in artifact["event_timeline"] if e["date"] == "2026-02-24")
    assert event["classification"] == "research_only"
    assert artifact["entity_relationships"]["dsrv_labs"]["commercial_launch_proven"] is False


def test_rlusd_japan_distribution_is_separate_from_xrp_settlement() -> None:
    artifact = load_artifact()
    event = next(e for e in artifact["event_timeline"] if e["date"] == "2026-06-24")
    assert event["classification"] == "stablecoin_distribution_launch"
    assert "RLUSD" in event["event"]
    assert "not evidence that each RLUSD transfer uses XRP" in artifact["source_independence_and_disagreement"]["stablecoin_caveat"]


def test_visa_reward_option_does_not_prove_open_market_xrp_purchases() -> None:
    artifact = load_artifact()
    event = next(e for e in artifact["event_timeline"] if e["date"] == "2026-05-01")
    assert event["classification"] == "consumer_product_announcement"
    assert artifact["entity_relationships"]["visa_aplus"]["xrp_purchase_volume_disclosed"] is False
    assert "does not prove equivalent open-market XRP purchases" in artifact["counterhypotheses"][3]
    assert "no cardholder selection share" in artifact["source_independence_and_disagreement"]["consumer_card_caveat"]


def test_related_party_announcements_are_not_independent_volume_confirmation() -> None:
    artifact = load_artifact()
    caveat = artifact["source_independence_and_disagreement"]["independence_limit"]
    assert "not independent verification" in caveat
    assert artifact["model_admission"]["admitted_to_feature_store"] is False
    assert artifact["model_admission"]["price_directional_use"] is False


def test_no_forecast_or_external_financial_action() -> None:
    artifact = load_artifact()
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["directional_forecast"] is False
    assert artifact["external_actions"]["financial_action"] is False
    assert artifact["external_actions"]["external_model_transfer"] is False
