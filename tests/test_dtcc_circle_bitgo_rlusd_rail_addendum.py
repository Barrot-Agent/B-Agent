import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = "data/xrp_intelligence/snapshots/20261101T162626Z-dtcc-tokenization-circle-bitgo-and-rlusd-chain-mix.json"


def load():
    return json.loads((ROOT / SNAPSHOT).read_text(encoding="utf-8"))


def test_dtcc_launch_networks_are_canton_and_private_besu_not_xrpl():
    snap = load()
    dtcc = snap["dtcc"]
    assert dtcc["launch_networks"] == ["Canton Network", "DTCC private Besu network"]
    assert dtcc["xrp_or_ripple_named_in_oct28_press_release"] is False
    assert "2027" in dtcc["additional_networks"]


def test_circle_and_bitgo_pilot_participation_are_not_overstated():
    snap = load()
    pilot = snap["dtcc_july15_pilot"]
    assert "Circle" in pilot["named_participants"]
    assert "BitGo Bank & Trust" in pilot["named_participants"]
    assert "does not specify" in pilot["circle_role"]
    assert pilot["xrp_or_ripple_named"] is False
    assert snap["dtcc"]["circle_named_in_oct28_collaborator_list"] is False


def test_rlusd_chain_mix_is_not_called_cross_chain_migration():
    snap = load()
    rlusd = snap["rlusd_two_chain_observation"]
    assert round(rlusd["xrpl_change"], 2) == -3854626.13
    assert rlusd["ethereum_change"] == 27446000
    assert rlusd["xrpl_share_start_pct"] == 38.07
    assert rlusd["xrpl_share_end_pct"] == 37.57
    assert "does not prove a bridge transfer" in rlusd["interpretation"]
    assert rlusd["model_feature_admission"].startswith("QUARANTINED")


def test_permissioned_domain_and_europ_pool_activity_are_not_promoted_to_adoption():
    snap = load()
    activity = snap["xrpl_institutional_feature_activity_claims"]
    assert activity["permissioned_domains"]["offer_maker_accounts"] == 1
    assert activity["permissioned_domains"]["qualified_accounts_with_domain_trades"] == 0
    assert activity["europ_xrp_amm"]["xrp_used_as_intermediate_asset"] == 0
    assert "NOT_INDEPENDENTLY_RETRIEVED" in activity["permissioned_domains"]["classification"]


def test_no_xrp_forecast_or_market_feature_is_issued_from_single_source_observations():
    snap = load()
    assert snap["model_controls"]["forecast_status"] == "NOT_ISSUED"
    assert snap["model_controls"]["rlusd_chain_share_feature"] == "QUARANTINED"
    assert snap["model_controls"]["permissioned_domain_activity_feature"] == "QUARANTINED"
