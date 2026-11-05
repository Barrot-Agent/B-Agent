import json
from pathlib import Path


def test_c2fo_instant_pay_rollout_is_not_misclassified_as_live_xrp_capital():
    root = Path(__file__).resolve().parents[1]
    path = root / "research" / "xrp_intelligence" / "20261105T071229Z-c2fo-instant-pay-rollout-and-capital-status.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))

    assert artifact["model_eligible"] is False
    assert artifact["actual_capital_classification"]["instant_pay_funded_amount_usd"] is None
    assert artifact["actual_capital_classification"]["participating_capital_provider_identities"] == []
    assert artifact["actual_capital_classification"]["historical_early_pay_volume_c2fo_usd"] == ">525000000000"
    assert artifact["actual_capital_classification"]["historical_early_pay_volume_ripple_usd"] == ">520000000000"

    instant_pay = next(item for item in artifact["relationships"] if item["id"] == "c2fo_instant_pay_xrpl_rlusd")
    assert instant_pay["status"] == "ANNOUNCED_WAITLIST_LIMITED_ROLLOUT_PLANNED"
    assert instant_pay["settlement_asset"] == "RLUSD"
    assert instant_pay["xrp_bridge_asset_established"] is False
    assert instant_pay["xrp_collateral_established"] is False
    assert instant_pay["funded_amount_usd"] is None
    assert instant_pay["production_volume"] is None

    product_page = next(item for item in artifact["source_registry"] if item["id"] == "c2fo_instant_pay_product_page_20261105")
    assert "waitlist" in " ".join(product_page["claims_supported"]).lower()
    assert "limited rollout" in " ".join(product_page["claims_supported"]).lower()
    assert product_page["model_eligible"] is False
    c2fo_release = next(item for item in artifact["source_registry"] if item["id"] == "c2fo_ripple_instant_pay_joint_release_20261027")
    assert product_page["independence_group"] == c2fo_release["independence_group"]

    assert artifact["actual_capital_classification"]["rule"].startswith("Do not classify a waitlist")
    assert "5000000000" in artifact["actual_capital_classification"]["discrepancy_usd"]
    assert "not Instant Pay" in artifact["actual_capital_classification"]["historical_early_pay_scope"]
    assert any("methodology" in item for item in artifact["next_actions"])
