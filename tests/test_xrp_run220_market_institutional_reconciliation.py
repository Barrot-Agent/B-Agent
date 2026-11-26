import json
from pathlib import Path

from barrot_agent.evolution.event_timeline import build_event_timeline


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = ROOT / "research" / "xrp_intelligence" / "20261117T162924Z-run220-market-institutional-reconciliation.json"
REGISTRY_PATH = ROOT / "research" / "xrp_intelligence" / "event_registry_current.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_run220_reconciliation_is_research_only_and_source_provenanced():
    artifact = _load(ARTIFACT_PATH)
    assert artifact["artifact_type"] == "barrot.xrp.market_institutional_reconciliation"
    assert artifact["run_id"] == "run220"
    assert artifact["mission"]["priority"] == 1
    assert artifact["mission"]["foundation"].startswith("Barrot V3")
    assert artifact["predictions"]["issued"] is False
    assert artifact["predictions"]["forecast_status"] == "NOT_ISSUED"
    assert artifact["predictions"]["directional_forecast_allowed"] is False

    sources = artifact["source_registry"]
    source_ids = {source["source_id"] for source in sources}
    assert len(source_ids) == len(sources)
    assert len(sources) == 17
    assert all(source["raw_content_sha256"] is None for source in sources)
    assert all(source["model_eligible"] is False for source in sources)

    for observation in artifact["observations"]:
        assert set(observation["source_ids"]).issubset(source_ids)

    assert len(artifact["platform_map"]) == 9
    assert artifact["platform_map"]["ChatGPT"]["status"] == "verified_read_access"
    assert artifact["platform_map"]["Grok"]["status"] == "not_tested"
    assert artifact["platform_map"]["Claude"]["status"] == "not_tested"
    assert artifact["identity_research"]["kamilah_stevenson"]["video_inventory_status"] == "NOT_INVENTORIED"


def test_run220_market_providers_remain_separate_and_quality_gated():
    artifact = _load(ARTIFACT_PATH)
    market = artifact["market_snapshot"]
    assert market["derivatives"]["aggregation_policy"] == "DO_NOT_AVERAGE_PROVIDER_TOTALS"
    assert market["etf_flows"]["aggregation_policy"] == "DO_NOT_AVERAGE_DIFFERENT_FUND_UNIVERSES"
    assert market["derivatives"]["optimistfi"]["status"] == "QUARANTINED"
    assert market["etf_flows"]["cryptokeyhole"]["status"] == "PARTIAL_NOT_TOTAL"
    assert market["etf_flows"]["xrp_insights"]["quality_status"] == "QUARANTINE_AGGREGATE_AUM; FLOW_PROVISIONAL"
    assert market["order_book"]["fuelmaps"]["snapshot_age_seconds"] > 65 * 60
    assert artifact["data_quality"]["byte_exact_raw_receipts"] == 0
    assert artifact["data_quality"]["model_eligible_events"] == 0


def test_current_event_registry_builds_a_cutoff_safe_research_timeline():
    registry = _load(REGISTRY_PATH)
    assert registry["registry_version"] == "run224-20261126-ripple-holdings-primary-capture"
    assert registry["event_count"] == len(registry["events"]) == 152
    coverage = registry["publisher_timestamp_coverage"]
    assert coverage["exact_publisher_timestamps"] == 59
    assert coverage["missing_exact_publisher_timestamps"] == 93
    assert coverage["exact_publisher_timestamps"] + coverage["missing_exact_publisher_timestamps"] == registry["event_count"]

    assert registry["run220_update"]["appended_event_count"] == 15
    assert registry["run221_update"]["appended_event_count"] == 0
    assert len(registry["run221_update"]["refreshed_event_ids"]) == 2
    update = registry["run222_update"]
    assert update["prior_event_count"] == 140
    assert update["appended_event_count"] == 10
    assert registry["run223_update"]["resulting_event_count"] == 151
    assert update["raw_source_sha256_receipts_added"] == 0
    added_ids = set(update["added_event_ids"])
    assert len(added_ids) == 10
    added = [event for event in registry["events"] if event["event_id"] in added_ids]
    assert len(added) == 10
    assert all(event["raw_source_sha256"] is None for event in added)
    assert all(event["model_eligible"] is False for event in added)
    run223 = registry["run223_update"]
    assert run223["prior_event_count"] == 150
    assert run223["appended_event_count"] == 1
    assert run223["resulting_event_count"] == 151
    assert run223["added_event_ids"] == ["ripple-coinbase-rlusd-partnership-2026-10-28"]
    assert run223["raw_source_sha256_receipts_added"] == 0
    ripple_coinbase = next(
        event for event in registry["events"]
        if event["event_id"] == "ripple-coinbase-rlusd-partnership-2026-10-28"
    )
    assert ripple_coinbase["raw_source_sha256"] is None
    assert ripple_coinbase["model_eligible"] is False
    assert ripple_coinbase["feature_admission_status"] == "EXCLUDED_NO_BYTE_EXACT_RECEIPT"

    run224 = registry["run224_update"]
    assert run224["prior_event_count"] == 151
    assert run224["appended_event_count"] == 1
    assert run224["resulting_event_count"] == registry["event_count"] == 152
    assert run224["added_event_ids"] == ["ripple-xrp-holdings-2026-09-30"]
    assert run224["raw_source_sha256_receipts_added"] == 0
    assert run224["missing_exact_publisher_timestamp_count"] == 93
    assert run224["model_eligible"] is False
    assert run224["forecast_status"] == "NOT_ISSUED"
    ripple_holdings = next(
        event for event in registry["events"]
        if event["event_id"] == "ripple-xrp-holdings-2026-09-30"
    )
    assert ripple_holdings["source_url"] == "https://ripple.com/xrp/"
    assert ripple_holdings["source_published_at_utc"] is None
    assert ripple_holdings["raw_source_sha256"] is None
    assert registry["model_eligible"] is False
    assert "36,809,481,946 XRP" in ripple_holdings["claim"]
    assert "31,700,000,000 XRP in escrow" in ripple_holdings["claim"]
    assert "do not by themselves measure net market selling" in ripple_holdings["hypothesis"]
    assert "re-escrow" in ripple_holdings["counter_hypothesis"]
    assert all(event["feature_admission_status"] == "EXCLUDED_NO_BYTE_EXACT_RECEIPT" for event in added)

    kamilah = next(event for event in registry["events"] if event["event_id"] == "kamilah-stevenson-youtube-identity-unresolved-20260611")
    assert kamilah["identity_verified"] is False
    assert kamilah["video_inventory_status"] == "NOT_INVENTORIED"
    assert len(kamilah["candidate_channel_ids"]) == 2

    timeline = build_event_timeline(
        asset="XRP",
        data_cutoff_utc=registry["captured_at_utc"],
        horizon_seconds=365 * 24 * 60 * 60,
        event_records=registry["events"],
    )
    assert timeline["event_count"] + len(timeline["excluded_events"]) == len(registry["events"])
    assert timeline["raw_hash_present_count"] == 0
    assert timeline["receipt_complete"] is False
    assert timeline["forecast_status"] == "NOT_ISSUED"
    assert timeline["directional_forecast"] is False
    assert timeline["model_eligible"] is False
    assert timeline["scenario_set"]["forecast_status"] == "NOT_ISSUED"
    assert timeline["scenario_set"]["directional_forecast"] is False
