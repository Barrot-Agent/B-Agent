import hashlib
import json
from pathlib import Path

ARTIFACT = Path(
    "research/xrp_intelligence/20261107T110558Z-binance-breach-xrp-crosschain-trace-and-issuer-freezes.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_evidence_paraphrase_hashes_are_exact():
    artifact = load_artifact()
    for source in artifact["source_registry"]:
        for item in source.get("evidence_paraphrases", []):
            assert hashlib.sha256(item["text"].encode("utf-8")).hexdigest() == item["sha256"]


def test_initial_binance_xrp_outflow_is_separated_from_normal_exchange_flow():
    artifact = load_artifact()
    theft = artifact["theft_and_trace"]
    assert theft["stolen_xrp"] == 233_461_943.1
    assert theft["source_wallet_count"] == 5
    assert theft["source_account"] == "rK21t6nGLy4MNDqhvy3pGwcLFy25qgfzMx"
    assert len(theft["source_wallets"]) == 5
    assert artifact["model_admission"]["exchange_flow_feature_eligible"] is False


def test_failed_rlusd_payment_is_not_counted_as_an_rlusd_transfer():
    artifact = load_artifact()
    failed = next(x for x in artifact["event_timeline"] if x["status"] == "FAILED_PAYMENT_NO_RLUSD_TRANSFER")
    assert "42.75M RLUSD" in failed["event"]
    assert failed["tx"] == "AE08D54F8E7B05473AD5A1E3BF2C1D76A818B119DFBD3396C9C9F7BC7EF55A59"


def test_split_recipient_count_disagreement_is_preserved():
    artifact = load_artifact()
    split = artifact["theft_and_trace"]["account_split"]
    assert split["panoptic_recipient_count"] == 7
    assert split["elliptic_recipient_count"] == 6
    assert split["status"] == "COUNT_SEMANTICS_RECONCILED; 0.59905_XRP_ARITHMETIC_DIFFERENCE_UNRESOLVED"


def test_panoptic_thorchain_subset_is_not_fully_attributed():
    artifact = load_artifact()
    movement = artifact["theft_and_trace"]["movement_progress"]
    assert movement["panoptic_thorchain_deposits_xrp"] == 6_550_000
    assert movement["panoptic_thorchain_btc_output"] == 75.89
    assert movement["panoptic_minimum_other_sender_xrp"] == 1_420_000
    assert "do not attribute all 75.89 BTC to the theft" in artifact["theft_and_trace"]["interpretation"]["panoptic_output_attribution"]


def test_bitquery_and_elliptic_cutoffs_are_kept_separate():
    artifact = load_artifact()
    movement = artifact["theft_and_trace"]["movement_progress"]
    assert movement["bitquery_xrp_first_exit_xrp"] == 44_200_000
    assert movement["elliptic_nov6_0845_xrp_left"] == 42_000_000
    assert movement["elliptic_nov7_0800_additional_xrp_left"] == 44_000_000
    assert movement["elliptic_nov7_0800_xrp_remaining"] == 148_000_000


def test_cross_chain_conversion_is_not_mislabeled_as_cashout_or_cex_sale():
    artifact = load_artifact()
    interpretation = artifact["theft_and_trace"]["interpretation"]
    assert "not proof of centralized-exchange sale or fiat cashout" in interpretation["cross_chain_route"]
    assert "negligible amount" in interpretation["current_cashout_status"]
    assert artifact["model_admission"]["price_feature_eligible"] is False


def test_stablecoin_issuer_freezes_are_distinct_from_native_xrp():
    artifact = load_artifact()
    freezes = artifact["stablecoin_and_freeze_reconciliation"]
    assert freezes["ripple_rlusd"]["paused_xrp_incident_rlusd"] == 40_540_000
    assert freezes["circle_usdc"]["ethereum_main_receiving_address_frozen_usdc"] == 823_000_000
    assert freezes["native_xrp_freeze_function"] is False
    docs = next(s for s in artifact["source_registry"] if s["source_id"] == "xrpl_official_freeze_protocol")
    assert docs["evidence_paraphrases"][0]["text"] == "No one can freeze XRP in the XRP Ledger."
    assert freezes["freeze_total_disagreement"]["do_not_average"] is True


def test_total_incident_and_frozen_amount_disagreements_are_not_averaged():
    artifact = load_artifact()
    totals = artifact["incident_scope_disagreement"]["total_incident_usd"]
    assert totals["binance"] == 6_340_000_000
    assert totals["panoptic"] == 6_410_000_000
    assert totals["elliptic"] == 6_430_000_000
    assert artifact["stablecoin_and_freeze_reconciliation"]["freeze_total_disagreement"]["status"] == "UNRESOLVED_SCOPE_AND_CUTOFF_DIFFERENCE"


def test_attribution_and_ai_agent_claims_remain_qualified():
    artifact = load_artifact()
    attribution = artifact["attribution"]
    assert attribution["official_fbi_assessment"] == "DPRK / TraderTraitor"
    assert attribution["north_korea_position"] == "Denied responsibility"
    assert "not the human identity" in attribution["on_chain_identity_limit"]
    ai = artifact["ai_security_assessment"]
    assert any("No evidence" in item for item in ai["what_is_not_established"])
    assert any("no evidence of ai-agent decision-making" in item.lower() for item in ai["what_is_not_established"])


def test_no_forecast_or_trade_is_issued():
    artifact = load_artifact()
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["directional_forecast"] is None
    assert artifact["forecast"]["shadow_forecast"] is None
    assert artifact["forecast"]["paper_trade_executed"] is False
    assert artifact["forecast"]["real_money_action"] is False


def test_elliptic_summary_usd_values_are_not_mistaken_for_xrp_token_counts():
    artifact = load_artifact()
    note = artifact["cross_source_reconciliation"]["elliptic_unit_note"]
    assert "USD values, not XRP token counts" in note
    assert "148M XRP remaining" in note


def test_official_xrpl_docs_confirm_native_xrp_cannot_be_frozen():
    artifact = load_artifact()
    docs = next(s for s in artifact["source_registry"] if s["source_id"] == "xrpl_official_freeze_protocol")
    assert docs["publisher"] == "XRP Ledger Documentation"
    assert docs["evidence_paraphrases"][0]["text"] == "No one can freeze XRP in the XRP Ledger."


def test_six_main_recipients_plus_one_test_account_reconcile_six_vs_seven_count():
    artifact = load_artifact()
    split = artifact["theft_and_trace"]["account_split"]
    assert split["elliptic_main_recipient_count"] == 6
    assert split["q_eternal_main_recipient_count"] == 6
    assert split["panoptic_reported_new_accounts"] == 7
    assert split["separate_test_account_balance_xrp"] == 1000
    assert split["six_main_recipient_total_xrp"] == 233_460_920
    assert split["combined_reported_balance_xrp"] == 233_461_943.69905
    assert split["difference_vs_initial_report_xrp"] == 0.59905
    assert split["status"] == "COUNT_SEMANTICS_RECONCILED; 0.59905_XRP_ARITHMETIC_DIFFERENCE_UNRESOLVED"


def test_exact_five_hot_wallet_amounts_sum_to_the_reported_stolen_tranche():
    artifact = load_artifact()
    wallets = artifact["theft_and_trace"]["source_wallets"]
    assert sum(row["amount_xrp"] for row in wallets) == artifact["theft_and_trace"]["stolen_xrp"]
    assert len({row["ctid"] for row in wallets}) == 5


def test_separate_nov1_binance_50m_transfer_is_not_linked_to_the_attack():
    artifact = load_artifact()
    transfer = artifact["theft_and_trace"]["separate_binance_50m_transfer"]
    assert transfer["amount_xrp"] == 50_000_000
    assert transfer["linkage_to_attack"] == "NOT_ESTABLISHED"
    assert transfer["classification"] == "SEPARATE_EXCHANGE_FLOW_OBSERVATION"
