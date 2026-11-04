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
