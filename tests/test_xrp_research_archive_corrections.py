"""Regression tests for append-only XRP archive review corrections."""
from __future__ import annotations

import hashlib
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


def json_path_value(root, path):
    assert path.startswith("$.")
    value = root
    for segment in path[2:].split("."):
        if "[" in segment:
            key, index = segment[:-1].split("[", 1)
            value = value[key][int(index)]
        else:
            value = value[segment]
    return value


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
        for source_id in entry.get("canonical_evidence_source_ids", []):
            assert source_id in known
        for entity in entry.get("canonical_entities", []):
            for source_id in entity.get("evidence_source_ids", []):
                assert source_id in known
        for source_id in entry.get("canonical_edge", {}).get("evidence_source_ids", []):
            assert source_id in known


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
    circle = next(x for x in replacements if x.get("source_id") == "circle_q2_2026_10q_correct")
    ripple = next(x for x in replacements if x.get("source_id") == "ripple_occ_cas_correct")
    coinbase = next(x for x in replacements if x.get("source_id") == "coinbase_occ_cas_correct")
    circle_occ = next(x for x in replacements if x.get("source_id") == "circle_occ_cas_final")
    coinbase_decision = next(x for x in replacements if x.get("source_id") == "coinbase_occ_decision_1370")
    assert "000187604226000248" in circle["canonical_url"]
    assert "000187604226000045" in circle["old_url"]
    assert "RjzoD2gxmYOv" in ripple["canonical_url"]
    assert "3RAoRRek6o4j" in coinbase["canonical_url"]
    assert "D79Z71vmerN8" in circle_occ["canonical_url"]
    assert ripple["canonical_url"] != coinbase["canonical_url"]
    assert circle["target_field"] == "$.bank_charter_status.circle.sources[0]"
    assert circle_occ["target_field"] == "$.bank_charter_status.circle.sources[1]"
    assert ripple["target_field"] == "$.bank_charter_status.ripple.sources[0]"
    assert coinbase["target_field"] == "$.bank_charter_status.coinbase.sources[1]"
    assert coinbase_decision["target_field"] == "$.bank_charter_status.coinbase.sources[0]"
    assert source_map(data)["circle_occ_cas_final"]["model_eligible"] is False
    assert "2026-07-24" in " ".join(source_map(data)["circle_occ_cas_final"]["claims_supported"])

    target_path = ROOT / entry["target_artifact"]
    target = json.loads(target_path.read_text(encoding="utf-8"))
    targeted_paths = set()
    for replacement in replacements:
        target_field = replacement.get("target_field")
        if not target_field:
            continue
        assert target_field not in targeted_paths
        targeted_paths.add(target_field)
        assert json_path_value(target, target_field) == replacement["old_url"]
    assert len(targeted_paths) == entry["preimage_validation"]["targeted_replacement_count"]
    assert entry["preimage_validation"]["non_targeted_candidate_count"] == 2


def test_dangling_handoff_is_not_referenced_as_existing():
    data = load_artifact()
    entry = correction(data, "C02_DANGLING_HANDOFF_REFERENCE")
    assert entry["invalid_reference"].endswith("HANDOFF_20261103T223519Z-PROVENANCE-CLOCK-AUDIT.md")
    assert all(ref.endswith("20261103T223519Z-research-artifact-clock-audit.json") or ref.startswith("https://github.com/") for ref in entry["canonical_references"])
    assert entry["target_field"] == "$.provenance_correction.references"
    assert entry["canonical_value"] == entry["canonical_references"]
    assert entry["application_status"] == "NOT_EXECUTED_RESEARCH_ONLY_OVERLAY"


def test_kraken_open_is_daily_not_rolling_24h():
    data = load_artifact()
    entry = correction(data, "C03_KRAKEN_UTC_DAILY_OPEN")
    fields = {item["path"]: item for item in entry["field_corrections"]}
    daily = fields["$.market_snapshot.spot[0].open_24h_usd"]
    derived = fields["$.market_snapshot.spot[0].last_vs_open_pct"]
    assert daily["canonical_name"] == "daily_open_usd"
    assert daily["canonical_path"] == "$.market_snapshot.spot[0].daily_open_usd"
    assert derived["canonical_name"] == "last_vs_daily_open_pct"
    assert derived["canonical_path"] == "$.market_snapshot.spot[0].last_vs_daily_open_pct"
    expected = (1.2922 / 1.27513 - 1) * 100
    assert math.isclose(derived["canonical_value"], expected, rel_tol=0, abs_tol=0.00005)


