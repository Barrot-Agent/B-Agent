import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "xrp_intelligence"
SNAPSHOT = BASE / "20261105T143601Z-xrp-spot-depth-derivatives-snapshot.json"
CORRECTION = BASE / "20261105T144600Z-xrp-perpetual-oi-row-sum-correction.json"


def test_perpetual_oi_displayed_rows_reconcile_without_overwriting_snapshot():
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    values = correction["corrected_values"]
    k = values["kodexius"]
    t = values["tradradar"]
    assert sum(k["displayed_exchange_rows_usd"].values()) == k["displayed_exchange_row_sum_open_interest_usd"] == 884_090_000
    assert k["displayed_exchange_row_sum_open_interest_usd"] - k["dashboard_aggregate_open_interest_usd"] == 10_000
    assert sum(t["displayed_exchange_rows_usd"].values()) == t["displayed_exchange_row_sum_open_interest_usd"] == 2_064_720_000
    assert t["displayed_exchange_row_sum_open_interest_usd"] - t["dashboard_rounded_aggregate_open_interest_usd"] == 4_720_000
    cross = values["cross_provider"]
    assert cross["rounded_dashboard_gap_usd"] == 2_060_000_000 - 884_080_000
    assert cross["displayed_row_sum_gap_usd"] == 2_064_720_000 - 884_090_000
    assert cross["aggregation"] == "not_averaged"
    assert correction["supersedes"]["artifact_id"] == snapshot["artifact_id"]
    assert correction["correction_scope"].startswith("Arithmetic only")
    assert correction["source_capture_policy"]["model_eligible"] is False
    assert correction["forecast_status"] == "NOT_ISSUED"
