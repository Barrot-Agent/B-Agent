import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261117T180321Z-run222-market-derivatives-depth-etf-regulatory-refresh.json"


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None
    return parsed.astimezone(timezone.utc)


def _load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_run222_sources_are_unique_and_no_rendered_page_is_misrepresented_as_raw():
    data = _load()
    sources = data["source_registry"]
    ids = [item["id"] for item in sources]
    assert len(ids) == len(set(ids))
    for source in sources:
        assert source["raw_source_sha256"] is None
        assert source["model_eligible"] is False
        assert "not retained" in source["raw_capture_status"].lower() or "not archived" in source["raw_capture_status"].lower()


def test_run222_observation_and_disagreement_evidence_resolves():
    data = _load()
    known = {item["id"] for item in data["source_registry"]}
    assert len(data["observations"]) >= 12
    for observation in data["observations"]:
        assert observation["id"] and observation["claim"]
        assert observation["evidence"]
        assert set(observation["evidence"]) <= known
        assert observation["model_eligible"] is False
    for disagreement in data["disagreement_register"]:
        assert disagreement["id"] and disagreement["issue"] and disagreement["resolution"]


def test_run222_cutoff_is_point_in_time_and_market_sources_keep_unknown_clocks_unknown():
    data = _load()
    cutoff = _utc(data["data_cutoff_utc"])
    captured = _utc(data["captured_at_utc"])
    assert captured >= cutoff
    for source in data["source_registry"]:
        if source.get("source_as_of_utc"):
            assert _utc(source["source_as_of_utc"]) <= cutoff
        if source.get("source_published_at_utc"):
            assert _utc(source["source_published_at_utc"]) <= captured
    investing = next(x for x in data["source_registry"] if x["id"] == "investing_xrp_daily_20261117")
    assert investing.get("source_as_of_utc") is None
    assert "timezone not stated" in investing["source_time_label"]


def test_run222_preserves_derivatives_and_etf_provider_disagreement_without_averaging():
    data = _load()
    assert data["market_snapshot"]["derivatives"]["open_interest"][0]["open_interest_usd"] != data["market_snapshot"]["derivatives"]["open_interest"][1]["open_interest_usd"]
    assert len(data["market_snapshot"]["funding"]["observations"]) == 3
    assert len(data["market_snapshot"]["etf_flows"]) == 2
    assert data["market_snapshot"]["etf_flows"][0]["status"] == "partial"
    assert data["market_snapshot"]["etf_flows"][1]["status"] == "provisional_until_settled"


def test_run222_institutional_and_regulatory_claims_retain_qualifications():
    data = _load()
    relationships = data["institutional_relationships"]
    assert any(x["from"] == "BNY" and any("No public client-level XRP balances" in y for y in x["not_established"]) for x in relationships)
    assert any(x["from"] == "Coinbase" and any("future rollout" in y for y in x["not_established"]) for x in relationships)
    assert any(x["from"] == "SBI Holdings and SBI Shinsei Bank" for x in relationships)
    sec = next(x for x in data["observations"] if x["id"] == "sec-xrp-digital-commodity-interpretation-20260317")
    assert "investment contract" in sec["counter_evidence"][0].lower()
    proposal = next(x for x in data["observations"] if x["id"] == "sec-regulation-crypto-assets-proposal-pending-20261117")
    assert proposal["status"] == "proposed_not_final"


def test_run222_forecast_and_nine_platform_gates_remain_closed():
    data = _load()
    assert data["prediction_status"]["issued"] is False
    assert data["prediction_status"]["this_run"]["raw_source_receipts"] == 0
    assert data["prediction_status"]["this_run"]["model_eligible_observations"] == 0
    platforms = data["nine_platform_map"]["platforms"]
    assert len(platforms) == 9
    assert len({x["platform"] for x in platforms}) == 9
    assert next(x for x in platforms if x["platform"] == "ChatGPT")["status"] == "tested_current_runtime"
    assert all(x["status"] != "tested_current_runtime" for x in platforms if x["platform"] != "ChatGPT")
    assert data["nine_platform_map"]["external_provider_dispatch"] is False
