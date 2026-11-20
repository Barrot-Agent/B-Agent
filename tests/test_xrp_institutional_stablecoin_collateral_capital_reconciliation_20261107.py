from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T171515Z-xrp-institutional-stablecoin-collateral-capital-reconciliation.json"
)
CORRECTION = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T171515Z-coinbase-stablecoin-revenue-excerpt-hash-correction.json"
)


@pytest.fixture(scope="module")
def evidence() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _source(evidence: dict, source_id: str) -> dict:
    return next(item for item in evidence["sources"] if item["source_id"] == source_id)


def test_all_normalized_source_excerpt_hashes_reproduce(evidence: dict) -> None:
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    for source in evidence["sources"]:
        digest = hashlib.sha256(source["normalized_excerpt"].encode("utf-8")).hexdigest()
        if source["source_id"] == correction["supersedes_source_id"]:
            assert source["normalized_excerpt_sha256"] == correction["incorrect_prior_sha256"]
            assert digest == correction["corrected_sha256"]
        else:
            assert digest == source["normalized_excerpt_sha256"]


def test_circle_coinbase_distribution_costs_and_supply_are_separate_metrics(evidence: dict) -> None:
    r = evidence["reconciliations"]["circle_coinbase"]
    assert any("$331.3M Q3" in x for x in r["confirmed"])
    assert any("$986.6M nine-month" in x for x in r["confirmed"])
    assert any("$73.879B" in x for x in r["confirmed"])
    assert any("$13.868B" in x for x in r["confirmed"])
    assert any("$306.905M" in x for x in r["confirmed"])
    assert any("cannot be directly netted" in x for x in r["not_established"])


def test_coinbase_collateral_is_not_mislabeled_as_xrp_collateral(evidence: dict) -> None:
    r = evidence["reconciliations"]["coinbase_collateral"]
    assert any("$1.009297B" in x for x in r["confirmed"])
    assert any("$3.284562B" in x for x in r["confirmed"])
    assert any("no xrp-specific collateral balance" in x.lower() for x in r["confirmed"])
    assert any("No public XRP collateral utilization amount" in x for x in r["not_established"])


def test_sbi_q2_segment_results_are_not_attributed_to_xrp(evidence: dict) -> None:
    s = _source(evidence, "sbi_holdings_q2_fy2027_interim_results")
    assert "Crypto-asset Business revenue ¥23,083 million (-30.1%)" in s["normalized_excerpt"]
    assert "loss before tax ¥1,595 million" in s["normalized_excerpt"]
    assert "PE Investment Business revenue ¥181,283 million (+28.5%)" in s["normalized_excerpt"]
    assert any("not XRP-specific" in x for x in s["limitations"])
    assert "no Ripple or XRP matches" in evidence["reconciliations"]["sbi_multi_rail"]["not_established"][-1]


def test_jpysc_balance_lending_and_risk_disclosures_are_preserved(evidence: dict) -> None:
    s = _source(evidence, "sbi_vc_trade_jpysc_nov2_balance_and_lending")
    assert "¥10 billion" in s["normalized_excerpt"]
    assert "¥30 billion" in s["normalized_excerpt"]
    assert "168 days at 3%" in s["normalized_excerpt"]
    assert any("not a bank deposit" in x for x in s["limitations"])
    assert any("not a current public-chain liquidity metric" in x for x in s["limitations"])


def test_smfg_and_open_standard_links_remain_exploratory(evidence: dict) -> None:
    smfg = _source(evidence, "sbi_smfg_stablecoin_alliance")
    standard = _source(evidence, "sbi_startale_open_standard")
    assert "5% equity interest" in smfg["normalized_excerpt"]
    assert "proof-of-concept work, not a launched production service" in smfg["normalized_excerpt"]
    assert "Coinbase" in standard["normalized_excerpt"]
    assert "does not mean a new service or production settlement" in standard["normalized_excerpt"]
    assert any("not evidence of a direct Coinbase-SBI XRP partnership" in x for x in standard["limitations"])


def test_rlusd_jpysc_issuer_and_distribution_roles_are_not_conflated(evidence: dict) -> None:
    rlusd = _source(evidence, "sbi_vc_trade_rlusd_launch")
    jpysc = _source(evidence, "sbi_jpysc_issuance_roles")
    assert "Type 4 electronic payment instrument" in rlusd["normalized_excerpt"]
    assert "not a trust beneficial interest under US law" in rlusd["normalized_excerpt"]
    assert "SBI Shinsei Trust Bank was named issuer of JPYSC" in jpysc["normalized_excerpt"]
    assert "Startale Group co-developed it" in jpysc["normalized_excerpt"]
    assert any("not an XRP purchase" in x for x in rlusd["limitations"])


def test_japan_sbic_east_central_west_are_distinct_from_sbi_holdings(evidence: dict) -> None:
    r = evidence["reconciliations"]["sbic_identity"]
    assert r["resolved"] is True
    assert r["not_sbi_holdings"] is True
    assert len(r["entities"]) == 3
    assert "Act No. 101 of 1963" in r["statutory_context"]
    assert _source(evidence, "sbic_east_identity")["normalized_excerpt"].startswith("Tokyo Small")
    assert "SBIC Central Japan" in _source(evidence, "sbic_central_identity")["normalized_excerpt"]
    assert "SBIC West Japan" in _source(evidence, "sbic_west_identity")["normalized_excerpt"]


def test_sbic_chatgpt_training_is_not_misrepresented_as_a_partnership(evidence: dict) -> None:
    s = _source(evidence, "sbic_chatgpt_training_context")
    assert "ChatGPT usage" in s["normalized_excerpt"]
    assert "not evidence of an OpenAI partnership" in s["normalized_excerpt"]
    assert evidence["reconciliations"]["sbic_identity"]["chatgpt_context"].endswith("authenticated SBIC-ChatGPT integration.")


def test_exact_phrase_actual_capital_is_secondary_and_ask_is_ambiguous(evidence: dict) -> None:
    actual = _source(evidence, "evernorth_actual_capital_secondary_phrase")
    ask = _source(evidence, "ask_coin_permission_ticker_disambiguation")
    assert actual["primary_source"] is False
    assert "not completed financing" in actual["normalized_excerpt"]
    assert ask["primary_source"] is False
    assert "Permission Coin" in ask["normalized_excerpt"]
    assert "no XRP relationship" in ask["normalized_excerpt"]


def test_institutional_context_is_not_promoted_to_xrp_flow_or_forecast(evidence: dict) -> None:
    admission = evidence["model_admission"]
    assert admission["admitted_as_xrp_price_feature"] is False
    assert admission["admitted_as_xrp_flow_feature"] is False
    assert admission["admitted_as_xrp_collateral_feature"] is False
    assert admission["eligible_as_categorical_event_context"] is True
    assert evidence["forecast"]["status"] == "NOT_ISSUED"
    assert evidence["forecast"]["directional_forecast"] is False
