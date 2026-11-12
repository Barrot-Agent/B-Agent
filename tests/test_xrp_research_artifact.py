import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T011000Z-institutional-collateral-identity.json"
)


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None
    return parsed.astimezone(timezone.utc)


def test_xrp_research_artifact_has_valid_provenance_and_cutoff() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_ecosystem_evidence_reconciliation"
    assert data["repository"] == "Barrot-Agent/B-Agent"
    assert data["mission"]["priority"] == (
        "XRP intelligence and prediction-engine mastery"
    )
    assert _parse_utc(data["captured_at_utc"]) >= _parse_utc(
        data["data_cutoff_utc"]
    )
    assert _parse_utc(data["market_snapshot"]["observed_at_utc"]) <= _parse_utc(
        data["data_cutoff_utc"]
    )
    for observation in data["market_snapshot"].get("onchain_observations", []):
        assert _parse_utc(observation["retrieved_at_utc"]) <= _parse_utc(data["data_cutoff_utc"])


def test_xrp_research_evidence_references_are_resolvable() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    source_ids = [source["id"] for source in data["source_registry"]]
    assert len(source_ids) == len(set(source_ids))
    known = set(source_ids)

    for observation in data["observations"]:
        assert observation["id"]
        assert observation["class"]
        assert "evidence" in observation
        if observation["class"] != "unknown":
            assert observation["evidence"]
        assert set(observation["evidence"]) <= known

    for edge in data["relationship_graph"]:
        assert edge["from"]
        assert edge["to"]
        assert edge["relation"]
        assert edge["status"]
        assert set(edge["evidence"]) <= known


def test_xrp_hypotheses_and_prediction_boundary_are_explicit() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    hypothesis_ids = [item["id"] for item in data["competing_hypotheses"]]
    assert len(hypothesis_ids) >= 4
    assert len(hypothesis_ids) == len(set(hypothesis_ids))
    assert any(item["id"].endswith("::H7-sponsored-fees-shifts-xrp-demand") for item in data["competing_hypotheses"])
    assert any(item["id"].endswith("::H8-institutional-privacy-mpt-not-xrp") for item in data["competing_hypotheses"])
    assert any(item["id"].endswith("::H9-gross-volume-distortion") for item in data["competing_hypotheses"])
    assert any(item["id"].endswith("::H10-custody-is-not-xrp-demand") for item in data["competing_hypotheses"])
    assert any(item["id"].endswith("::H11-bank-rail-adoption-throughput-unknown") for item in data["competing_hypotheses"])
    assert any(item["id"].endswith("::H12-value-concentration-not-broad-adoption") for item in data["competing_hypotheses"])
    assert any(item["id"].endswith("::H13-SBI-multirail-hub") for item in data["competing_hypotheses"])

    for hypothesis in data["competing_hypotheses"]:
        assert hypothesis["claim"]
        assert hypothesis["support"]
        assert hypothesis["disconfirming_or_missing"]
        assert hypothesis["tests"]

    assert data["predictions"]["issued"] is False
    assert data["predictions"]["reason"]
    assert data["blockers"]
    assert data["next_actions"]



def test_nine_platform_map_does_not_overstate_live_connections() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    platforms = data["platform_map"]
    names = [item["platform"] for item in platforms]
    assert len(names) == 9
    assert len(names) == len(set(names))
    assert set(names) == {
        "ChatGPT", "Claude", "Grok", "Gemini", "Copilot",
        "Codex", "Hugging Face", "Kaggle", "Databricks",
    }
    assert next(item for item in platforms if item["platform"] == "ChatGPT")[
        "status"
    ] == "tested_current_runtime"
    for item in platforms:
        if item["platform"] != "ChatGPT":
            assert item["status"] in {
                "not_tested", "workflow_reference_only"
            }
            authentication = item["authentication"].lower()
            assert "no authenticated" in authentication or (
                "no live" in authentication
            ) or ("no separate" in authentication)
    contract = data["agent_exchange_contract"]
    assert contract["disagreement_policy"]
    assert contract["least_privilege_policy"]
    assert contract["adapter_status"].startswith("Architecture designed")


ADDENDUM = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T030546Z-market-structure-capital-flow-addendum.json"
)


def test_market_addendum_source_references_and_graph_are_resolvable() -> None:
    data = json.loads(ADDENDUM.read_text(encoding="utf-8"))
    source_ids = [source["id"] for source in data["source_registry"]]
    assert len(source_ids) == len(set(source_ids))
    known = set(source_ids)
    assert len(data["observations"]) >= 8
    assert len(data["relationship_graph"]) >= 5
    assert len(data["competing_hypotheses"]) >= 4

    for observation in data["observations"]:
        assert observation["id"]
        assert observation["claim"]
        assert set(observation["evidence"]) <= known

    for edge in data["relationship_graph"]:
        assert edge["from"] and edge["to"] and edge["relation"]
        assert set(edge["evidence"]) <= known

    for hypothesis in data["competing_hypotheses"]:
        assert hypothesis["claim"]
        assert hypothesis["support"]
        assert hypothesis["disconfirming_or_missing"]
        assert hypothesis["test"]


def test_market_addendum_preserves_provider_and_etf_disagreements() -> None:
    data = json.loads(ADDENDUM.read_text(encoding="utf-8"))
    cutoff = _parse_utc(data["data_cutoff_utc"])
    for item in data["market_snapshot"]["derivatives"]:
        assert _parse_utc(item["as_of_utc"]) <= cutoff

    oi = data["market_snapshot"]["derivatives"]
    assert oi[0]["open_interest_usd"] != oi[1]["open_interest_usd"]
    assert "Do not average" in data["data_quality"]["no_averaging_policy"]

    etf = data["market_snapshot"]["etf_flows"]
    assert len(etf) == 2
    assert etf[0]["net_flow_xrp"] != 0
    assert etf[1]["net_flow_usd"] != 0
    assert data["mission"]["prediction_status"] == "NOT_ISSUED"


def test_market_addendum_quarantines_internally_inconsistent_source() -> None:
    data = json.loads(ADDENDUM.read_text(encoding="utf-8"))
    quarantined = set(data["data_quality"]["quarantined_sources"])
    assert "swiftedge_xrp_perps_dynamic_20261104_0305z" in quarantined
    source = next(
        item for item in data["source_registry"]
        if item["id"] == "swiftedge_xrp_perps_dynamic_20261104_0305z"
    )
    assert any("later than this run" in limitation for limitation in source["limitations"])
    observation = next(
        item for item in data["observations"]
        if item["id"] == "OBS-SWIFTEDGE-20261104-01"
    )
    assert observation["evidence"] == [source["id"]]
    assert observation["classification"] == "quarantined_source_observation"


def test_ripple_corporate_claims_are_not_mislabeled_as_xrp_flows() -> None:
    data = json.loads(ADDENDUM.read_text(encoding="utf-8"))
    source_ids = {source["id"] for source in data["source_registry"]}
    assert "ripple_corporate_strategy_20261028" in source_ids
    claims = [
        item for item in data["observations"]
        if item["id"].startswith("OBS-RIPPLE-CORP-")
    ]
    assert len(claims) >= 5
    assert all(item["classification"].startswith("issuer_") for item in claims)
    assert all("not" in " ".join(item["disconfirming_or_limiting"]).lower()
               or "undisclosed" in " ".join(item["disconfirming_or_limiting"]).lower()
               for item in claims)
    rntb = next(
        item for item in data["observations"]
        if item["id"] == "OBS-RNTB-20261104-02"
    )
    assert "ripple_rntb_final_approval_20261026" in rntb["evidence"]
    assert "ripple_corporate_strategy_20261028" in rntb["evidence"]


def test_circle_q3_event_is_future_at_research_cutoff() -> None:
    data = json.loads(ADDENDUM.read_text(encoding="utf-8"))
    event = next(
        item for item in data["observations"]
        if item["id"] == "OBS-CIRCLE-Q3-20261104-01"
    )
    source_ids = {source["id"] for source in data["source_registry"]}
    assert event["classification"] == "confirmed_scheduled_event"
    assert set(event["evidence"]) <= source_ids
    cutoff = _parse_utc(data["captured_at_utc"])
    event_time = _parse_utc("2026-11-04T13:00:00Z")
    assert event_time > cutoff


def test_requested_camilla_identity_is_not_conflated_with_kamilah_candidate() -> None:
    data = json.loads(ADDENDUM.read_text(encoding="utf-8"))
    identity = data["identity_disambiguation"]
    assert identity["requested_identity"] == "Camilla Stephenson"
    assert identity["candidate_identity"].startswith("Kamilah Stevenson")
    assert identity["status"] == "UNRESOLVED_NOT_EQUIVALENT"
    assert identity["candidate_video_count"] == 12
    assert identity["inventory_exhaustive"] is False
    assert "Do not label" in identity["attribution_rule"]
    source_ids = {source["id"] for source in data["source_registry"]}
    observation = next(
        item for item in data["observations"]
        if item["id"] == "OBS-IDENTITY-20261104-01"
    )
    assert set(observation["evidence"]) <= source_ids

