from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]


def test_prediction_contracts_distinguish_calibration_implementation_from_validation():
    feature = (ROOT / "research/xrp_intelligence/feature-store-contract.md").read_text(encoding="utf-8")
    ledger = (ROOT / "research/xrp_intelligence/forecast-ledger-contract.md").read_text(encoding="utf-8")
    mission = json.loads((ROOT / "barrot_agent/data/missions/primary_mission.json").read_text(encoding="utf-8"))

    assert "rolling_temporal_temperature_scaling_v1" in feature
    assert "not yet VERIFIED on a mature live XRP history" in feature
    assert "not a trained predictive model" in feature
    assert "rolling_temporal_temperature_scaling_v1" in ledger
    assert "calibration quality on mature independent XRP outcomes" in ledger
    assert "validated calibration performance" in ledger
    assert "no probability recalibration is performed" not in feature
    assert "fitted probability recalibration" not in ledger

    calibration = next(item for item in mission["workstreams"] if item["topic_id"] == "xrp_calibration_drift_shadow")
    assert "Validate rolling temporal temperature scaling" in calibration["goal"]
