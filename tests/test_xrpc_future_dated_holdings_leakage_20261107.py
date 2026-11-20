import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T175608Z-xrpc-future-dated-holdings-leakage-reconciliation.json"
)
CORRECTION = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T180029Z-xrpc-xrp-insights-method-excerpt-hash-correction.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_aggregator_nov6_xrpc_holdings_match_canary_future_nov9_row():
    artifact = load_artifact()
    issuer = artifact["primary_issuer_evidence"]
    reconciliation = artifact["reconciliation"]
    future = issuer["separate_holdings_section"]

    assert future["as_of_date"] == "2026-11-09"
    assert future["future_dated_relative_to_cutoff"] is True
    assert future["xrpc_holdings_xrp"] == 242_962_753.64
    assert reconciliation["cryptokeyhole_nov6_xrpc_holdings_xrp"] == 242_962_754
    assert reconciliation["xrp_insights_nov6_xrpc_holdings_xrp"] == 242_962_754
    assert reconciliation["absolute_difference_cryptoKeyhole_xrp"] <= 0.36
    assert reconciliation["absolute_difference_xrpInsights_xrp"] <= 0.36
    assert artifact["model_admission"]["admitted"] is False


def test_canary_share_count_history_separates_nov6_from_future_row():
    issuer = load_artifact()["primary_issuer_evidence"]
    history = issuer["historical_table"]
    future = issuer["separate_holdings_section"]

    assert history["nov4_shares_outstanding"] == 22_990_000
    assert history["nov5_shares_outstanding"] == 22_990_000
    assert history["nov6_shares_outstanding"] == 22_990_000
    assert future["shares_outstanding"] == 22_920_000
    assert issuer["nov6_to_nov9_share_count_difference"] == 70_000


def test_cryptokeyhole_partial_nov6_outflow_is_rejected_as_point_in_time_evidence():
    artifact = load_artifact()
    keyhole = artifact["aggregator_observations"]["cryptokeyhole"]

    assert keyhole["nov6_partial_net_flow_xrp"] == -752_048
    assert keyhole["nov6_coverage"] == "3 of 4 daily-readable funds reported; Franklin pending"
    assert keyhole["latest_issuer_file_date"] == "2026-11-09"
    assert keyhole["admission_status"] == "REJECTED_FOR_2026-11-06_POINT_IN_TIME_FEATURE"


def test_xrp_insights_aggregate_is_quarantined_not_mechanically_corrected():
    artifact = load_artifact()
    insights = artifact["aggregator_observations"]["xrp_insights"]
    sensitivity = artifact["reconciliation"]["xrp_insights_aggregate_sensitivity"]

    assert insights["reported_nov6_total_holdings_delta_xrp"] == -663_043
    assert insights["xrpc_reported_nov6_holdings_xrp"] == 242_962_754
    assert insights["admission_status"] == "QUARANTINED_FOR_2026-11-06_POINT_IN_TIME_FEATURE"
    assert sensitivity["illustrative_adjusted_aggregate_xrp"] == 85_666
    assert sensitivity["status"] == "sensitivity_only_not_a_corrected_flow"


def test_secondary_search_snippets_are_not_promoted_over_stale_open_pages():
    artifact = load_artifact()
    corp = artifact["secondary_retrieval_vintages"]["corpstacking"]
    maketo = artifact["secondary_retrieval_vintages"]["maketo"]

    assert corp["search_result_snippet_only"]["status"] == "unverified_secondary_search_snippet"
    assert corp["opened_page_snapshot"]["page_data_as_of"] == "2026-11-04"
    assert maketo["search_result_snippet_only"]["status"] == "unverified_secondary_search_snippet"
    assert maketo["opened_page_snapshot"]["page_data_as_of"] == "2026-10-28"


def test_every_normalized_source_receipt_matches_its_exact_excerpt_hash_or_explicit_correction():
    artifact = load_artifact()
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    corrected_source_id = correction["supersedes_source_id"]

    assert correction["supersedes_artifact_path"] == str(ARTIFACT.relative_to(ROOT))
    assert correction["supersedes_artifact_id"] == artifact["artifact_id"]
    assert correction["supersedes_artifact_git_blob_sha1"] == "0a785d9f2716602336aeae08f700b53e93b09825"

    corrected_receipts = [
        receipt for receipt in artifact["source_receipts"]
        if receipt["source_id"] == corrected_source_id
    ]
    assert len(corrected_receipts) == 1
    corrected_receipt = corrected_receipts[0]
    actual_corrected_digest = hashlib.sha256(
        corrected_receipt["excerpt"].encode("utf-8")
    ).hexdigest()

    assert correction["incorrect_prior_sha256"] == corrected_receipt["sha256"]
    assert correction["normalized_excerpt"] == corrected_receipt["excerpt"]
    assert correction["corrected_sha256"] == actual_corrected_digest

    for receipt in artifact["source_receipts"]:
        assert receipt["receipt_kind"] == "normalized_text_excerpt"
        assert re.fullmatch(r"[0-9a-f]{64}", receipt["sha256"])
        actual = hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest()
        if receipt["source_id"] == corrected_source_id:
            assert receipt["sha256"] == correction["incorrect_prior_sha256"]
            assert actual == correction["corrected_sha256"]
        else:
            assert actual == receipt["sha256"], receipt["source_id"]


def test_future_row_guard_and_forecast_issuance_remain_fail_closed():
    artifact = load_artifact()
    guard = artifact["point_in_time_ingestion_guard"]

    assert guard["rule_id"] == "issuer_row_effective_date_must_not_be_backdated"
    assert any("underlying issuer row" in item for item in guard["requirements"])
    assert artifact["model_admission"]["admitted"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["paper_or_real_money_actions"] == "NONE"


def test_hash_correction_is_append_only_and_does_not_make_data_model_eligible():
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    artifact = load_artifact()

    assert correction["correction_type"] == "append_only_source_excerpt_hash_correction"
    assert correction["field_corrected"] == "normalized_excerpt_sha256"
    assert correction["model_eligibility"]["eligible"] is False
    assert correction["forecast"]["status"] == "NOT_ISSUED"
    assert correction["safety"]["paper_trade_executed"] is False
    assert correction["safety"]["real_money_action"] is False
    assert artifact["model_admission"]["admitted"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"
