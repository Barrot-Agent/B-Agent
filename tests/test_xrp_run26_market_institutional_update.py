import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261111T135621Z-run26-market-etf-stablecoin-and-institutional-network-update.json"
)


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None
    return parsed.astimezone(timezone.utc)


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_run26_artifact_has_point_in_time_cutoff_and_provenance() -> None:
    data = _load()
    assert data["artifact_type"] == "xrp_market_etf_stablecoin_and_institutional_network_update"
    assert data["repository"] == "Barrot-Agent/B-Agent"
    assert _utc(data["captured_at_utc"]) >= _utc(data["data_cutoff_utc"])
    assert _utc(data["market_snapshot"]["observed_at_utc"]) <= _utc(data["data_cutoff_utc"])
    source_ids = [item["id"] for item in data["source_registry"]]
    assert len(source_ids) == len(set(source_ids))
    known = set(source_ids)
    for observation in data["observations"]:
        assert observation["id"] and observation["class"] and observation["claim"]
        assert set(observation["evidence"]) <= known
    for edge in data["relationship_graph"]:
        assert edge["from"] and edge["to"] and edge["relation"] and edge["status"]
        assert set(edge["evidence"]) <= known
    for hypothesis in data["competing_hypotheses"]:
        assert hypothesis["claim"] and hypothesis["support"]
        assert hypothesis["disconfirming_or_missing"] and hypothesis["tests"]
        assert set(hypothesis["evidence"]) <= known


def test_run26_does_not_conflate_derivatives_mark_prices_with_spot() -> None:
    data = _load()
    market = data["market_snapshot"]
    assert market["direct_spot"]["status"] == "NOT_SYNCHRONIZED"
    assert market["direct_spot"]["price_usd"] is None
    assert len(market["derivatives"]) == 2
    assert all(item["model_eligible"] is False for item in market["derivatives"])
    assert "do not add" in market["derivatives"][1]["caveat"].lower()
    assert market["order_book"]["status"] == "NO_ELIGIBLE_SYNCHRONIZED_SPOT_DEPTH"


def test_run26_preserves_etf_provider_windows_without_averaging() -> None:
    data = _load()
    rows = data["etf_flows"]["observations"]
    assert [row["source_id"] for row in rows] == [
        "alpha_etf", "theblock_etf", "xrp_insights"
    ]
    assert rows[0]["net_flow_usd"] == -7_600_000
    assert rows[1]["net_flow_usd"] == -10_400_000
    assert rows[1]["window"].startswith("24-hour")
    assert rows[2]["nov10_row_status"] == "PROVISIONAL_PENDING_RE_SETTLEMENT"
    assert "Do not average" in data["etf_flows"]["reconciliation"]


def test_run26_coinbase_circle_ripple_sbi_edges_keep_scope_limits() -> None:
    data = _load()
    ids = {edge["id"] for edge in data["stablecoin_and_institutional_relationships"]["relationships"]}
    assert "coinbase-pnc-usdc-pilot" in ids
    assert "coinbase-circle-usdc-governance-and-economics" in ids
    assert "coinbase-ripple-rlusd-distribution" in ids
    assert "sbi-vc-trade-ripple-rlusd-distribution" in ids
    assert "circle-usdc-xrpl" in ids
    assert "circle-ripple-direct-partnership" in ids
    not_established = next(
        edge for edge in data["stablecoin_and_institutional_relationships"]["relationships"]
        if edge["id"] == "circle-ripple-direct-partnership"
    )
    assert not_established["status"] == "NOT_ESTABLISHED"
    assert any(edge["from"] == "PNC" and edge["to"] == "Circle" and edge["status"] == "inference"
               for edge in data["relationship_graph"])
    sbi = next(
        edge for edge in data["stablecoin_and_institutional_relationships"]["relationships"]
        if edge["id"] == "sbi-vc-trade-ripple-rlusd-distribution"
    )
    assert any("Ethereum as current" in item for item in sbi["limitations"])
    assert any("XRPL is future" in item for item in sbi["limitations"])


def test_run26_competing_hypotheses_preserve_counterevidence_without_probabilities() -> None:
    data = _load()
    assert len(data["competing_hypotheses"]) >= 4
    for hypothesis in data["competing_hypotheses"]:
        assert hypothesis["disconfirming_or_missing"]
        assert hypothesis["tests"]
        assert "probability" not in hypothesis
        assert "direction" not in hypothesis
    assert data["predictions"]["issued"] is False
    assert data["predictions"]["status"] == "NOT_ISSUED"
    assert data["model_eligibility"]["status"] == "EXCLUDED"
    assert data["model_eligibility"]["raw_receipts_created"] is False
    assert data["model_eligibility"]["feature_store_admission"] is False


def test_run26_nine_platform_map_does_not_overstate_unverified_connections() -> None:
    data = _load()
    platforms = data["platform_map"]
    names = {item["platform"] for item in platforms}
    assert names == {
        "ChatGPT", "Claude", "Grok", "Gemini", "Copilot",
        "Codex", "Hugging Face", "Kaggle", "Databricks"
    }
    assert len(platforms) == 9
    assert next(item for item in platforms if item["platform"] == "ChatGPT")[
        "status"
    ] == "tested_current_runtime"
    for item in platforms:
        if item["platform"] != "ChatGPT":
            assert item["status"] in {"not_tested", "workflow_reference_only"}
            assert "no live" in item["data_flow"].lower() or "no live" in item["authentication"].lower()
    assert data["brain_endpoint"]["status"] == "REPOSITORY_DECLARED_ONLY"
    assert data["safety"]["no_external_model_transfer"] is True
