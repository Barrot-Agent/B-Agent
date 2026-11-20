import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research/xrp_intelligence/20261108T021527Z-tga-actual-versus-projection-reconciliation.json"
)


def test_tga_actual_balance_is_separated_from_treasury_projection():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    obs = data["observations"]
    assert obs["latest_closing_balance_usd_millions"] == 922752
    assert obs["change_from_oct27_peak_usd_millions"] == -129778
    assert obs["change_from_oct30_usd_millions"] == -28841
    projection = data["reconciliation_to_treasury_projection"]
    assert projection["projected_tga_peak_usd_billions"] == 1025
    assert "not an observed current balance" in projection["interpretation"]


def test_tga_daily_flows_and_source_provenance_are_preserved():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    obs = data["observations"]
    assert obs["nov5_deposits_usd_millions"] == 300916
    assert obs["nov5_withdrawals_usd_millions"] == 314412
    assert obs["nov5_net_change_usd_millions"] == -13496
    assert data["primary_source"]["classification"] == "official_underlying_source_with_secondary_mirror_retrieval"
    assert len(data["mirror_sources"]) == 2
    assert all("not independent confirmation" in item["independence"] for item in data["mirror_sources"])


def test_tga_counter_evidence_does_not_become_an_xrp_signal():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["scenario_update"][0]["status"] == "DISCONFIRMED_FOR_THE_OBSERVED_OCT27_TO_NOV5_WINDOW"
    assert data["scenario_update"][1]["status"] == "OPEN_FORWARD_HYPOTHESIS"
    assert data["feature_policy"]["feature_store_admission"] is False
    assert data["forecast_status"] == "NOT_ISSUED"
