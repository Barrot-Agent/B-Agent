import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "research/xrp_intelligence/20261105T190803Z-xrp-late-session-spot-derivatives-etf-macro-snapshot.json"
CORRECTION = ROOT / "research/xrp_intelligence/20261105T191449Z-xrp-late-session-etf-date-only-timestamp-correction.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_daily_etf_rows_do_not_claim_synthetic_2100_utc_event_times():
    target = load(TARGET)
    correction = load(CORRECTION)
    fields = {item["target_field"]: item for item in correction["field_corrections"]}
    for path in (
        "$.source_registry[5].source_event_time_utc",
        "$.source_registry[6].source_event_time_utc",
        "$.source_registry[7].source_event_time_utc",
    ):
        assert fields[path]["canonical_value"] is None
        assert fields[path]["canonical_date"] in {"2026-11-03", "2026-11-04"}
        assert fields[path]["original_value"].endswith("T21:00:00Z")
    assert target["source_registry"][5]["source_event_time_utc"] == "2026-11-04T21:00:00Z"
    assert target["source_registry"][6]["source_event_time_utc"] == "2026-11-03T21:00:00Z"
    assert all("source_event_time_utc" not in item for item in target["market_snapshot"]["etf_flows"])
    assert correction["preservation"]["target_artifact_modified"] is False


def test_issuer_file_stamps_are_not_mislabeled_as_page_retrieval_time():
    target = load(TARGET)
    correction = load(CORRECTION)
    entry = next(item for item in correction["field_corrections"] if item["target_field"] == "$.source_registry[6].page_checked_at_utc")
    assert target["source_registry"][6]["page_checked_at_utc"] == "2026-11-05T03:04:00Z"
    assert entry["canonical_value"] is None
    assert entry["canonical_value_by_fund"]["XRP"] == "2026-11-05T03:04:00Z"
    assert entry["canonical_value_by_fund"]["XRPZ"]["start"] == "2026-11-04T23:42:00Z"
    assert entry["canonical_value_by_fund"]["XRPC"]["start"] == "2026-11-04T05:17:00Z"
    assert entry["canonical_value_by_fund"]["TOXR"] == "2026-11-05T03:00:00Z"


def test_correction_preserves_flow_values_and_quarantines_all_sources():
    target = load(TARGET)
    correction = load(CORRECTION)
    flows = target["market_snapshot"]["etf_flows"]
    assert flows[0]["daily_flow_2026_11_04_xrp"] == -64826
    assert flows[0]["aggregate_flow_2026_11_02_to_2026_11_04_xrp"] == -259700
    assert flows[1]["daily_flow_2026_11_03_xrp"] == -3339
    assert flows[2]["daily_flow_2026_11_03_xrp"] == 0
    assert all(source["model_eligible"] is False for source in correction["source_registry"])
    assert correction["preservation"]["forecast_issued"] is False
    assert correction["preservation"]["model_eligible"] is False