LIQUIDITY_ADDENDUM = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T034115Z-market-liquidity-usdc-etf-addendum.json"
)


def test_liquidity_addendum_has_cutoff_and_resolvable_sources() -> None:
    data = json.loads(LIQUIDITY_ADDENDUM.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_market_liquidity_usdc_etf_addendum"
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(data["data_cutoff_utc"])
    source_ids = [item["id"] for item in data["source_registry"]]
    assert len(source_ids) == len(set(source_ids))
    known = set(source_ids)
    for observation in data["observations"]:
        assert observation["claim"]
        assert set(observation["evidence"]) <= known
    for edge in data["relationship_graph"]:
        assert edge["from"] and edge["to"] and edge["relation"]
        assert set(edge["evidence"]) <= known
    assert data["predictions"]["issued"] is False


def test_liquidity_addendum_preserves_scope_and_provider_disagreement() -> None:
    data = json.loads(LIQUIDITY_ADDENDUM.read_text(encoding="utf-8"))
    assert len(data["market_snapshot"]["etf_flows"]) == 2
    assert data["market_snapshot"]["circle_usdc"]["scope"].startswith("Global USDC")
    assert "Do not average" in data["data_quality"]["no_averaging_policy"]
    assert data["market_snapshot"]["xrp_spot_aggregate"]["model_eligible"] is False
    event = data["market_snapshot"]["upcoming_events"][0]
    assert event["status_at_cutoff"] == "future_scheduled_event"
    assert _parse_utc(event["scheduled_at_utc"]) > _parse_utc(data["data_cutoff_utc"])

PROTOCOL_ADDENDUM = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T040211Z-protocol-derivatives-event-addendum.json"
)


def test_protocol_addendum_provenance_graph_and_prediction_boundary() -> None:
    data = json.loads(PROTOCOL_ADDENDUM.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_protocol_derivatives_event_addendum"
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(data["data_cutoff_utc"])
    sources = {item["id"] for item in data["source_registry"]}
    assert len(sources) == len(data["source_registry"])
    assert len(data["observations"]) >= 8
    assert len(data["relationship_graph"]) >= 5
    assert len(data["competing_hypotheses"]) >= 4
    for observation in data["observations"]:
        assert observation["id"] and observation["claim"]
        assert set(observation["evidence"]) <= sources
    for edge in data["relationship_graph"]:
        assert edge["from"] and edge["to"] and edge["relation"]
        assert set(edge["evidence"]) <= sources
    for hypothesis in data["competing_hypotheses"]:
        assert hypothesis["claim"] and hypothesis["support"]
        assert hypothesis["disconfirming_or_missing"] and hypothesis["test"]
    assert data["predictions"]["issued"] is False
    amendment = data["market_snapshot"]["xrpl_amendment"]
    assert amendment["status_at_cutoff"] == "activating_not_yet_enabled"
    assert amendment["validators_for"] == 33
    assert amendment["votes_required"] == 29
    event = data["market_snapshot"]["upcoming_events"][0]
    assert _parse_utc(event["scheduled_at_utc"]) > _parse_utc(data["data_cutoff_utc"])
    assert data["market_snapshot"]["lending_protocol"]["status_at_cutoff"] == "not_enabled"


EVENT_ADDENDUM = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T050632Z-circle-arc-binance-xrpl-event-addendum.json"
)


def test_circle_arc_binance_and_xrpl_event_addendum_is_provenance_safe() -> None:
    data = json.loads(EVENT_ADDENDUM.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_circle_arc_and_protocol_event_addendum"
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(data["data_cutoff_utc"])
    source_ids = [item["id"] for item in data["source_registry"]]
    assert len(source_ids) == len(set(source_ids))
    known = set(source_ids)

    for observation in data["observations"]:
        assert observation["id"] and observation["class"] and observation["detail"]
        assert observation["evidence"]
        assert set(observation["evidence"]) <= known

    for edge in data["relationship_graph"]:
        assert edge["from"] and edge["to"] and edge["relation"] and edge["status"]
        assert set(edge["evidence"]) <= known

    for hypothesis in data["competing_hypotheses"]:
        assert hypothesis["claim"]
        assert hypothesis["support"]
        assert hypothesis["disconfirming_or_missing"]
        assert hypothesis["tests"]

    assert data["predictions"]["issued"] is False


def test_circle_q3_and_fixcleanup_events_are_not_mislabeled_as_completed() -> None:
    data = json.loads(EVENT_ADDENDUM.read_text(encoding="utf-8"))
    cutoff = _parse_utc(data["data_cutoff_utc"])
    circle_event = next(
        item for item in data["observations"]
        if item["id"] == "OBS-CIRCLE-Q3-20261104-02"
    )
    assert circle_event["class"] == "confirmed_scheduled_event"
    assert _parse_utc("2026-11-04T13:00:00Z") > cutoff

    fix = data["market_snapshot"]["xrpl_amendment"]
    assert fix["votes_for"] == 33
    assert fix["trusted_validators"] == 35
    assert fix["threshold_votes"] == 29
    assert fix["active_at_cutoff"] is False
    assert _parse_utc(fix["earliest_activation_utc"]) > cutoff


ETF_FLOW_ADDENDUM = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T050900Z-etf-flow-source-disagreement.json"
)


def test_etf_flow_provider_disagreement_is_preserved_not_averaged() -> None:
    data = json.loads(ETF_FLOW_ADDENDUM.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_etf_flow_source_disagreement_addendum"
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(data["data_cutoff_utc"])
    source_ids = [item["id"] for item in data["source_registry"]]
    assert len(source_ids) == len(set(source_ids))
    known = set(source_ids)
    for observation in data["observations"]:
        assert observation["evidence"]
        assert set(observation["evidence"]) <= known
    snapshot = data["market_snapshot"]
    assert snapshot["xrp_insights"]["net_flow_xrp"] == -32825
    assert snapshot["bykaranteli"]["net_flow_usd"] == -530000
    assert snapshot["discrepancy"]["approx_ratio"] > 10
    assert "Do not average" in data["data_quality"]["no_averaging_policy"]
    assert data["predictions"]["issued"] is False


BINANCE_INCIDENT_ADDENDUM = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T051139Z-binance-hot-wallet-incident.json"
)


def test_binance_incident_addendum_preserves_xrp_flow_exclusion() -> None:
    data = json.loads(BINANCE_INCIDENT_ADDENDUM.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_binance_hot_wallet_incident_addendum"
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(data["data_cutoff_utc"])
    source_ids = [item["id"] for item in data["source_registry"]]
    assert len(source_ids) == len(set(source_ids))
    known = set(source_ids)
    for observation in data["observations"]:
        assert observation["evidence"]
        assert set(observation["evidence"]) <= known
    for edge in data["relationship_graph"]:
        assert edge["from"] and edge["to"] and edge["relation"] and edge["status"]
        assert set(edge["evidence"]) <= known
    for hypothesis in data["competing_hypotheses"]:
        assert hypothesis["claim"] and hypothesis["support"]
        assert hypothesis["disconfirming_or_missing"] and hypothesis["tests"]
    assert data["market_snapshot"]["xrp_outflow"]["amount_xrp"] == 233461943.1
    assert data["market_snapshot"]["xrp_repartition_as_of_20261103"]["main_recipient_wallets"] == 6
    assert data["predictions"]["issued"] is False
    assert "exclude it from organic exchange-flow" in data["data_quality"]["incident_exclusion_rule"].lower()


def test_binance_incident_keeps_attribution_and_freeze_scope_distinct() -> None:
    data = json.loads(BINANCE_INCIDENT_ADDENDUM.read_text(encoding="utf-8"))
    classes = {item["class"] for item in data["observations"]}
    assert "official_law_enforcement_attribution" in classes
    assert "official_denial_reported_by_independent_press" in classes
    freeze = data["market_snapshot"]["issuer_freezes"]
    assert freeze["ripple_rlusd_ethereum_usd_approx"] == 40500000
    assert freeze["circle_usdc_reuters_20261102"] == "more than $1.1B"
    assert freeze["circle_usdc_xrplwin_20261030"] == "$823M"
    assert "different dated snapshots" in data["data_quality"]["discrepancies"][1]["classification"]


INCIDENT_EVENT_ADDENDUM = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T061200Z-binance-flow-event-integrity-addendum.json"
)


