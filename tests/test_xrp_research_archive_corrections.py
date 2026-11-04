"""Regression tests for append-only XRP archive review corrections."""
from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = ROOT / "research" / "xrp_intelligence" / "20261104T144241Z-archive-review-corrections-and-point-in-time-quarantine.json"


def load_artifact():
    return json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))


def correction(artifact, correction_id):
    return next(item for item in artifact["correction_overlay"]["entries"] if item["correction_id"] == correction_id)


def source_map(artifact):
    return {item["id"]: item for item in artifact["source_registry"]}


def parse_utc(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_correction_artifact_is_append_only_and_research_only():
    data = load_artifact()
    assert data["preservation"]["original_artifacts_modified"] is False
    assert data["preservation"]["original_raw_source_receipts_modified"] is False
    assert data["correction_overlay"]["consumer_application_status"] == "NOT_EXECUTED_RESEARCH_ONLY_OVERLAY"
    assert data["forecast_issued"] is False
    assert data["prediction_status"] == "NOT_ISSUED"
    assert data["model_eligible"] is False


def test_all_source_ids_are_unique_and_resolve():
    data = load_artifact()
    ids = [item["id"] for item in data["source_registry"]]
    assert len(ids) == len(set(ids))
    assert len(ids) >= 20
    known = set(ids)
    for entry in data["correction_overlay"]["entries"]:
        for source_id in entry.get("evidence_source_ids", []):
            assert source_id in known
        if entry.get("source_id"):
            assert entry["source_id"] in known


def test_rendered_sources_are_not_misrepresented_as_raw_receipts():
    data = load_artifact()
    for source in data["source_registry"]:
        assert source["model_eligible"] is False
        assert source["raw_content_sha256"] is None
        assert source["raw_capture_status"] in {"web_rendered_extract_only", "web_search_extract_only", "title_metadata_and_primary_page"}


def test_new_source_retrieval_times_do_not_exceed_addendum_cutoff():
    data = load_artifact()
    cutoff = parse_utc(data["captured_at_utc"])
    for source in data["source_registry"]:
        assert parse_utc(source["retrieved_at_utc"]) <= cutoff


def test_late_sources_are_rehomed_without_rewriting_original_capture():
    data = load_artifact()
    entry = correction(data, "C08_LATE_SOURCE_REHOMING")
    original_capture = parse_utc(entry["original_captured_at_utc"])
    revised = parse_utc(entry["original_revised_at_utc"])
    assert revised > original_capture
    assert entry["original_artifact_modified"] is False
    assert entry["canonical_treatment"].startswith("QUARANTINE_ORIGINAL_ARTIFACT")
    ids = {source["id"]: source for source in data["source_registry"]}
    for source_id in entry["late_source_ids"]:
        assert source_id in ids
        assert parse_utc(ids[source_id]["retrieved_at_utc"]) == revised
        assert ids[source_id]["model_eligible"] is False
        assert parse_utc(ids[source_id]["retrieved_at_utc"]) > original_capture


def test_circle_q2_sec_accession_and_occ_records_are_distinct():
    data = load_artifact()
    entry = correction(data, "C01_SOURCE_CITATION_CROSSWALK")
    replacements = entry["replacements"]
    circle = next(x for x in replacements if x["source_id"] == "circle_q2_2026_10q_correct")
    ripple = next(x for x in replacements if x["source_id"] == "ripple_occ_cas_correct")
    coinbase = next(x for x in replacements if x["source_id"] == "coinbase_occ_cas_correct")
    assert "000187604226000248" in circle["canonical_url"]
    assert "000187604226000045" in circle["old_url"]
    assert "RjzoD2gxmYOv" in ripple["canonical_url"]
    assert "3RAoRRek6o4j" in coinbase["canonical_url"]
    assert ripple["canonical_url"] != coinbase["canonical_url"]


def test_dangling_handoff_is_not_referenced_as_existing():
    data = load_artifact()
    entry = correction(data, "C02_DANGLING_HANDOFF_REFERENCE")
    assert entry["invalid_reference"].endswith("HANDOFF_20261103T223519Z-PROVENANCE-CLOCK-AUDIT.md")
    assert all(ref.endswith("20261103T223519Z-research-artifact-clock-audit.json") or ref.startswith("https://github.com/") for ref in entry["canonical_references"])


def test_kraken_open_is_daily_not_rolling_24h():
    data = load_artifact()
    entry = correction(data, "C03_KRAKEN_UTC_DAILY_OPEN")
    fields = {item["path"]: item for item in entry["field_corrections"]}
    daily = fields["$.market_snapshot.spot[0].open_24h_usd"]
    derived = fields["$.market_snapshot.spot[0].last_vs_open_pct"]
    assert daily["canonical_name"] == "daily_open_usd"
    assert derived["canonical_name"] == "last_vs_daily_open_pct"
    expected = (1.2922 / 1.27513 - 1) * 100
    assert math.isclose(derived["canonical_value"], expected, rel_tol=0, abs_tol=0.00005)


def test_coinbase_xpm_dash_is_null_not_zero():
    data = load_artifact()
    entry = correction(data, "C04_COINBASE_XPM_DASH_NOT_ZERO")
    fields = {item["path"]: item for item in entry["field_corrections"]}
    xpm = fields["$.product_scope_matrix[0].haircut_cross_portfolio_margin_pct"]
    assert xpm["canonical_value"] is None
    assert xpm["displayed_source_cell"] == "—"
    assert "15%" in fields["$.relationships[3].notes"]["canonical_value"]


def test_youtube_metric_finding_cites_the_metric_source_not_channel_search():
    data = load_artifact()
    entry = correction(data, "C05_YOUTUBE_F2_EVIDENCE_LINK")
    assert entry["finding_id"] == "F2"
    assert "youtube_video_search_result_137k" in entry["canonical_evidence"]
    assert "youtube_channel_search_result" not in entry["canonical_evidence"]
    assert entry["status"] == "METRICS_NOT_COMPARABLE; DO_NOT_USE_FOR_IDENTITY"


def test_circle_arc_validator_claim_uses_circle_launch_source_and_limits_status():
    data = load_artifact()
    entry = correction(data, "C06_CIRCLE_ARC_VALIDATOR_SOURCE")
    sources = source_map(data)
    assert entry["canonical_evidence_source_ids"] == ["circle_arc_mainnet_launch"]
    assert "SBI Group is named" in sources["circle_arc_mainnet_launch"]["claims_supported"][0]
    assert "RUNTIME_NOT_INDEPENDENTLY_VERIFIED" in entry["canonical_status"]


def test_evernorth_facility_lender_cost_basis_and_graph_are_reconciled():
    data = load_artifact()
    entry = correction(data, "C07_EVERNORTH_CAPITAL_LEDGER")
    fields = {item["path"]: item for item in entry["field_corrections"]}
    assert fields["$.capital_reconciliation.additional_debt_capital[2].source"]["canonical_value"].startswith("Ripple Labs")
    avg = fields["$.xrp_asset_reconciliation.cash_funded_market_purchase.implied_average_cost_usd_per_xrp"]
    assert math.isclose(avg["canonical_value"], 214050000 / 84365876, rel_tol=0, abs_tol=0.000000005)
    edges = entry["canonical_graph_edges"]
    identities = {(e["from"], e["to"], e["relation"]) for e in edges}
    assert len(edges) == len(identities) == 2
    assert entry["duplicate_edge_count_removed_from_canonical_view"] == 2
    assert entry["separate_capital_items"][0]["purchaser"].startswith("NH Investment")
    assert entry["separate_capital_items"][1]["lender"] == "Ripple Labs Inc."


def test_creator_identity_is_unverified_and_video_inventory_is_blocked():
    data = load_artifact()
    entry = correction(data, "C09_CREATOR_IDENTITY_SUPERSESSION")
    assert entry["superseded_observation"] == "O27"
    assert entry["canonical_status"] == "UNVERIFIED; DO_NOT_INVENTORY"
    assert entry["candidate_list_exhaustive"] is False
    assert "Camila Stevenson" in entry["name_variants"]
    assert entry["video_inventory_status"] == "NOT_STARTED_PENDING_FIRST_PARTY_CHANNEL_CROSS_LINK"
    assert "UCXm6KAr1WHF6UN7g5b2W7wg" in entry["candidate_channel_ids"]


def test_actual_capital_phrase_is_secondary_commentary_only():
    data = load_artifact()
    entry = correction(data, "C10_ACTUAL_CAPITAL_PHRASE_QUALIFICATION")
    assert entry["canonical_classification"] == "SECONDARY_COMMENTARY_LEAD_ONLY"
    assert entry["primary_evidence_of_capital_from_this_source"] is False


def test_pillars_fiction_scan_is_inconclusive_until_http_200_is_verified():
    data = load_artifact()
    entry = correction(data, "C11_PILLARS_FICTION_SCAN_HTTP_STATUS")
    assert entry["original_status"] == "PASS_SOURCE_ONLY"
    assert entry["canonical_status"] == "INCONCLUSIVE_HTTP_STATUS_UNVERIFIED"
    assert entry["related_pr"] == 1640


def test_each_derivatives_etf_observation_is_explicitly_model_ineligible():
    data = load_artifact()
    entry = correction(data, "C12_DERIVATIVES_AND_ETF_OBSERVATION_ELIGIBILITY")
    observations = entry["observation_eligibility"]
    assert len(observations) == 6
    assert len({item["observation_id"] for item in observations}) == 6
    assert all(item["model_eligible"] is False and item["reason"] for item in observations)


def test_sbic_regional_entities_and_sbi_holdings_are_distinct():
    data = load_artifact()
    entry = correction(data, "C13_SBIC_SBI_CHATGPT_ENTITY_BOUNDARY")
    names = {item["alias"] for item in entry["canonical_entities"]}
    assert {"SBIC East Japan", "SBIC Central Japan", "SBIC West Japan", "SBI Group parent"} <= names
    distinctions = " ".join(entry["distinctions"])
    assert "not an OpenAI partnership" in distinctions
    assert "ChatGPT Enterprise adoption" in distinctions
    assert "Ethereum-only" in distinctions
