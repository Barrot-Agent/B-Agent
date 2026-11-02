import pytest
from barrot_agent.analysis.xrp_telemetry_matrix import EvidenceError, render_report, validate_snapshot, write_report

def not_issued():
    return {"schema_version":"1.0","snapshot_id":"xrp-not-issued","captured_at_utc":"2026-11-02T14:00:00Z","data_cutoff_utc":"2026-11-02T13:59:00Z","sources":[],"market_observations":[],"forecast":{"status":"NOT_ISSUED","reason":"Synchronized post-event observations and validated model evidence are missing."}}

def issued():
    s=not_issued(); s["snapshot_id"]="xrp-issued"
    s["sources"]=[
      {"source_id":"a","publisher":"A","url":"https://a.example","retrieved_at_utc":"2026-11-02T13:58:00Z","independence_group":"a","evidence_class":"market"},
      {"source_id":"b","publisher":"B","url":"https://b.example","retrieved_at_utc":"2026-11-02T13:58:20Z","independence_group":"b","evidence_class":"market"}]
    s["market_observations"]=[
      {"symbol":"XRP/USD","venue":"A","price":1.2,"timestamp_utc":"2026-11-02T13:58:00Z","source_id":"a"},
      {"symbol":"XRP/USD","venue":"B","price":1.19,"timestamp_utc":"2026-11-02T13:58:20Z","source_id":"b"}]
    s["forecast"]={"status":"ISSUED","target":"XRP/USD return over one hour","horizon":"1h","horizon_seconds":3600,"issued_at_utc":"2026-11-02T14:00:01Z","data_cutoff_utc":"2026-11-02T13:59:00Z","probability":0.65,"confidence":0.7,"model_version":"test-v1","assumptions":["Observations are valid."],"alternatives":["Move reverses."],"evaluation":{"walk_forward_samples":30,"out_of_sample":True,"leakage_check":"passed","drift_status":"stable","model_brier_score":0.18,"baseline_brier_score":0.22,"model_log_loss":0.5,"baseline_log_loss":0.62,"calibration_error":0.05,"calibration_tolerance":0.1,"evaluation_artifact_id":"eval-1","evaluation_run_url":"https://github.com/Barrot-Agent/B-Agent/actions/runs/1"},"outcome":{"status":"PENDING"}}
    return s

def test_not_issued_never_emits_hardcoded_price_or_direction():
    report=render_report(not_issued())
    assert "Forecast status: NOT_ISSUED" in report and "No directional forecast" in report
    assert "Market Price" not in report and "BUY" not in report and "SELL" not in report

def test_issued_requires_independent_sources():
    s=issued(); s["sources"][1]["independence_group"]="a"
    with pytest.raises(EvidenceError,match="market observations must be backed"):
        validate_snapshot(s)

def test_issued_requires_synchronized_venues():
    s=issued(); s["market_observations"][0]["timestamp_utc"]="2026-11-02T13:57:00Z"; s["market_observations"][1]["timestamp_utc"]="2026-11-02T13:58:30Z"; s["sources"][1]["retrieved_at_utc"]="2026-11-02T13:58:40Z"
    with pytest.raises(EvidenceError,match="synchronization window"):
        validate_snapshot(s)

def test_issued_requires_baseline_improvement():
    s=issued(); s["forecast"]["evaluation"]["model_brier_score"]=0.25
    with pytest.raises(EvidenceError,match="Brier score must beat"):
        validate_snapshot(s)

def test_issued_requires_outcome_record():
    s=issued(); s["forecast"]["outcome"]={}
    with pytest.raises(EvidenceError,match="outcome must be"):
        validate_snapshot(s)

def test_valid_issued_forecast_is_research_only():
    report=render_report(issued())
    assert "Research-only forecast. Not a trading instruction." in report and "Outcome: PENDING" in report

def test_writer_never_overwrites(tmp_path):
    p=tmp_path/"report.md"; p.write_text("preserve me",encoding="utf-8")
    with pytest.raises(FileExistsError): write_report("new",p)
    assert p.read_text(encoding="utf-8")=="preserve me"

def test_naive_timestamp_rejected():
    s=not_issued(); s["captured_at_utc"]="2026-11-02T14:00:00"
    with pytest.raises(EvidenceError,match="UTC timezone"): validate_snapshot(s)


def test_issued_rejects_sources_retrieved_after_forecast_cutoff():
    s = issued()
    s["sources"][0]["retrieved_at_utc"] = "2026-11-02T14:00:00Z"
    with pytest.raises(EvidenceError, match="retrieval time follows forecast data cutoff"):
        validate_snapshot(s)


def test_issued_requires_observations_to_use_distinct_independent_sources():
    s = issued()
    s["market_observations"][1]["source_id"] = "a"
    s["market_observations"][1]["timestamp_utc"] = "2026-11-02T13:58:00Z"
    with pytest.raises(EvidenceError, match="market observations must be backed"):
        validate_snapshot(s)


def test_issued_rejects_observation_newer_than_its_source_retrieval():
    s = issued()
    s["market_observations"][0]["timestamp_utc"] = "2026-11-02T13:58:10Z"
    with pytest.raises(EvidenceError, match="timestamp follows source retrieval"):
        validate_snapshot(s)


def test_issued_requires_distinct_publishers_and_source_hosts():
    s = issued()
    s["sources"][1]["publisher"] = "A"
    s["sources"][1]["url"] = "https://a.example/second-feed"
    with pytest.raises(EvidenceError, match="market observations must be backed"):
        validate_snapshot(s)


def test_issued_requires_forecast_issue_timestamp_and_numeric_horizon():
    s = issued()
    s["forecast"].pop("issued_at_utc")
    with pytest.raises(EvidenceError, match="forecast.issued_at_utc"):
        validate_snapshot(s)


def test_issued_rejects_forecast_issued_before_snapshot_capture():
    s = issued()
    s["forecast"]["issued_at_utc"] = "2026-11-02T13:59:59Z"
    with pytest.raises(EvidenceError, match="precedes snapshot capture"):
        validate_snapshot(s)


def test_resolved_outcome_cannot_precede_declared_horizon():
    s = issued()
    s["forecast"]["outcome"] = {
        "status": "RESOLVED",
        "resolved_at_utc": "2026-11-02T14:30:00Z",
        "observed_value": 0.01,
        "scoring": {},
    }
    with pytest.raises(EvidenceError, match="precedes the declared forecast horizon"):
        validate_snapshot(s)


def test_resolved_outcome_after_declared_horizon_is_accepted():
    s = issued()
    s["forecast"]["outcome"] = {
        "status": "RESOLVED",
        "resolved_at_utc": "2026-11-02T15:00:01Z",
        "observed_value": 0.01,
        "scoring": {"brier_score": 0.18, "log_loss": 0.5},
    }
    assert validate_snapshot(s)["observations"] == 2


def test_pending_outcome_cannot_carry_resolution_fields():
    s = issued()
    s["forecast"]["outcome"]["observed_value"] = 0.01
    with pytest.raises(EvidenceError, match="pending outcome must not contain resolution fields"):
        validate_snapshot(s)