def test_incident_event_addendum_has_resolvable_provenance_and_cutoff() -> None:
    data = json.loads(INCIDENT_EVENT_ADDENDUM.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_incident_flow_and_event_integrity_addendum"
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(data["data_cutoff_utc"])
    assert data["repository_state"]["inspected_main_sha"] == (
        "7f07db962be7d5adff7db347f0c297951d1d56c7"
    )
    source_ids = [item["id"] for item in data["source_registry"]]
    assert len(source_ids) == len(set(source_ids))
    known = set(source_ids)
    for observation in data["observations"]:
        assert observation["id"] and observation["class"] and observation["detail"]
        assert set(observation["evidence"]) <= known
    for edge in data["relationship_graph"]:
        assert edge["from"] and edge["to"] and edge["relation"] and edge["status"]
        assert set(edge["evidence"]) <= known
    for hypothesis in data["competing_hypotheses"]:
        assert hypothesis["claim"] and hypothesis["support"]
        assert hypothesis["disconfirming_or_missing"] and hypothesis["tests"]
    assert data["predictions"]["issued"] is False


def test_incident_flow_contamination_is_conditional_and_quarantined() -> None:
    data = json.loads(INCIDENT_EVENT_ADDENDUM.read_text(encoding="utf-8"))
    incident = data["market_snapshot"]["binance_incident"]["original_xrp_outflow"]
    flows = data["market_snapshot"]["trackwhale_seven_day_xrp_flows"]
    contamination = data["market_snapshot"]["conditional_incident_contamination"]
    assert incident["amount_xrp"] == 233461943.1
    assert contamination["inclusion_in_provider_aggregate"] == "unknown"
    assert contamination["model_treatment"].startswith("quarantine aggregate")
    assert abs(
        incident["amount_xrp"] / flows["gross_exchange_outflows_xrp"] * 100
        - contamination["incident_xrp_divided_by_reported_gross_outflows_percent"]
    ) < 0.1
    assert abs(
        incident["amount_xrp"] / abs(flows["net_exchange_flow_xrp"]) * 100
        - contamination["incident_xrp_divided_by_reported_net_outflow_percent"]
    ) < 0.1


def test_fixcleanup_and_circle_events_remain_future_at_cutoff() -> None:
    data = json.loads(INCIDENT_EVENT_ADDENDUM.read_text(encoding="utf-8"))
    cutoff = _parse_utc(data["data_cutoff_utc"])
    amendment = data["market_snapshot"]["xrpl_amendment"]
    circle = data["market_snapshot"]["circle_q3_event"]
    assert amendment["status_at_cutoff"] == "activating_not_yet_enabled"
    assert amendment["active_at_cutoff"] is False
    assert _parse_utc(amendment["earliest_activation_utc"]) > cutoff
    assert circle["status_at_cutoff"] == "future_scheduled_event"
    assert _parse_utc(circle["scheduled_at_utc"]) > cutoff
    assert data["predictions"]["issued"] is False


TRACKWHALE_CROSSVIEW_ADDENDUM = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T061400Z-trackwhale-crossview-consistency-addendum.json"
)


def test_trackwhale_crossview_addendum_quarantines_inconsistent_aggregates() -> None:
    data = json.loads(TRACKWHALE_CROSSVIEW_ADDENDUM.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_trackwhale_cross_view_consistency_addendum"
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(data["data_cutoff_utc"])
    source_ids = [item["id"] for item in data["source_registry"]]
    assert len(source_ids) == len(set(source_ids))
    known = set(source_ids)
    for observation in data["observations"]:
        assert observation["id"] and observation["class"] and observation["detail"]
        assert set(observation["evidence"]) <= known
    for edge in data["relationship_graph"]:
        assert edge["from"] and edge["to"] and edge["relation"] and edge["status"]
        assert set(edge["evidence"]) <= known
    for hypothesis in data["competing_hypotheses"]:
        assert hypothesis["claim"] and hypothesis["support"]
        assert hypothesis["disconfirming_or_missing"] and hypothesis["tests"]
    snapshot = data["market_snapshot"]
    assert (
        snapshot["xrp_exchange_flows_7d"]["binance_outflow_usd"]
        > snapshot["binance_exchange_flows_30d"]["page_reports_xrp_asset_outflow_usd"]
    )
    assert data["data_quality"]["model_eligibility"] == "quarantined"
    assert data["predictions"]["issued"] is False


def test_trackwhale_incident_membership_is_unknown_not_assumed() -> None:
    data = json.loads(TRACKWHALE_CROSSVIEW_ADDENDUM.read_text(encoding="utf-8"))
    assert data["market_snapshot"]["cross_view_checks"]["transaction_level_membership_confirmed"] is False
    assert data["data_quality"]["incident_membership"] == "unknown"
    assert "must not be used" in data["data_quality"]["correction_to_prior_conditional_calculation"]
    assert data["predictions"]["issued"] is False


def test_base_snapshot_moves_later_onchain_observations_to_addendum() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["market_snapshot"].get("onchain_observations", []) == []
    assert not any(item["id"] == "RLUSD-XRPL-supply-nov4-provider-disagreement" for item in data["observations"])
    addendum = next(item for item in data["addenda"] if item["captured_at_utc"] == "2026-11-04T02:10:41Z")
    addendum_cutoff = _parse_utc(addendum["data_cutoff_utc"])
    rows = addendum["market_snapshot"]["onchain_observations"]
    assert len(rows) == 3
    assert all(_parse_utc(item.get("retrieved_at_utc", item.get("observed_at_utc", "").replace(" approx", ""))) <= addendum_cutoff for item in rows)
    assert any(item["id"] == "RLUSD-XRPL-supply-nov4-provider-disagreement" for item in addendum["observations"])


def test_research_hypothesis_ids_are_namespaced_across_artifacts() -> None:
    names = [
        "20261104T011000Z-institutional-collateral-identity.json",
        "20261104T030546Z-market-structure-capital-flow-addendum.json",
        "20261104T034115Z-market-liquidity-usdc-etf-addendum.json",
        "20261104T040211Z-protocol-derivatives-event-addendum.json",
        "20261104T050632Z-circle-arc-binance-xrpl-event-addendum.json",
        "20261104T050900Z-etf-flow-source-disagreement.json",
        "20261104T051139Z-binance-hot-wallet-incident.json",
        "20261104T061200Z-binance-flow-event-integrity-addendum.json",
        "20261104T061400Z-trackwhale-crossview-consistency-addendum.json",
        "20261104T065909Z-live-market-event-update.json",
        "20261104T071800Z-coinbase-q3-collateral-sec-addendum.json",
    ]
    seen = set()
    for name in names:
        data = json.loads((REPO_ROOT / "research" / "xrp_intelligence" / name).read_text(encoding="utf-8"))
        namespace = data["hypothesis_id_namespace"]
        assert name.startswith(namespace + "-")
        for hypothesis in data["competing_hypotheses"]:
            assert hypothesis["id"].startswith(namespace + "::")
            assert hypothesis["id"] not in seen
            seen.add(hypothesis["id"])


def test_later_identity_search_is_separate_and_receipt_time_bounded() -> None:
    path = REPO_ROOT / "research" / "xrp_intelligence" / "20261104T065909Z-identity-phrase-followup.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert _parse_utc(data["captured_at_utc"]) >= _parse_utc(data["data_cutoff_utc"])
    assert _parse_utc(data["ingested_at_utc"]) == _parse_utc(data["captured_at_utc"])
    assert _parse_utc(data["historical_replay_eligible_from_utc"]) == _parse_utc(data["ingested_at_utc"])
    assert _parse_utc(data["search_scope"]["captured_at_utc"]) <= _parse_utc(data["data_cutoff_utc"])
    assert data["identity_disambiguation"]["status"] == "UNRESOLVED_NOT_EQUIVALENT"
    assert data["identity_disambiguation"]["inventory_exhaustive"] is False
    source_ids = {source["id"] for source in data["source_registry"]}
    for observation in data["observations"]:
        assert set(observation["evidence"]) <= source_ids
    assert data["predictions"]["issued"] is False


def test_live_market_event_update_preserves_disagreements_and_future_events() -> None:
    path = REPO_ROOT / "research" / "xrp_intelligence" / "20261104T065909Z-live-market-event-update.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    cutoff = _parse_utc(data["data_cutoff_utc"])
    assert _parse_utc(data["captured_at_utc"]) == cutoff
    assert data["predictions"]["issued"] is False
    assert data["market_snapshot"]["xrp_spot"]["model_eligible"] is False
    assert data["data_quality"]["no_averaging_policy"]
    replenishment = data["market_snapshot"]["binance_replenishment"]
    assert replenishment[0]["reported_pct"] == 98
    assert replenishment[1]["reported_pct"] == 95
    assert replenishment[0]["as_of_date"] != replenishment[1]["as_of_date"]
    for event in data["market_snapshot"]["upcoming_events"]:
        assert event["status_at_cutoff"] == "future_scheduled_event"
        assert _parse_utc(event["scheduled_at_utc"]) > cutoff


def test_coinbase_q3_sec_collateral_disclosures_do_not_imply_xrp_utilization() -> None:
    path = REPO_ROOT / "research" / "xrp_intelligence" / "20261104T071800Z-coinbase-q3-collateral-sec-addendum.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    lending = data["coinbase_q3"]["lending"]
    assert data["coinbase_q3"]["filing"]["period_end"] == "2026-09-30"
    assert lending["total_loan_receivables_usd"] == 1_976_137_000
    assert lending["crypto_asset_loan_receivables_usd"] == 17_598_000
    collateral = data["coinbase_q3"]["recognized_lending_collateral"]
    assert collateral["other_crypto_assets_aggregate_usd"] == 9_903_000
    assert collateral["xrp_specific_amount_usd"] is None
    assert collateral["conditional_xrp_upper_bound_if_in_other_bucket_usd"] == 9_903_000
    assert data["coinbase_q3"]["recognized_derivatives_collateral"]["xrp_line_disclosed"] is False
    assert data["coinbase_q3"]["unrecognized_borrower_collateral"]["crypto_asset_breakdown_by_token_available"] is False
    assert data["data_quality"]["quarter_end_precedes_october_1_xrp_collateral_policy_update"]
    assert data["predictions"]["issued"] is False


def test_rntb_approval_release_dates_are_separately_attributed() -> None:
    path = REPO_ROOT / "research" / "xrp_intelligence" / "20261104T011000Z-institutional-collateral-identity.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    sources = {source["id"]: source for source in data["source_registry"]}
    assert sources["ripple_rntb_final_oct26"]["published"] == "2026-10-26"
    assert sources["ripple_rntb_final_claim"]["published"] == "2026-10-28"
    edge = next(item for item in data["relationship_graph"] if item.get("to") == "Ripple National Trust Bank")
    assert "October 26" in edge["relation"]
    assert "October 28" in edge["relation"]


def test_coinbase_q3_relationship_edges_use_only_supported_sources() -> None:
    path = REPO_ROOT / "research" / "xrp_intelligence" / "20261104T071800Z-coinbase-q3-collateral-sec-addendum.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    source_ids = {source["id"] for source in data["source_registry"]}
    for edge in data["relationship_graph"]:
        assert set(edge["evidence"]) <= source_ids
    assert not any(edge["from"] == "Coinbase" and edge["to"] == "Ripple/RLUSD" for edge in data["relationship_graph"])


BINANCE_AMENDMENT_UPDATE = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T073349Z-binance-xrpl-amendment-market-update.json"
)


