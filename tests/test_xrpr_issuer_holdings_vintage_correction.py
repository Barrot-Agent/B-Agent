import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105T024651Z-xrpr-nov3-primary-holdings-correction.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_latest_xrpr_issuer_snapshot_separates_direct_and_indirect_exposure():
    data = load()
    latest = data["latest_observation"]
    assert latest["as_of_date"] == "2026-11-03"
    assert latest["direct_xrp"]["quantity"] == 19885382
    assert latest["direct_xrp"]["weight_pct"] == 59.86
    assert latest["indirect_coinshares_xrp_etp"]["shares"] == 362750
    assert latest["indirect_coinshares_xrp_etp"]["weight_pct"] == 40.12
    assert latest["fund_assets_usd"] == 42380000
    assert data["model_eligible"] is False


def test_prior_xrpr_snapshot_is_preserved_as_historical_not_current():
    data = load()
    prior = data["prior_observation_preserved"]
    assert prior["as_of_date"] == "2026-10-01"
    assert prior["direct_xrp_quantity"] == 21260382
    assert data["latest_observation"]["direct_xrp"]["quantity"] != prior["direct_xrp_quantity"]


def test_xrpr_holdings_delta_is_not_mislabeled_as_net_flow():
    data = load()
    comparison = data["comparisons"]
    assert comparison["direct_xrp_quantity_change_between_displayed_snapshots"] == -1375000
    assert comparison["coinshares_etp_share_count_change_between_displayed_snapshots"] == -24000
    assert "not verified creations" in comparison["interpretation"]
    assert "not directly comparable" in comparison["aggregator_comparability"].lower()


def test_xrpr_source_is_not_admitted_as_a_model_feature():
    data = load()
    quality = data["data_quality"]
    assert quality["original_issuer_bytes_hashed"] is False
    assert quality["precise_intraday_timestamp"] is False
    assert quality["daily_creation_redemption_records"] is False
    assert quality["direct_and_indirect_exposure_separated"] is True
    assert quality["model_eligibility"] == "NONE"
    assert data["forecast_issued"] is False