def test_coinbase_xpm_dash_is_null_not_zero():
    data = load_artifact()
    entry = correction(data, "C04_COINBASE_XPM_DASH_NOT_ZERO")
    fields = {item["path"]: item for item in entry["field_corrections"]}
    xpm = fields["$.product_scope_matrix[1].haircut_cross_portfolio_margin_pct"]
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
    assert entry["superseded_evidence_source_ids"] == ["circle_q3_2026_presentation", "sbi_circle_jv"]
    assert entry["canonical_edge"]["evidence_source_ids"] == ["circle_arc_mainnet_launch"]
    assert entry["canonical_edge"]["to"] == "Circle Arc"


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
    assert entry["related_pr_head"] == "398a2e8a3664f638416923cd0665f1f2a8d1389a"
    assert entry["branch_status"].startswith("HTTP_STATUS_GUARD_PRESENT")


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



def test_occ_news_release_2026_29_is_not_a_charter_approval():
    data = load_artifact()
    entry = correction(data, "C01_SOURCE_CITATION_CROSSWALK")
    replacement = next(x for x in entry["replacements"] if x["old_url"].endswith("nr-occ-2026-29.html"))
    assert replacement["canonical_url"].endswith("/cd1370.pdf")
    source = source_map(data)["occ_model_risk_2026_29"]
    assert source["published_at_utc"] == "2026-04-17"
    assert "Model Risk Management Guidance" in source["claims_supported"][0]


def test_circle_arc_is_a_usdc_gas_counter_hypothesis_not_xrp_evidence():
    data = load_artifact()
    entry = correction(data, "C14_CIRCLE_ARC_USDC_NATIVE_COUNTERHYPOTHESIS")
    source = source_map(data)["circle_arc_mainnet_launch"]
    assert any("fees are paid in USDC" in claim for claim in source["claims_supported"])
    assert "NO_DIRECTIONAL_XRP_EFFECT_ADMITTED" == entry["forecast_effect"]
    assert entry["model_eligible"] is False


def test_unverified_publication_dates_remain_unknown():
    data = load_artifact()
    sources = source_map(data)
    assert sources["ripple_occ_cas_correct"]["published_at_utc"] is None
    assert sources["coinbase_global_derivatives_cross_collateral"]["published_at_utc"] is None


def test_circle_and_ripple_occ_replacements_are_entity_scoped():
    data = load_artifact()
    replacements = correction(data, "C01_SOURCE_CITATION_CROSSWALK")["replacements"]
    by_id = {item["source_id"]: item for item in replacements if item.get("source_id")}
    assert by_id["circle_occ_cas_final"]["target_field"] == "$.bank_charter_status.circle.sources[1]"
    assert by_id["ripple_occ_cas_correct"]["target_field"] == "$.bank_charter_status.ripple.sources[0]"
    assert by_id["ripple_rntb_final_approval"]["target_field"] == "$.bank_charter_status.ripple.sources[1]"
    assert by_id["circle_occ_cas_final"]["target_field"] != by_id["ripple_occ_cas_correct"]["target_field"]
    assert "D79Z71vmerN8" in by_id["circle_occ_cas_final"]["canonical_url"]
    assert "RjzoD2gxmYOv" in by_id["ripple_occ_cas_correct"]["canonical_url"]
    assert "ripple_rntb_press_slug_candidate" in {item.get("candidate_id") for item in replacements}
    assert "occ_generic_interpretations_index_candidate" in {item.get("candidate_id") for item in replacements}
    assert all("source_id" not in item and "target_field" not in item for item in replacements if item.get("candidate_id"))



 
def test_circle_q3_results_are_post_event_append_only_and_not_model_eligible():
    path = ROOT / "research" / "xrp_intelligence" / "20261104T150819Z-circle-q3-2026-results-primary-release-and-xrp-counterhypothesis.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    sources = {item["id"]: item for item in data["source_registry"]}
    assert data["forecast_issued"] is False
    assert data["prediction_status"] == "NOT_ISSUED"
    assert data["model_eligible"] is False
    assert data["data_quality"]["raw_content_sha256_available"] is False
    assert sources["circle_q3_2026_earnings_release"]["model_eligible"] is False
    assert sources["circle_q3_2026_earnings_release"]["raw_content_sha256"] is None
    assert data["financial_observations"][0]["value_usd_billions"] == 73.3
    assert data["financial_observations"][1]["value_usd_billions"] == 73.9
    assert data["financial_observations"][2]["value_usd_trillions"] == 13.9
    other = next(x for x in data["financial_observations"] if x["id"] == "CIRCLE-Q3-OTHER-REVENUE-2026")
    assert other["includes_arc_token_presale_usd_millions"] == 182
    assert other["derived_other_revenue_ex_arc_usd_millions"] == 25.264
    assert other["derived_arc_presale_share_of_other_revenue_pct"] > 87
    assert data["arc_token_economics"]["genesis_mint_tokens_billions"] == 10
    assert data["arc_token_economics"]["gas_fee_asset"] == "USDC"
    assert data["xrp_implications"]["directional_effect"] == "UNRESOLVED_NO_DIRECTIONAL_XRP_EFFECT_ADMITTED"
    assert all(not x["model_eligible"] for x in data["financial_observations"])