def test_binance_xrp_amendment_update_has_provenance_and_bounded_cutoffs():
    data = json.loads(BINANCE_AMENDMENT_UPDATE.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_binance_xrpl_amendment_market_update"
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(data["data_cutoff_utc"])
    source_ids = [item["id"] for item in data["source_registry"]]
    assert len(source_ids) == len(set(source_ids))
    known = set(source_ids)
    for observation in data["observations"]:
        assert observation["id"] and observation["claim"]
        assert observation["evidence"]
        assert set(observation["evidence"]) <= known
    for edge in data["relationship_graph"]:
        assert edge["from"] and edge["to"] and edge["relation"]
        assert edge["status"]
        assert set(edge["evidence"]) <= known
    assert data["predictions"]["issued"] is False


def test_binance_xrp_recipient_state_preserves_reconciliation_gap():
    data = json.loads(BINANCE_AMENDMENT_UPDATE.read_text(encoding="utf-8"))
    incident = data["market_snapshot"]["binance_xrp_incident"]
    assert len(incident["recipient_wallets"]) == 6
    assert incident["separate_test_destination"]["reported_balance_xrp"] == 1000
    assert incident["recipient_state_claim_as_of_utc"] == "2026-11-04T04:12:00Z"
    assert incident["recipient_outbound_transactions_reported_as_of_0412z"] == 0
    assert incident["sale_or_exchange_deposit_verified"] is False
    assert incident["arithmetic_difference_vs_initial_after_residual_xrp"] == 0.59905


def test_xrpl_amendment_is_not_marked_active_before_conditional_window():
    data = json.loads(BINANCE_AMENDMENT_UPDATE.read_text(encoding="utf-8"))
    amendment = data["market_snapshot"]["xrpl_amendments"]["fixCleanup3_4_0"]
    cutoff = _parse_utc(data["data_cutoff_utc"])
    activation = _parse_utc(amendment["earliest_activation_utc"])
    assert amendment["newer_tracker_votes_for"] == 34
    assert amendment["newer_tracker_trusted_validator_count"] == 36
    assert amendment["required_votes"] == 29
    assert amendment["active_verified"] is False
    assert activation > cutoff
    assert data["market_snapshot"]["upcoming_events"][0]["status_at_cutoff"] == "future_scheduled_event"


def test_xrp_market_provider_disagreement_is_not_averaged_or_model_eligible():
    data = json.loads(BINANCE_AMENDMENT_UPDATE.read_text(encoding="utf-8"))
    market = data["market_snapshot"]["xrp_market_aggregates"]
    assert market["coingecko"]["model_eligible"] is False
    assert market["altcoinlog"]["model_eligible"] is False
    assert market["coingecko"]["displayed_market_rows"] == 10
    assert market["coingecko"]["total_market_rows_reported"] == 130
    assert "Do not average" in data["data_quality"]["no_averaging_policy"]


CIRCLE_ARC_CPN = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T134427Z-circle-arc-cpn-network-scale-reconciliation.json"
)


def test_circle_arc_cpn_metrics_keep_gross_volume_and_annualized_tpv_separate():
    data = json.loads(CIRCLE_ARC_CPN.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_circle_arc_cpn_network_scale_reconciliation"
    assert data["prediction_status"]["status"] == "NOT_ISSUED"
    sources = {item["id"]: item for item in data["source_registry"]}
    assert len(sources) == len(data["source_registry"]) == 1
    source = next(iter(sources.values()))
    assert source["raw_content_sha256"] is None
    assert source["raw_capture_status"] == "web_rendered_pdf_text_extract_only"
    assert source["model_eligible"] is False

    observations = {item["id"]: item for item in data["observations"]}
    assert len(observations) == len(data["observations"])
    assert observations["arc_usdc_cumulative_volume_20261030"]["value"] == 30_000_000_000
    assert observations["arc_usdc_cumulative_volume_20261030"]["class"] == "issuer_reported_gross_transfer_metric"
    assert observations["cpn_annualized_tpv_q3_2026"]["value"] == 41_300_000_000
    assert observations["cpn_annualized_tpv_q3_2026"]["trailing_window_days"] == 30
    assert observations["x402_usdc_payment_volume_share_20261025"]["underlying_provider"] == "Artemis"
    assert observations["arc_payment_sector_tps_roadmap"]["status"] == "planned_target_not_achieved"
    assert all(item["model_eligible"] is False for item in data["observations"])
    for item in data["observations"]:
        assert item["evidence"]
        assert set(item["evidence"]) <= set(sources)

    for edge in data["relationship_graph"]:
        assert edge["from"] and edge["to"] and edge["relation"]
        assert edge["evidence"]
        assert set(edge["evidence"]) <= set(sources)
    assert len(data["competing_hypotheses"]) >= 4
    for hypothesis in data["competing_hypotheses"]:
        assert hypothesis["claim"]
        assert hypothesis["support"]
        assert hypothesis["disconfirming_or_missing"]
        assert hypothesis["tests"]
    assert any("USDC is also natively available on XRPL" in item for item in data["explicit_disconfirming_evidence"])
    assert any("Do not interpret gross transfer volume as net new capital" in item for item in data["data_quality"]["scope_controls"])


EVERNORTH_CANTOR_ELOC_ADDENDUM = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T140144Z-evernorth-cantor-eloc-pricing-fee-reconciliation.json"
)


def test_evernorth_cantor_facility_keeps_capacity_pricing_fees_and_actual_capital_separate() -> None:
    data = json.loads(EVERNORTH_CANTOR_ELOC_ADDENDUM.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_evernorth_cantor_eloc_pricing_fee_reconciliation_addendum"
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(data["data_cutoff_utc"])
    assert data["predictions"]["issued"] is False

    sources = {item["id"] for item in data["source_registry"]}
    assert len(sources) == len(data["source_registry"]) == 1
    assert data["source_registry"][0]["raw_content_sha256"] is None
    assert data["source_registry"][0]["model_eligible"] is False

    for observation in data["observations"]:
        assert observation["id"] and observation["claim"] and observation["evidence"]
        assert set(observation["evidence"]) <= sources
        assert observation["model_eligible"] is False

    for edge in data["relationship_graph"]:
        assert edge["from"] and edge["to"] and edge["relation"] and edge["status"]
        assert set(edge["evidence"]) <= sources

    for hypothesis in data["competing_hypotheses"]:
        assert hypothesis["id"].startswith(data["hypothesis_id_namespace"] + "::")
        assert hypothesis["support"]
        assert hypothesis["disconfirming_or_missing"]
        assert hypothesis["tests"]

    calc = data["capital_reconciliation"]["derived_scenarios"]
    shares = data["capital_reconciliation"]["reference_assumptions"]["maximum_new_class_a_shares"]
    price = data["capital_reconciliation"]["reference_assumptions"]["cover_page_closing_price_usd_per_share"]
    assert abs(calc["full_shares_at_cover_price_gross_usd"] - shares * price) < 0.00001
    assert abs(calc["hypothetical_proceeds_at_97pct_before_issuer_fees_usd"] - shares * price * 0.97) < 0.00001
    assert calc["specified_upfront_plus_stoneX_fee_usd"] > calc["difference_97pct_proxy_proceeds_minus_stated_net_usd"]
    assert calc["maximum_disclosed_capped_fee_items_usd"] == 1_701_000

    actual = data["capital_reconciliation"]["actual_capital"]
    assert actual["facility_drawdown_status"] == "not_established_in_reviewed_prospectus"
    assert actual["issuer_cash_receipt_from_facility"] == "not_established_in_reviewed_prospectus"
    assert actual["facility_funded_xrp_purchase"] == "not_established_in_reviewed_prospectus"
    assert actual["cantors_subsequent_resale_proceeds_to_issuer"] is False
    assert data["data_quality"]["reconciliation_status"] == "UNRESOLVED_ASSUMPTION_AND_FEE_BASIS"


NINE_PLATFORM_CAPABILITY_AUDIT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T141402Z-nine-platform-capability-authentication-observation.json"
)


