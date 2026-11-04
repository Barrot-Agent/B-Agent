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
