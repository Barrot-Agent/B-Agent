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
    assert _parse_utc(data["captured_at_utc"]) == _parse_utc(
        data["data_cutoff_utc"]
    )
    assert _parse_utc(data["market_snapshot"]["observed_at_utc"]) <= _parse_utc(
        data["data_cutoff_utc"]
    )


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
    assert any(item["id"] == "H7-sponsored-fees-shifts-xrp-demand" for item in data["competing_hypotheses"])
    assert any(item["id"] == "H8-institutional-privacy-mpt-not-xrp" for item in data["competing_hypotheses"])
    assert any(item["id"] == "H9-gross-volume-distortion" for item in data["competing_hypotheses"])
    assert any(item["id"] == "H10-custody-is-not-xrp-demand" for item in data["competing_hypotheses"])
    assert any(item["id"] == "H11-bank-rail-adoption-throughput-unknown" for item in data["competing_hypotheses"])
    assert any(item["id"] == "H12-value-concentration-not-broad-adoption" for item in data["competing_hypotheses"])
    assert any(item["id"] == "H13-SBI-multirail-hub" for item in data["competing_hypotheses"])

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