def test_nine_platform_capability_audit_separates_session_and_connector_evidence() -> None:
    data = json.loads(NINE_PLATFORM_CAPABILITY_AUDIT.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "barrot_nine_platform_capability_authentication_audit"
    assert data["predictions"]["issued"] is False
    assert data["data_quality"]["model_eligible"] is False
    assert data["source_registry"][0]["raw_content_sha256"] is None

    platforms = {item["name"]: item for item in data["platforms"]}
    assert set(platforms) == {
        "ChatGPT", "Claude", "Grok", "Gemini", "Copilot",
        "Codex", "Hugging Face", "Kaggle", "Databricks",
    }
    assert all(item["live_barrot_adapter_verified"] is False for item in platforms.values())
    assert platforms["ChatGPT"]["observed_status"] == "current_chat_session_only"
    assert platforms["Grok"]["provider"] == "xAI"
    assert "Groq is a separate provider" in platforms["Grok"]["identity_note"]
    assert platforms["Copilot"]["observed_status"] == "single_use_review_event_observed"
    assert platforms["Hugging Face"]["observed_status"] == "public_runtime_probe_reachable_build_error"
    assert platforms["Databricks"]["observed_status"] == "sql_probe_http_403"
    assert platforms["Kaggle"]["observed_status"] == "not_verified"

    github = data["separate_integrations"]["github_repository_connector"]
    assert github["observed_status"] == "verified_repository_access"
    app = data["separate_integrations"]["github_app_pillars_probe"]
    assert app["observed_status"] == "environment_variables_not_available_to_job"

    checks = {item["id"]: item for item in data["workflow_observations"]}
    assert checks["PILLARS-REPO-SOURCE-MARKER-01"]["status"] == "PASS_SOURCE_ONLY"
    assert checks["PILLARS-REPO-SOURCE-FICTION-01"]["status"] == "PASS_SOURCE_ONLY"
    assert checks["PILLARS-HF-RUNTIME-01"]["status"] == "FAIL"
    assert checks["PILLARS-DATABRICKS-01"]["status"] == "FAIL"
    assert all(item["model_eligible"] is False for item in data["workflow_observations"])
    assert "DATABRICKS_TOKEN" not in json.dumps(data)
    assert "PRIVATE_KEY_VALUE" not in json.dumps(data)


MARKET_AMENDMENT_PREACTIVATION = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T141402Z-market-and-fixcleanup-preactivation.json"
)


def test_market_amendment_preactivation_snapshot_keeps_cutoffs_and_trackers_distinct() -> None:
    data = json.loads(MARKET_AMENDMENT_PREACTIVATION.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_market_and_xrpl_amendment_pre_activation_snapshot"
    assert data["predictions"]["issued"] is False
    assert data["data_quality"]["model_eligibility"] == "quarantined"
    sources = {item["id"] for item in data["source_registry"]}
    assert len(sources) == len(data["source_registry"])
    for item in data["observations"]:
        assert set(item["evidence"]) <= sources
        assert item["model_eligible"] is False
    for edge in data["relationship_graph"]:
        assert set(edge["evidence"]) <= sources

    market = data["market_snapshot"]
    kraken = market["kraken_xrpusd"]
    assert kraken["event_timestamp_available"] is False
    assert kraken["last_usd"] == 1.28084
    assert abs(kraken["spread_basis_points"] - 0.7026830782) < 1e-8
    perp = market["binance_xrpusdt_perpetual"]
    assert perp["event_timestamp_utc"] == "2026-11-04T13:29:55Z"
    assert perp["last_funding_rate"] == 0.0001
    assert perp["next_funding_time_utc"] == "2026-11-04T16:00:00Z"
    assert perp["open_interest"] == "not captured"
    assert perp["order_book_depth"] == "not captured"
    assert market["synchronization"]["kraken_vs_binance_spot_perp_basis"] == "NOT_COMPUTED"

    amendment = market["xrpl_amendment"]
    assert amendment["amendment_id"] == "98433DD001A5737F773D74F8CA2A25A065089C73B2E611C760BAF369E4FECA76"
    assert amendment["xrplwin_counts"]["votes_yes"] == 33
    assert amendment["xrplwin_counts"]["validators"] == 35
    assert amendment["xrplwin_counts"]["required_yes"] == 29
    assert amendment["actual_activation_verified"] is False
    assert amendment["status_at_cutoff"] == "PENDING_WINDOW_NOT_REACHED_AND_NOT_NODE_VERIFIED"
    assert _parse_utc(amendment["xrplwin_counts"]["earliest_activation_utc"]) > _parse_utc(data["data_cutoff_utc"])
    assert amendment["lending_protocol_amendment_votes_reported"] < amendment["xrplwin_counts"]["required_yes"]
    assert amendment["single_asset_vault_amendment_votes_reported"] < amendment["xrplwin_counts"]["required_yes"]
    dashboard = next(s for s in data["source_registry"] if s["id"].startswith("xrpldashboard_"))
    assert dashboard["signed_at_utc"] == "2026-11-04T01:00:00Z"
    assert dashboard["signed_snapshot_leaf_hash"] != dashboard["raw_content_sha256"]
    assert any("timezone is unspecified" in x for x in next(s for s in data["source_registry"] if s["id"].startswith("bithomp_"))["limitations"])


LIVE_TICKER_FOLLOWUP = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T221315Z-kraken-xrpusd-ticker-followup.json"
)


def test_kraken_ticker_followup_is_timestamp_bounded_and_not_model_eligible() -> None:
    data = json.loads(LIVE_TICKER_FOLLOWUP.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "append_only_single_venue_spot_ticker_followup"
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(data["data_cutoff_utc"])
    source = data["source_registry"][0]
    assert source["source_event_timestamp_utc"] is None
    assert source["raw_content_sha256"] is None
    assert source["model_eligible"] is False
    market = data["market_snapshot"]
    assert market["venue"] == "Kraken"
    assert market["best_bid_usd"] < market["best_ask_usd"]
    assert abs(
        market["spread_bps"]
        - (market["best_ask_usd"] - market["best_bid_usd"])
        / market["midpoint_usd"] * 10000
    ) < 1e-7
    assert market["best_ask_to_bid_size_ratio"] > 10
    assert data["prior_same_venue_comparison"]["elapsed_seconds"] == 4095
    assert data["data_quality"]["model_eligible"] is False
    assert data["predictions"]["issued"] is False
    assert "cache reuse cannot be excluded" in source["limitations"][2]


POST_ACTIVATION_ADDENDUM = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T224049Z-post-activation-xrpl-ledger-market-update.json"
)


