import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T052215Z-binance-security-incident-xrp-flow-and-withdrawal-recovery.json"
)


def test_official_withdrawal_update_keeps_eth_network_separate_from_xrpl():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    update = data["withdrawal_and_reserve_analysis"]["nov6_withdrawal_update"]
    assert update["network_label"] == "ETH"
    assert update["asset"] == "XRP"
    assert update["native_xrpl_withdrawal_confirmed"] is False
    assert update["live_status_confirmed"] is False


def test_replenishment_and_recovery_are_distinct_events():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    recovery = data["withdrawal_and_reserve_analysis"]
    assert recovery["binance_replenished_affected_assets_percent_as_of_2026_11_04"] == 98
    assert recovery["remaining_assets_percent"] == "approximately 2%"
    assert "not the same as recovering stolen assets" in recovery["limitations"][1]
    assert data["xrp_flow_analysis"]["confirmed_sale_or_swap_from_nov2_transfers"] is False