def test_circle_q3_post_event_overlay_preserves_original_cutoff():
    data = load_artifact()
    entry = correction(data, "C15_CIRCLE_Q3_2026_RESULTS_POST_EVENT")
    assert entry["prior_status_at_original_cutoff"] == "future_scheduled_event"
    assert entry["canonical_status"] == "RESULTS_RELEASED_2026-11-04T13:00:00Z"
    assert entry["original_artifact_modified"] is False
    assert entry["superseding_artifact"].endswith("20261104T150819Z-circle-q3-2026-results-primary-release-and-xrp-counterhypothesis.json")
    assert entry["source_id"] == "circle_q3_2026_earnings_release"


def test_arc_token_context_is_updated_without_relabeling_usdc_gas():
    data = load_artifact()
    entry = correction(data, "C14_CIRCLE_ARC_USDC_NATIVE_COUNTERHYPOTHESIS")
    assert entry["additional_evidence_source_ids"] == ["circle_q3_2026_earnings_release"]
    assert "10B ARC genesis mint" in entry["token_context_update"]
    assert "transaction fees are paid in USDC" in entry["token_context_update"]



def test_xrpl_fixcleanup_activation_is_confirmed_by_two_node_backed_trackers():
    path = ROOT / "research" / "xrp_intelligence" / "20261104T152533Z-xrpl-fixcleanup-activation-post-window-verification.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    amendment = data["amendment"]
    assert amendment["status"] == "ENABLED_CONFIRMED_BY_TWO_NODE_BACKED_PUBLIC_TRACKERS"
    assert amendment["enablement_ledger"] == 108112129
    assert amendment["actual_enablement_utc"] == "2026-11-04T14:52:00Z"
    assert amendment["reported_yes_votes_at_enablement"] == 33
    assert amendment["threshold_yes_votes"] == 29
    assert amendment["enable_amendment_transaction"] == "F2E0342BC2419508DBAB9E869B7057941A07782426167396F87C7D0CA008FA6C"
    assert data["xrp_implications"]["native_xrp_supply_effect"] is False
    assert data["xrp_implications"]["directional_price_signal"] == "NONE_ADMITTED"
    assert data["forecast_issued"] is False
    assert data["model_eligible"] is False
    assert data["data_quality"]["independent_node_backed_observers"] == 2


def test_xrpl_fixcleanup_does_not_activate_lending_or_single_asset_vault():
    path = ROOT / "research" / "xrp_intelligence" / "20261104T152533Z-xrpl-fixcleanup-activation-post-window-verification.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    states = {item["name"]: item for item in data["other_amendment_status_at_capture"]}
    assert states["SingleAssetVault"]["yes_votes"] == 21
    assert states["LendingProtocol"]["yes_votes"] == 19
    assert states["LendingProtocolV1_1"]["yes_votes"] == 19
    assert all(states[name]["status"] == "NOT_ENABLED" for name in ("SingleAssetVault", "LendingProtocol", "LendingProtocolV1_1"))


def test_xrpl_activation_overlay_preserves_official_docs_warning_as_stale_not_live_status():
    data = load_artifact()
    entry = correction(data, "C16_XRPL_FIXCLEANUP_POST_WINDOW_ACTIVATION")
    assert entry["canonical_status"] == "ENABLED_2026-11-04T14:52:00Z_LEDGER_108112129"
    assert entry["original_artifact_modified"] is False
    assert "xrpldashboard_fixcleanup_activation" in entry["evidence_source_ids"]
    assert "xrplwin_fixcleanup_activation" in entry["evidence_source_ids"]
    assert "xrpl_official_permission_values" in entry["evidence_source_ids"]


def test_evernorth_sbi_share_class_crosswalk_preserves_both_primary_snapshots():
    data = load_artifact()
    entry = correction(data, "C17_SBI_EVERNORTH_SHARE_CLASS_CROSSWALK")
    assert entry["original_artifact_modified"] is False
    old = entry["prior_closing_8k_observation"]
    new = entry["later_prospectus_observation"]
    assert old["as_of"] == "2026-10-09"
    assert (old["class_a_shares"], old["class_c_shares"]) == (8885293, 2905659)
    assert (old["class_a_pct_of_class"], old["class_c_pct_of_class"]) == (39.9, 9.0)
    assert new["as_of"] == "2026-10-22"
    assert (new["class_a_shares"], new["class_c_shares"]) == (9431914, 2359038)
    assert (new["class_a_pct_of_class"], new["class_c_pct_of_class"]) == (36.1, 7.5)
    assert old["combined_shares"] == new["combined_shares"] == 11790952
    assert entry["reconciliation"]["class_a_delta_shares"] == 546621
    assert entry["reconciliation"]["class_c_delta_shares"] == -546621
    assert entry["reconciliation"]["combined_delta_shares"] == 0
    assert entry["denominator_distinction"]["at_closing_pro_forma_voting_power_pct"] == 39.9
    assert "evernorth_business_combination_closing_8k_20261012" in entry["evidence_source_ids"]
    assert "evernorth_sec_424b3" in entry["evidence_source_ids"]
    assert data["model_eligible"] is False