def test_post_activation_addendum_confirms_fix_without_claiming_lending_activation() -> None:
    data = json.loads(POST_ACTIVATION_ADDENDUM.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "post_activation_xrpl_protocol_state_and_market_microstructure_update"
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(data["data_cutoff_utc"])
    sources = {item["id"] for item in data["source_registry"]}
    assert len(sources) == len(data["source_registry"])
    fix = data["protocol_status"]["fixCleanup3_4_0"]
    assert fix["status"] == "ENABLED"
    assert fix["enablement_ledger"] == 108112129
    assert fix["enablement_utc"] == "2026-11-04T14:52:00Z"
    assert fix["amendment_id"] == "98433DD001A5737F773D74F8CA2A25A065089C73B2E611C760BAF369E4FECA76"
    assert fix["enable_amendment_transaction_hash"] == "F2E0342BC2419508DBAB9E869B7057941A07782426167396F87C7D0CA008FA6C"
    assert {"xrpldashboard_amendments_live_20261104T2240Z", "xrplwin_fixcleanup3_4_0_live_20261104T2240Z"} <= sources
    lending = data["protocol_status"]["native_lending"]
    assert lending["status"] == "NOT_ACTIVE"
    assert lending["required_yes_votes"] == 29
    assert lending["yes_votes"] == {"SingleAssetVault": 21, "LendingProtocol": 19, "LendingProtocolV1_1": 19}
    assert lending["activation_countdown_active"] is False
    assert data["predictions"]["issued"] is False
    assert all(item["model_eligible"] is False for item in data["source_registry"])


def test_post_activation_market_snapshot_preserves_timestamp_and_scope_disagreement() -> None:
    data = json.loads(POST_ACTIVATION_ADDENDUM.read_text(encoding="utf-8"))
    market = data["market_snapshot"]
    assert market["currency_pair"] == "XRP/USD"
    assert market["venue"] == "Kraken"
    assert market["best_bid_usd"] == 1.31376
    assert market["best_ask_usd"] == 1.31387
    assert market["last_trade_usd"] == 1.31352
    assert market["spread_bps"] == 0.8373
    assert market["volume_24h_xrp"] == 41189420.05610191
    assert market["vwap_24h_usd"] == 1.29201409
    assert market["utc_daily_open_usd"] == 1.27513
    assert market["provider_event_timestamp_utc"] is None
    assert market["dashboard_quote"]["price_usd"] == 1.3076
    assert "Do not average" in market["comparison_policy"]
    quality = data["data_quality"]["dashboard_current_ledger_indicator_disagreement"]
    assert quality["header_ledger"] == 108118734
    assert quality["body_validated_ledger_at_fetch"] == 108118715
    assert data["preservation"]["raw_source_bytes_archived"] is False
    assert data["preservation"]["immutable_raw_receipts_created"] is False


CIRCLE_SEC_RIPPLE_OCC_CORRECTION = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T230254Z-circle-sec-ripple-occ-primary-source-correction.json"
)


def test_circle_sec_and_ripple_occ_primary_source_correction_preserves_measure_scope() -> None:
    data = json.loads(CIRCLE_SEC_RIPPLE_OCC_CORRECTION.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "circle_q3_sec_and_ripple_occ_effective_status_primary_source_correction"
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(data["data_cutoff_utc"])
    sources = {item["id"]: item for item in data["source_registry"]}
    assert len(sources) == len(data["source_registry"])
    sec = sources["sec_circle_q3_2026_ex99_1_direct"]
    assert "000187604226000309/finalq3epr-110326.htm" in sec["url"]
    assert sec["filing_index_status"] == "DIRECT_EXHIBIT_URL_RESOLVED; FILING_INDEX_PAGE_NOT_INDEPENDENTLY_RETRIEVED"
    assert sec["raw_content_sha256"] is None
    assert sec["model_eligible"] is False

    circle = data["circle_q3_metrics"]
    assert circle["average_usdc_circulation_usd_bn"] == 73.3
    assert circle["end_period_usdc_circulation_usd_bn"] == 73.9
    assert circle["end_period_usdc_circulation_yoy_pct"] == 0
    assert circle["reserve_income_yoy_pct"] == -8
    assert circle["other_revenue_yoy_pct"] == 627
    assert circle["arc_token_presale_revenue_usd_mn"] == 182
    assert circle["usdc_minted_gross_usd_bn"] == 104
    assert circle["usdc_redeemed_gross_usd_bn"] == 104
    assert circle["usdc_onchain_transaction_volume_usd_trn"] == 13.9
    assert circle["usdc_on_platform_end_period_usd_bn"] == 13.9
    assert circle["binance_equity_investment"]["status"].startswith("ANNOUNCED_IN_CIRCLE_EXHIBIT")

    occ = sources["occ_cas_ripple_national_trust_bank"]
    assert occ["source_independence_group"] == "occ_primary_regulator"
    rntb = data["ripple_rntb_status"]
    assert rntb["occ_approved_date"] == "2025-12-12"
    assert rntb["occ_consummated_effective_date"] == "2026-10-26"
    assert rntb["rlusd_issuer"] == "Standard Custody & Trust Company, LLC"
    assert "NOT_ESTABLISHED" in rntb["operational_status"]

    assert data["correction_overlay"]["prior_artifact_modified"] is False
    assert data["predictions"]["issued"] is False
    assert data["data_quality"]["model_eligible"] is False
    assert all(item["model_eligible"] is False for item in sources.values())
    source_ids = set(sources)
    for item in data["findings"]:
        assert set(item["evidence"]) <= source_ids
    for edge in data["relationship_graph"]:
        assert set(edge["evidence"]) <= source_ids


CIRCLE_BINANCE_8K_CLOSE_VERIFICATION = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T230818Z-binance-circle-private-placement-close-verification.json"
)


def test_binance_circle_private_placement_is_verified_actual_equity_not_xrp_flow() -> None:
    data = json.loads(CIRCLE_BINANCE_8K_CLOSE_VERIFICATION.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "circle_binance_actual_equity_capital_and_usdc_commercial_agreement_verification"
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(data["data_cutoff_utc"])
    sources = {item["id"]: item for item in data["source_registry"]}
    assert len(sources) == 3
    sec = sources["sec_circle_binance_private_placement_8k"]
    assert "/000187604226000276/crcl-20260917.htm" in sec["url"]
    assert sec["raw_content_sha256"] is None
    assert sec["model_eligible"] is False
    capital = data["capital_flow"]
    assert capital["shares_issued"] == 1237011
    assert capital["price_per_share_usd"] == 80.84
    assert capital["gross_proceeds_usd"] == 100000000
    assert capital["event_date"] == "2026-09-17"
    assert capital["closing_status"] == "CLOSED_PER_CIRCLE_FORM_8K"
    assert capital["reciprocal_commercial_arrangement"]["term_years"] == 5
    assert "monthly incentive fee" in capital["reciprocal_commercial_arrangement"]["circle_payment_to_binance"].lower()
    assert capital["xrp_implication"] == "NONE_ESTABLISHED"
    assert data["correction_overlay"]["prior_artifact_modified"] is False
    assert data["predictions"]["issued"] is False
    assert data["data_quality"]["model_eligible"] is False
    assert all(item["model_eligible"] is False for item in sources.values())
    source_ids = set(sources)
    for item in data["findings"]:
        assert set(item["evidence"]) <= source_ids
    for edge in data["relationship_graph"]:
        assert set(edge["evidence"]) <= source_ids


SBI_JPYSC_EREBOR_UPDATE = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261104T231520Z-sbi-jpysc-erebor-institutional-rail-update.json"
)


def test_sbi_jpysc_and_erebor_update_preserves_offchain_and_planned_capital_scope() -> None:
    data = json.loads(SBI_JPYSC_EREBOR_UPDATE.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "sbi_current_stablecoin_liquidity_and_institutional_capital_relationship_update"
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(data["data_cutoff_utc"])
    sources = {item["id"]: item for item in data["source_registry"]}
    assert len(sources) == 9
    jpysc = data["dated_metrics"]["jpysc_as_of_2026_11_02"]
    assert jpysc["handling_balance_jpy_bn_gt"] == 30
    assert jpysc["lending_balance_jpy_bn_gt"] == 10
    assert "not independently verified public-chain supply" in jpysc["measurement_type"]
    erebor = data["dated_metrics"]["erebor"]
    assert erebor["planned_sbi_investment_usd_mn"] == 100
    assert erebor["planned_investment_status"] == "ANNOUNCED_NOT_CLOSED_OR_FUNDED"
    assert erebor["occ_effective_date"] == "2026-02-06"
    assert erebor["fdic_certificate"] == "59378"
    assert "SBI Shinsei Trust Bank" in data["relationship_graph"][1]["from"] or any(
        edge["from"] == "SBI Shinsei Trust Bank" and edge["to"] == "JPYSC"
        for edge in data["relationship_graph"]
    )
    open_standard = next(edge for edge in data["relationship_graph"] if edge["to"] == "Open Standard")
    assert open_standard["status"] == "MEMBERSHIP_AND_POC_PROPOSAL"
    assert "Do not infer direct SBI-Coinbase agreement" in open_standard["xrp_implication"]
    assert data["predictions"]["issued"] is False
    assert data["data_quality"]["model_eligible"] is False
    assert all(item["model_eligible"] is False for item in sources.values())
    source_ids = set(sources)
    for edge in data["relationship_graph"]:
        assert set(edge["evidence"]) <= source_ids


EVERNORTH_ELOC_DOLLAR_CAP_CORRECTION = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T043450Z-evernorth-eloc-dollar-cap-correction.json"
)


