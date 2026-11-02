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
    assert "does not make this a direct Ripple loan" in " ".join(d["limits"])


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


GRAPH = ROOT / "data/xrp_intelligence/relationship_graph_addenda/20261102T001348Z-ripple-flare-sentora-firelight-coinbase-circle-sbi.json"


def load_graph():
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def test_circle_arc_is_usdc_gas_and_sbi_is_its_validator():
    d = load_snapshot()["coinbase_circle_sbi"]["circle"]["arc"]
    assert d["gas_asset"] == "USDC"
    assert d["founding_validator"] == "SBI Group"
    assert d["exchange_participants"] == ["Coinbase", "Binance"]
    assert d["circle_claim_agent_transaction_volume_usdc_pct"] == 98.8
    assert d["arc_token"]["public_launch"].startswith("Not committed")
    g = load_graph()
    edges = {(e["from"], e["to"], e["type"]) for e in g["edges"]}
    assert ("SBI", "ARC_CHAIN", "founding_validator") in edges
    assert ("COINBASE", "ARC_CHAIN", "exchange_ecosystem_participant") in edges
    assert ("BINANCE", "ARC_CHAIN", "exchange_wallet_ecosystem_participant") in edges
    assert not any(a == "SBI" and b == "FLARE" for a, b, _ in edges)


def test_firelight_does_not_assume_sentora_usd_vault_is_rlusd():
    d = load_snapshot()["firelight_cover"]
    assert "do not assume" in d["sentora_usd_vault_asset_identity"]
    g = load_graph()
    assert not any(e["from"] == "FIRELIGHT" and e["to"] == "RLUSD" for e in g["edges"])
    assert any(e["from"] == "FIRELIGHT" and e["to"] == "SENTORA" for e in g["edges"])


def test_flare_fee_value_capture_is_not_mislabeled_as_xrp_value_capture():
    d = load_snapshot()["flare_official_ecosystem_update"]["token_value_capture"]
    assert d["reported_cumulative_fire_value_usd"] == 44632
    assert "FIRE" in d["fee_destination"]
    assert "not XRP value capture" in " ".join(d["limits"])
    path = load_snapshot()["flare_official_ecosystem_update"]["xrpl_native_rlusd_borrow_path"]
    assert path["status"] == "ROADMAP_NOT_LIVE"


def test_coinbase_rlusd_listing_is_live_but_global_exchange_collateral_is_future():
    d = load_snapshot()["coinbase_circle_sbi"]["coinbase"]["rlusd_listing"]
    assert d["platforms"] == ["Coinbase Prime", "Coinbase Exchange", "Coinbase Retail"]
    assert d["supported_networks"] == ["XRPL", "Base", "Ethereum"]
    assert d["global_exchange_collateral"] == "FUTURE_ANNOUNCED_NOT_LIVE_AT_CAPTURE"


def test_circle_arc_and_xrpl_x402_metrics_are_not_comparable():
    d = load_snapshot()["agentic_payments_comparison"]
    assert d["xrpl_t54"]["reported_all_time_transactions"] == 14_850_000
    assert d["xrpl_t54"]["reported_all_time_settled_value_usd"] == 48_848
    assert d["circle_arc"]["reported_usdc_share_of_agent_driven_transaction_volume_pct"] == 98.8
    assert d["circle_arc"]["absolute_volume_usd"] == "NOT_DISCLOSED"
    assert d["comparability"].startswith("NOT_COMPARABLE")


def test_sbi_circle_and_arc_exposure_is_separate_from_ripple_equity():
    sbi = load_snapshot()["coinbase_circle_sbi"]["sbi_group"]
    assert sbi["circle_equity_investment"]["total_usd"] == 50_000_000
    assert sbi["circle_jv"]["ownership"][0]["pct"] == 50
    assert sbi["circle_jv"]["ownership"][1]["pct"] == 50
    assert sbi["arc_presale"]["sbi_investment_amount"] == "NOT_DISCLOSED"
    assert "CEO_PUBLIC_STATEMENT" in sbi["ripple_equity"]["classification"]
    assert "not a $10B XRP token treasury" in sbi["ripple_equity"]["clarification"]
    assert "NOT_DISCLOSED" in sbi["arc_presale"]["token_allocation"]


def test_sbi_operational_xrp_and_xrpl_poc_are_not_token_treasury_claims():
    sbi = load_snapshot()["coinbase_circle_sbi"]["sbi_group"]
    assert "Operational XRP-based remittance" in sbi["operating_xrp_rails"]["sbi_remit"]
    assert sbi["xrpl_tokenized_deposits"]["status"] == "PROOF_OF_CONCEPT"
    assert "not proof of XRP collateralization" in sbi["xrpl_tokenized_deposits"]["description"]


def test_sbi_graph_has_circle_arc_presale_and_operational_entities():
    g = load_graph()
    edges = {(e["from"], e["to"], e["type"]) for e in g["edges"]}
    assert ("SBI", "ARC_CHAIN", "founding_validator") in edges
    assert ("SBI", "ARC_TOKEN", "presale_participation_via_consolidated_subsidiary_amount_undisclosed") in edges
    assert ("SBI", "CIRCLE_SBI_JV", "50_percent_joint_venture_ownership") in edges
    assert ("SBI_RIPPLE_ASIA", "XRPL", "tokenized_deposit_proof_of_concept_uses_XRPL") in edges
    assert ("SBI_REMIT", "XRP", "operational_cross_border_remittance_bridge_asset") in edges
