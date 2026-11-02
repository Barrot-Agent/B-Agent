from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/xrp_intelligence/snapshots/20261102T001348Z-flare-fxrp-firelight-morpho-collateral-market.json"


def load_snapshot():
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def test_fxrp_native_xrp_backing_is_separate_from_agent_collateral():
    d = load_snapshot()["flareforge_independent_snapshot"]
    assert d["fxrp_supply"] == 143_995_073.5804
    assert d["native_xrp_backing"] == 144_079_041.11
    assert 1.0005 < d["native_xrp_backing_ratio"] < 1.0007
    assert d["backing_surplus_xrp"] > 80_000
    assert d["agent_pool_collateral_ratio_range"] == [2.17, 8.41]
    assert d["core_vault_escrowed_xrp"] == 140_000_000
    assert d["core_vault_liquid_xrp"] < 3_000_000
    assert d["bridge_reconciliation_passed"] is True


def test_fxrp_remote_supply_and_protocol_holder_concentration_are_explicit():
    d = load_snapshot()["flareforge_independent_snapshot"]
    assert d["remote_fxrp_total"] == 20_097_501.29
    assert set(d["remote_fxrp_by_chain"]) == {
        "Ethereum", "Monad", "HyperEVM", "Katana", "Base", "BNB"
    }
    assert d["top_six_holder_share_pct"] == 86.98
    assert d["top_fxrp_holders"][0]["protocol"] == "Firelight stXRP vault"
    assert d["top_fxrp_holders"][0]["share_pct"] == 36.04


def test_morpho_market_is_live_collateral_use_but_not_a_ripple_loan():
    d = load_snapshot()["morpho_ethereum_rlusd_fxrp_market"]
    assert d["collateral_asset"] == "FXRP"
    assert d["debt_asset"] == "RLUSD"
    assert d["market_permissionless"] is True
    assert d["borrowed_rlusd"] == 8_440_000
    assert d["utilization_pct"] > 90
    assert d["liquidation_ltv_pct"] == 77
    assert d["supplier_concentration"]["share_pct"] == 99.04
    assert d["borrower_concentration"]["top_three_total_share_pct"] == 90.96
    assert d["realized_bad_debt_usd"] == 0
    assert "not a direct Ripple loan" in " ".join(d["limits"])


def test_firelight_is_slashable_shared_cover_not_native_xrp_staking_or_insurance():
    d = load_snapshot()["firelight_cover"]
    assert d["current_fxrp_held_in_firelight_contract"] == 51_899_854.32
    assert d["current_share_of_fxrp_supply_pct"] == 36.04
    assert d["not_insurance"] is True
    assert d["slashing_risk"].startswith("Confirmed")
    assert "Kraken USDC DeFi Earn Protected Strategy" in d["shared_cover_targets"]
    assert d["first_loss_buffer"]["status"] == "SECONDARY_ONCHAIN_OBSERVATION_NOT_CURRENTLY_REVERIFIED"
    assert d["reward_accrual_during_unstaking"] == "UNRESOLVED"


def test_actual_capital_phrase_is_not_a_disclosed_amount():
    d = load_snapshot()["actual_capital_phrase"]
    assert d["exact_phrase"] == "actual capital deployment and liquidity provision"
    assert d["classification"] == "EXACT_OFFICIAL_PHRASE_MATCH"
    assert d["intended_original_user_reference"] == "UNCONFIRMED"
    assert "not a disclosed dollar amount" in " ".join(d["limits"])


def test_ask_coin_permission_coin_and_asksurf_are_not_conflated():
    d = load_snapshot()["identity_resolution"]["ask_coin"]
    assert d["best_literal_match"] == "Ask Coin exchange listing on CoinMarketCap"
    assert d["status"] == "Inactive / untracked"
    assert d["xrp_relationship"] == "No direct XRP relationship established"
    assert "Permission Coin is a different token" in d["distinctions"][0]
    assert "AskSurf is a separate x402 directory merchant" in d["distinctions"][1]


def test_tokyo_sbic_chatgpt_course_is_education_not_partnership():
    d = load_snapshot()["identity_resolution"]["sbic"]
    assert d["entity"] == "Tokyo Small and Medium Business Investment & Consultation Co., Ltd."
    assert "Day 1: ChatGPT and generative AI" in d["content"]
    assert d["relationship_to_openai"] == "No OpenAI partnership established"
    assert d["relationship_to_xrp"] == "No XRP or Ripple relationship established"


def test_cumulative_sentiment_is_not_admitted_as_current_xrp_signal():
    d = load_snapshot()["repository_sentiment_audit"]
    assert d["entity_sentiment_profile"]["net_sentiment_score"] == 0.455
    assert d["entity_sentiment_profile"]["time_window"] == "All-time cumulative history"
    assert d["entity_sentiment_profile"]["model_admission"] == "REJECTED_AS_CURRENT_SENTIMENT_FEATURE"
    assert d["sentiment_shift"]["recent_entries"] == 0
    assert d["sentiment_shift"]["score"] is None