def test_evernorth_eloc_correction_uses_share_limit_not_fixed_usd_cap() -> None:
    data = json.loads(EVERNORTH_ELOC_DOLLAR_CAP_CORRECTION.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_evernorth_eloc_dollar_cap_correction_overlay"
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(data["data_cutoff_utc"])

    sources = {item["id"]: item for item in data["source_registry"]}
    assert len(sources) == 3
    sec = sources["sec_evernorth_20261030_424b3"]
    assert "xrpn-20261030.htm" in sec["url"]
    assert sec["raw_content_sha256"] is None
    assert sec["model_eligible"] is False

    correction = data["prior_artifact_correction"]
    assert correction["prior_value_usd"] == 76800000
    assert correction["prior_artifact_modified"] is False
    assert correction["disposition"] == "SUPERSEDED_AS_UNSUPPORTED_FIXED_OR_MAXIMUM_DOLLAR_AMOUNT"

    terms = data["verified_contract_terms"]
    assert terms["maximum_new_shares"] == 5218935
    assert terms["maximum_share_fraction_percent"] == 19.99
    assert terms["purchase_price_percent_of_applicable_vwap"] == 97
    assert terms["issuer_has_obligation_to_draw"] is False
    assert terms["fixed_usd_cap_disclosed"] is False
    assert terms["proceeds_received_as_of_prospectus_usd"] == 0
    assert terms["upfront_commitment_fee_usd"] == 521893.5
    assert "non-refundable" in terms["fee_status"].lower()

    capital = data["capital_reconciliation"]
    assert capital["closing_gross_cash_proceeds_usd"] == 272600000
    assert capital["closing_cash_components"]["private_placement_investments_usd"] == 224600000
    assert capital["closing_cash_components"]["released_spac_trust_usd"] == 48000000
    cash_purchase = capital["historical_cash_xrp_purchase"]
    assert cash_purchase["cash_received_under_advance_funding_subscriptions_usd"] == 214050000
    assert cash_purchase["xrp_purchased_units"] == 84365876.3625
    assert cash_purchase["purchase_announcement_date"] == "2025-11-04"
    assert cash_purchase["classification"] == "HISTORICAL_ACTUAL_CASH_XRP_PURCHASE_NOT_A_NOVEMBER_2026_FLOW"
    assert capital["in_kind_xrp_contributions_units"] == 388910554
    assert capital["convertible_notes"]["principal_usd"] == 30000000
    assert capital["convertible_notes"]["actual_xrp_purchases_from_note_proceeds_disclosed"] is False
    assert capital["ripple_related_party_facility"]["drawn_as_of_2026_10_07_usd"] == 9700000
    assert capital["ripple_related_party_facility"]["repayment_status_in_prospectus"] == "NOT_CONFIRMED"
    assert capital["cantor_eloc"]["proceeds_received_as_of_prospectus_usd"] == 0
    assert capital["resale_registration"]["company_receives_resale_proceeds"] is False

    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["issued"] is False
    assert all(item["model_eligible"] is False for item in sources.values())


EVERNORTH_ELOC_SOURCE_PRICE_ADDENDUM = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T043450Z-evernorth-eloc-source-and-reference-price-addendum.json"
)


def test_evernorth_eloc_source_type_and_reference_price_scenario_are_qualified() -> None:
    data = json.loads(EVERNORTH_ELOC_SOURCE_PRICE_ADDENDUM.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_evernorth_eloc_source_and_reference_price_addendum"

    sources = {item["id"]: item for item in data["source_registry"]}
    sec = sources["sec_evernorth_20261030_s1_preliminary_prospectus"]
    assert sec["source_type"] == "SEC Form S-1 registration statement; preliminary prospectus subject to completion"
    assert sec["raw_source_sha256"] is None
    assert sec["model_eligible"] is False

    source_correction = data["source_and_claim_corrections"]["source_type_correction"]
    assert source_correction["prior_artifact_source_type"] == "SEC Form 424B3"
    assert source_correction["corrected_source_type"].startswith("SEC Form S-1")
    assert source_correction["prior_artifacts_modified"] is False

    terms = data["verified_eloc_contract_terms"]
    assert terms["maximum_new_class_a_shares"] == 5218935
    assert terms["issuer_has_obligation_to_sell"] is False
    assert terms["purchase_price_percent_of_applicable_vwap"] == 97
    assert terms["proceeds_received_as_of_prospectus_usd"] == 0
    assert terms["fee_payment_status"] == "NOT_VERIFIED_AS_PAID"

    scenario = data["illustrative_reference_price_scenario"]
    assert scenario["reference_date"] == "2026-10-29"
    assert scenario["reference_class_a_closing_price_usd"] == 14.71
    assert scenario["nominal_gross_at_reference_close_usd"] == 76770533.85
    assert scenario["illustrative_purchase_proceeds_at_97_percent_usd"] == 74467417.8345
    assert scenario["illustrative_amount_after_fee_if_fee_paid_usd"] == 73945524.3345
    assert scenario["status"] == "SCENARIO_ONLY_NOT_ACTUAL_PROCEEDS"
    assert any("not net proceeds" in item.lower() for item in scenario["caveats"])

    offering = data["offering_scope_reconciliation"]
    assert offering["resale_registration"]["registered_class_a_shares"] == 73688162
    assert offering["resale_registration"]["company_receives_proceeds_from_selling_securityholders"] is False
    assert offering["sponsor_warrants"]["registered_warrants"] == 239653
    assert offering["sponsor_warrants"]["proceeds_received_or_exercises_verified"] is False
    assert offering["eloc_primary_sales"]["proceeds_received_as_of_prospectus_usd"] == 0

    capital = data["capital_taxonomy"]
    assert capital["closing_gross_cash_proceeds_usd"] == 272600000
    assert capital["historical_cash_xrp_purchase"]["cash_used_usd"] == 214050000
    assert capital["historical_cash_xrp_purchase"]["purchase_date"] == "2025-11-04"
    assert capital["in_kind_xrp_contributions_units"] == 388910554
    assert capital["convertible_notes"]["principal_usd"] == 30000000
    assert capital["convertible_notes"]["xrp_purchases_funded_by_notes_disclosed"] is False
    assert capital["company_facility_with_ripple"]["borrower"] == "The Company"
    assert capital["company_facility_with_ripple"]["drawn_as_of_2026_10_07_usd"] == 9700000
    assert capital["company_facility_with_ripple"]["repayment_status_in_prospectus"] == "NOT_CONFIRMED"
    assert capital["eloc"]["proceeds_received_as_of_prospectus_usd"] == 0
    assert capital["eloc_fee"]["payment_status"] == "NOT_VERIFIED_AS_PAID"

    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["issued"] is False
    assert all(item["model_eligible"] is False for item in sources.values())


EVERNORTH_NOTES_AND_FACILITY_CORRECTION = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T043450Z-evernorth-notes-and-facility-scope-correction.json"
)


def test_evernorth_note_proceeds_and_ripple_facilities_remain_separate() -> None:
    data = json.loads(EVERNORTH_NOTES_AND_FACILITY_CORRECTION.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_evernorth_notes_and_facility_scope_correction"

    sources = {item["id"]: item for item in data["source_registry"]}
    sec = sources["sec_evernorth_20261030_s1_preliminary_prospectus"]
    assert sec["source_type"] == "SEC Form S-1 registration statement; preliminary prospectus subject to completion"
    assert sec["raw_source_sha256"] is None
    assert sec["model_eligible"] is False

    notes = data["convertible_note_reconciliation"]
    assert notes["principal_usd"] == 30000000
    assert notes["narrative_disclosure"]["amount_usd"] == 30000000
    assert "before transaction expenses" in notes["narrative_disclosure"]["basis"]
    assert notes["financial_statement_note"]["cash_proceeds_after_advisor_fee_usd"] == 29000000
    assert notes["financial_statement_note"]["advisor_fee_deducted_usd"] == 1000000
    assert notes["reconciliation_status"] == "DISTINCT_MEASUREMENT_BASES_RECONCILED"
    assert notes["xrp_purchases_funded_by_note_proceeds_disclosed"] is False

    facilities = data["facility_scope_reconciliation"]
    company = facilities["company_facility_with_ripple"]
    evernorth = facilities["evernorth_facility"]
    assert company["borrower"] == "The Company"
    assert company["borrowing_limit_as_of_2026_10_07_usd"] == 10000000
    assert company["drawn_as_of_2026_10_07_usd"] == 9700000
    assert company["repayment_status_in_prospectus"] == "NOT_CONFIRMED"
    assert evernorth["borrower"] == "Evernorth"
    assert evernorth["revolving_limit_usd"] == 1000000
    assert evernorth["amount_borrowed_as_of_2026_06_30_usd"] == 0
    assert company["borrower"] != evernorth["borrower"]

    cash = data["cash_and_xrp_reconciliation"]
    historical = cash["historical_cash_xrp_purchase"]
    assert historical["cash_proceeds_usd"] == 214100000
    assert historical["xrp_purchased_units"] == 84365876
    assert historical["date"] == "2025-11-04"
    assert historical["classification"] == "HISTORICAL_CASH_FUNDED_XRP_PURCHASE_NOT_A_2026_CURRENT_FLOW"
    assert cash["closing_gross_cash_proceeds_usd"] == 272600000
    assert cash["in_kind_xrp_contributions_units"] == 388910554
    assert cash["note_funded_xrp_purchase_disclosed"] is False

    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["issued"] is False

RUN131B = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261110T141058Z-run131b-coinbase-occ-pnc-cbxrp-market-update.json"
)


