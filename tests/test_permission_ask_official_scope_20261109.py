from __future__ import annotations

import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261109T132519Z-permission-ask-official-token-scope.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_permission_ask_is_a_supported_candidate_not_a_confirmed_user_referent() -> None:
    data = load_artifact()
    assert data["candidate_status"] == "SUPPORTED_CANDIDATE_NOT_CONFIRMED_USER_REFERENT"
    assert data["exact_phrase_resolution"]["phrase"] == "ASK Coin"
    assert "ASK native token" in data["exact_phrase_resolution"]["finding"]


def test_official_ask_token_scope_and_networks_are_explicit() -> None:
    data = load_artifact()
    token = data["official_token_documentation"]
    assert token["token_name"] == "ASK"
    assert token["fixed_supply"] == 100_000_000_000
    assert token["token_standard"] == "LayerZero OFT (Omnichain Fungible Token)"
    assert [x["network"] for x in token["active_networks"]] == ["Base", "Polygon"]
    assert all(x["contract"].startswith("0x") for x in token["active_networks"])


def test_permission_ask_is_not_admitted_as_an_xrp_feature() -> None:
    data = load_artifact()
    relation = data["xrp_relationship"]
    assert relation["xrpl_listed_as_active_network"] is False
    assert relation["direct_xrp_or_xrpl_integration_verified"] is False
    assert data["model_eligible"] is False
    assert data["forecast_status"] == "NOT_ISSUED"


def test_actual_capital_is_not_inferred_from_token_supply_or_utility() -> None:
    data = load_artifact()
    assert data["actual_capital"]["model_feature_eligible"] is False
    assert "cash inflows" in data["actual_capital"]["finding"]
    assert data["source_independence"]["independent_publishers"] == 1


def test_official_homepage_current_positioning_is_recorded() -> None:
    data = load_artifact()
    assert data["homepage_observations"]["product_positioning"] == "Family-friendly AI; digital-wellbeing insights, boundaries and rewards."
    assert data["homepage_observations"]["rewards_partner"] == "Tremendous"