def test_latest_live_market_snapshot_has_exact_raw_hashes_and_no_directional_forecast():
    path = ROOT / "research" / "xrp_intelligence" / "20261104T154705Z-live-spot-derivatives-etf-snapshot.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    sources = {item["id"]: item for item in data["source_registry"]}
    for source_id in ("kraken_xrpusd_ticker_20261104T154705Z", "binance_xrpusdt_premium_index_20261104T153541Z"):
        source = sources[source_id]
        digest = hashlib.sha256(source["raw_response_body"].encode("utf-8")).hexdigest()
        assert digest == source["raw_content_sha256"]
        assert source["model_eligible"] is False
    spot = data["market_snapshot"]["spot"]
    assert spot["last_usd"] == 1.32744
    assert spot["daily_open_utc_usd"] == 1.27513
    assert abs(spot["last_vs_daily_open_pct"] - 4.1023) < 0.001
    assert spot["spread_basis_points"] < 1.0
    assert data["market_snapshot"]["order_book_depth"]["status"] == "NOT_CAPTURED"
    perp = data["market_snapshot"]["perpetuals"]
    assert perp["source_time_utc"] == "2026-11-04T15:35:41Z"
    assert perp["age_at_capture_seconds"] == 684
    assert perp["stale_at_capture"] is True
    etf = data["market_snapshot"]["etf_flows"]
    assert etf["partial_funds_reported"] == 3
    assert etf["daily_reporting_funds_expected"] == 4
    assert etf["partial_day_is_final"] is False
    assert data["forecast_issued"] is False
    assert data["prediction_status"] == "NOT_ISSUED"
    assert data["model_eligible"] is False



def test_circle_q3_market_update_source_correction_points_to_primary_issuer_pdfs():
    market_path = ROOT / "research" / "xrp_intelligence" / "20261104T180409Z-xrp-market-and-circle-q3-update.json"
    correction_path = ROOT / "research" / "xrp_intelligence" / "20261104T200200Z-circle-q3-source-correction.json"
    market = json.loads(market_path.read_text(encoding="utf-8"))
    correction_data = json.loads(correction_path.read_text(encoding="utf-8"))
    sources = {item["id"]: item for item in market["source_registry"]}
    entries = {item["correction_id"]: item for item in correction_data["correction_overlay"]["entries"]}

    original = sources["circle_q3_2026_8k_ex99_1_20261104"]
    assert original["source_type"] == "primary_sec_8k_exhibit_99_1"
    assert "000187604226000309" in original["url"]

    release = entries["C22_CIRCLE_Q3_RELEASE_SOURCE_ID_AND_URL"]
    assert release["target_artifact"] == "research/xrp_intelligence/20261104T180409Z-xrp-market-and-circle-q3-update.json"
    assert release["target_field"] == "$.source_registry[2]"
    assert release["canonical_source_id"] == "circle_q3_2026_earnings_release_pdf"
    assert release["canonical_value"]["source_type"] == "primary_issuer_earnings_release_pdf"
    assert release["canonical_value"]["url"].endswith("3Q26-Earnings-Release.pdf")
    assert release["model_eligible"] is False

    presentation = entries["C23_CIRCLE_Q3_PRESENTATION_CANONICAL_SOURCE"]
    assert presentation["target_field"] == "$.source_registry[3]"
    assert presentation["canonical_source_id"] == "circle_q3_2026_earnings_presentation_pdf"
    assert presentation["canonical_value"]["url"].endswith("3Q26-Earnings-Presentation.pdf")
    assert "secondary copy" in presentation["treatment"]

    sec = next(x for x in correction_data["source_registry"] if x["id"] == "sec_edgar_circle_company_directory_20261104")
    assert sec["visible_latest_circle_accession"] == "0001876042-26-000291"
    assert "not verified" in " ".join(sec["claims_supported"]).lower()
    assert correction_data["correction_overlay"]["consumer_application_status"] == "NOT_EXECUTED_RESEARCH_ONLY_OVERLAY"
    assert correction_data["forecast_issued"] is False
    assert correction_data["prediction_status"] == "NOT_ISSUED"
    assert correction_data["model_eligible"] is False