def test_run131b_evidence_graph_and_platform_map_are_resolvable() -> None:
    data = json.loads(RUN131B.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_coinbase_circle_pnc_occ_cbxrp_market_reconciliation"
    assert _parse_utc(data["captured_at_utc"]) >= _parse_utc(data["data_cutoff_utc"])
    sources = {item["id"] for item in data["source_registry"]}
    assert len(sources) == len(data["source_registry"])
    observation_ids = [item["id"] for item in data["observations"]]
    assert len(observation_ids) == len(set(observation_ids))
    for item in data["observations"]:
        assert item["classification"] and item["claim"]
        assert item["evidence"]
        assert set(item["evidence"]) <= sources
    for edge in data["relationship_graph"]:
        assert edge["from"] and edge["to"] and edge["relation"]
        assert set(edge["evidence"]) <= sources
    for hypothesis in data["competing_hypotheses"]:
        assert hypothesis["claim"] and hypothesis["support"]
        assert hypothesis["disconfirming_or_missing"] and hypothesis["tests"]
    platforms = data["platform_map"]
    assert len(platforms) == 9
    assert {item["platform"] for item in platforms} == {
        "ChatGPT", "Claude", "Grok", "Gemini", "Copilot",
        "Codex", "Hugging Face", "Kaggle", "Databricks",
    }
    assert next(item for item in platforms if item["platform"] == "ChatGPT")[
        "status"
    ] == "tested_current_runtime"
    assert data["agent_exchange_contract"]["disagreement_policy"]
    assert data["agent_exchange_contract"]["least_privilege_policy"]
    assert data["agent_exchange_contract"]["adapter_status"].startswith(
        "Architecture designed"
    )
    assert data["predictions"]["issued"] is False
    assert data["predictions"]["status"] == "NOT_ISSUED"


def test_run131b_cbxrp_collateral_snapshot_is_reconciled_but_not_model_admitted() -> None:
    data = json.loads(RUN131B.read_text(encoding="utf-8"))
    market = data["market_snapshot"]["morpho_cbxrp_usdc"]
    assert _parse_utc(market["source_timestamp_utc"]) <= _parse_utc(
        data["data_cutoff_utc"]
    )
    assert market["market_id"].startswith("0xd4a903dc")
    assert market["supplied_usdc_usd_millions"] == 62.93
    assert market["borrowed_usdc_usd_millions"] == 55.37
    assert market["utilization_pct"] == 88.0
    assert market["collateral_cbxrp_millions"] == 120.40
    assert market["lltv_pct"] == 62.5
    assert market["liquidations_last_30d"] == 1479
    assert market["model_eligible"] is False
    assert data["market_snapshot"]["indicative_cbxrp_collateral_share"][
        "model_eligible"
    ] is False
    spot = data["market_snapshot"]["spot_quality"]
    assert spot["okx_age_at_capture_seconds"] > 300
    assert spot["okx_model_eligible"] is False
    assert spot["kraken_provider_timestamp"] is None
    assert spot["kraken_model_eligible"] is False
    assert data["market_snapshot"]["etf_flows"]["model_eligible"] is False
    assert data["source_capture"]["raw_wire_bytes_available"] is False
    assert data["source_capture"]["raw_source_sha256_receipts_created"] is False


def test_run131b_coinbase_circle_and_pnc_relationships_are_scope_limited() -> None:
    data = json.loads(RUN131B.read_text(encoding="utf-8"))
    observations = {item["id"]: item for item in data["observations"]}
    occ = observations["OBS-COINBASE-OCC-20261106"]
    pnc = observations["OBS-PNC-USDC-PILOT-20261109"]
    distribution = observations["OBS-CIRCLE-COINBASE-DISTRIBUTION-COSTS"]
    assert set(occ["evidence"]) == {
        "coinbase_occ_final_approval", "occ_coinbase_cas_record"
    }
    assert "no XRP" in " ".join(pnc["limitations"])
    assert "331.3M" in distribution["claim"]
    assert "986.6M" in distribution["claim"]
    assert data["market_snapshot"]["coinbase_business"][
        "average_usdc_held_usd_billions"
    ] == 22
    assert data["market_snapshot"]["circle_business"][
        "average_usdc_circulation_usd_billions"
    ] == 73.3
    assert data["predictions"]["issued"] is False


# Run131B append-only correction and Circle network expansion checks.

RUN131B_CORRECTION = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261110T141651Z-run131b-cbxrp-address-circle-network-correction.json"
)


def test_run131b_morpho_collateral_token_correction_is_append_only_and_exact() -> None:
    data = json.loads(RUN131B_CORRECTION.read_text(encoding="utf-8"))
    assert data["corrects_artifact"].endswith(
        "20261110T141058Z-run131b-coinbase-occ-pnc-cbxrp-market-update.json"
    )
    correction = data["corrections"][0]
    assert correction["field"] == "market_snapshot.morpho_cbxrp_usdc.collateral_token"
    assert correction["original_value"] == (
        "0xcb585250f852b6e08f4c7c32d4f71b54bda02913"
    )
    assert correction["corrected_value"] == (
        "0xcb585250f852b6c6bf90434ab21a00f02833a4af"
    )
    identity = data["corrected_market_identity"]
    assert identity["loan_token"] == (
        "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
    )
    assert identity["collateral_token"] == correction["corrected_value"]
    assert identity["oracle"] == (
        "0x031b2efc8d70042ac8d9f5c793c4149ec4b60fde"
    )
    assert identity["chain_id"] == 8453
    assert data["corrections"][0]["model_eligible"] is False
    assert data["model_admission"]["predictions_issued"] is False


def test_run131b_circle_network_expansion_is_not_misclassified_as_xrp_capital() -> None:
    data = json.loads(RUN131B_CORRECTION.read_text(encoding="utf-8"))
    circle = data["circle_network_expansion"]
    assert circle["cpn_annualized_tpv_usd_billions"] == 41.3
    assert circle["tazapay_acquisition"]["status"] == (
        "definitive_agreement_signed_pending_regulatory_approvals"
    )
    assert circle["tazapay_acquisition"]["expected_close_year"] == 2027
    assert circle["tazapay_acquisition"]["model_eligible"] is False
    assert circle["visa_direct_usdc_prefunding"]["status"] == (
        "commercial_deployment_announced"
    )
    assert circle["arc_mainnet"]["native_asset_integration"] == "USDC"
    assert all(
        item["model_eligible"] is False
        for key, item in circle.items()
        if isinstance(item, dict) and "model_eligible" in item
    )
    assert data["prediction_boundary"]["issued"] is False
    assert all(
        item["limitations"]
        for item in data["additional_observations"]
    )


def test_run60_evidence_keeps_unreceipted_observations_and_identity_candidates_quarantined() -> None:
    run60_path = (
        REPO_ROOT
        / "research"
        / "xrp_intelligence"
        / "20261112T140946Z-run60-exact-head-ci-market-x402-institutional-and-repository-audit.json"
    )
    run60 = json.loads(run60_path.read_text(encoding="utf-8"))

    assert run60["forecast_status"] == "NOT_ISSUED"
    assert all(
        observation.get("raw_receipt_sha256") is None
        and observation.get("model_eligible") is False
        for observation in run60["observations"]
    )

    identity = run60["kamilah_identity_reconciliation"]
    assert identity["person_identity_status"] == "CONFIRMED"
    assert identity["channel_identity_status"] == "PROBABLE_MATCH_NOT_FIRST_PARTY_VERIFIED"
    assert identity["candidate_reference_count"] == 21
    assert identity["verified_personal_channel_upload_count"] == 0
    assert identity["inventory_complete"] is False

    older = json.loads(
        (
            REPO_ROOT
            / "research"
            / "xrp_intelligence"
            / "20261108T041850Z-kamilah-channel-identity-and-public-video-inventory.json"
        ).read_text(encoding="utf-8")
    )
    assert older["identity_resolution"]["person_to_channel_match_status"] == (
        "STRONGLY_CORROBORATED_NOT_CONCLUSIVE"
    )
    assert older["inventory_summary"]["direct_watch_page_upload_metadata_verified_count"] == 0
    assert older["inventory_summary"]["inventory_complete"] is False

    profile = json.loads(
        (
            REPO_ROOT
            / "data"
            / "xrp_intelligence"
            / "sources"
            / "kamilah_stevenson_channel.json"
        ).read_text(encoding="utf-8")
    )
    assert profile["video_inventory_status"]["verified_inventory_count"] == 0
    assert all(
        video["eligible_for_forecast_feature"] is False
        for video in profile["seed_videos"]
    )
