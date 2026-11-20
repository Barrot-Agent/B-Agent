import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T044552Z-ask-coin-entity-disambiguation.json"


def test_ask_coin_phrase_keeps_exchange_and_permission_token_separate():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "xrp_exact_phrase_entity_resolution"
    assert data["mission_priority"] == 1
    assert data["model_eligible"] is False
    assert data["forecast_issued"] is False
    assert data["resolution"]["status"] == "AMBIGUOUS_EXACT_PHRASE"
    assert set(data["candidate_entities"]) == {"ask_coin_exchange", "permission_coin"}
    assert data["candidate_entities"]["ask_coin_exchange"]["website"] == "https://askcoin.net"
    assert data["candidate_entities"]["permission_coin"]["ticker"] == "ASK"
    assert data["candidate_entities"]["ask_coin_exchange"]["relationship_to_permission_coin"] == "not_established"
    assert data["candidate_entities"]["permission_coin"]["relationship_to_ask_coin_exchange"] == "not_established"


def test_ask_coin_candidates_have_no_verified_xrp_relationship():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    for candidate in data["candidate_entities"].values():
        assert candidate["relationship_to_xrp_xrpl_ripple_sbi"] == "not_established"
    assert data["competing_interpretations"][2]["status"] == "NOT_ESTABLISHED"
    assert data["forecast_issued"] is False


def test_ask_coin_source_provenance_is_secondary_and_model_ineligible():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    sources = data["source_registry"]
    assert len(sources) == 2
    assert {source["source_independence_group"] for source in sources} == {"coinmarketcap"}
    assert all(source["raw_content_sha256"] is None for source in sources)
    assert all(source["model_eligible"] is False for source in sources)
    assert data["source_capture_policy"]["raw_http_bytes_captured"] is False
    assert "not independent publishers" in data["resolution"]["source_independence"]
