from __future__ import annotations

import json
from pathlib import Path

ARTIFACT = Path(__file__).resolve().parents[1] / "research/xrp_intelligence/20261108T113700Z-xrp-exchange-rlusd-x402-phrase-reconciliation.json"

def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))

def test_exchange_wallets_are_not_tradable_float_or_customer_flow():
    obs = load_artifact()["observations"]["exchange_wallets"]
    assert obs["total_xrp"] == 22_340_000_000
    assert obs["wallet_count"] == 701 and obs["exchange_count"] == 24
    assert obs["same_wallet_change_7d_xrp"] == -104_400_000
    assert obs["naive_total_change_7d_xrp"] == 362_700_000
    assert "not a net inflow" in obs["naive_change_note"]
    assert obs["selected"]["Coinbase"]["cbxrp_reserve"] == 151_300_000
    assert obs["selected"]["SBI_VC_Trade"]["cold_labeled_pct"] == 99
    assert obs["model_eligible"] is False

def test_circulating_supply_and_rlusd_disagreements_are_not_averaged():
    obs = load_artifact()["observations"]
    assert obs["exchange_wallets"]["circulating_supply_disagreement"]["do_not_average"] is True
    assert obs["rlusd"]["disagreement"]["do_not_average"] is True
    assert obs["rlusd"]["rwa_xyz"]["legal_issuer"] == "Standard Custody & Trust Company, LLC"

def test_etf_holdings_delta_and_registry_notional_are_not_cash_or_float():
    obs = load_artifact()["observations"]
    assert obs["etf_holdings_delta"]["holdings_delta_nov2_nov6_xrp"] == -812_529
    assert obs["etf_holdings_delta"]["model_eligible"] is False
    assert obs["xrpl_rwa"]["distributed_transferable_usd"] == 276_000_000
    assert obs["xrpl_rwa"]["registry_represented_usd"] == 4_060_000_000

def test_x402_disagreement_and_micro_payment_limits_are_preserved():
    x = load_artifact()["observations"]["x402"]
    assert x["xrp_insights"]["transactions"] == 15_335_356
    assert x["t54"]["transactions"] == 15_343_857
    assert x["discrepancy"]["transaction_count"] == 8_501
    assert x["discrepancy"]["do_not_average"] is True
    assert x["model_eligible"] is False

def test_exact_phrase_and_identity_gates_remain_closed():
    p = load_artifact()["observations"]["phrase_research"]
    assert p["ask_coin"]["xrp_relationship"] == "NOT_ESTABLISHED"
    assert p["actual_capital"]["classification"] == "secondary_commentary_phrase_not_issuer_metric"
    assert p["japan_sbic_chatgpt"]["openai_partnership"] == "NOT_ESTABLISHED"
    assert p["kamilah_camilla_stevenson"]["personal_channel"] == "NOT_VERIFIED"
    assert load_artifact()["forecast_status"] == "NOT_ISSUED"

def test_rendered_sources_are_all_model_ineligible_without_raw_receipts():
    a = load_artifact()
    assert a["source_capture"]["raw_http_bytes_captured"] is False
    assert all(s["model_eligible"] is False for s in a["sources"])
    assert a["admission"]["feature_store_admission"] == "PROHIBITED"
    assert a["admission"]["forecast_issued"] is False
