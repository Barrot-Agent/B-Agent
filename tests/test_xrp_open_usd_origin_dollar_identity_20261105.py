import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T141034Z-open-usd-origin-dollar-identity-bridge-reserve-reconciliation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_open_usd_and_origin_dollar_share_ticker_but_are_distinct_contracts():
    data = load()["entity_resolution"]
    open_usd = data["open_standard_open_usd"]
    origin = data["origin_dollar"]
    assert data["shared_symbol"] == "OUSD"
    assert open_usd["ticker"] == origin["ticker"] == "OUSD"
    assert open_usd["issuer_as_disclosed"] == "Bridge, a Stripe company"
    assert origin["issuer_and_protocol"] == "Origin Protocol"
    assert open_usd["project_linked_contract_directory"]["contracts"]["Ethereum"] != origin["Ethereum_contract"]


def test_open_standard_chain_contracts_are_explicit_and_xrpl_is_not_listed():
    identity = load()["entity_resolution"]["open_standard_open_usd"]
    contracts = identity["project_linked_contract_directory"]["contracts"]
    assert set(contracts) == {"Tempo", "Ethereum", "Base", "Solana"}
    assert identity["networks"] == ["Ethereum", "Solana", "Base", "Tempo"]
    assert "XRPL" not in identity["networks"]
    assert contracts["Solana"] == "ousd2mJsPEckLHcSCDxyKD7NDGARZcfLbDZkKiatYHB"


def test_november_12_first_live_payments_event_is_future_at_cutoff():
    status = load()["entity_resolution"]["open_standard_open_usd"]["status_at_cutoff"]
    assert status["first_live_payments_event_date"] == "2026-11-12"
    assert status["event_status"] == "future_at_research_cutoff"
    assert "separate milestones" in status["interpretation"]


def test_sbi_jpysc_ousd_relationship_is_only_a_pilot_under_consideration():
    source = next(s for s in load()["source_registry"] if s["source_id"] == "sbi_startale_open_standard_jpysc_pilot")
    assert any("not a new service or production" in c for c in source["claims_supported"])
    edge = next(e for e in load()["relationship_graph"] if e["from"] == "SBI Holdings and Startale")
    assert edge["relationship"] == "interoperability proof of concept under consideration"


def test_bridge_api_reserve_arithmetic_and_timestamp_are_preserved():
    data = load()["reserve_reconciliation"]
    api = data["api_snapshot_2026_11_05T141034Z"]
    arithmetic = data["api_arithmetic"]
    assert api["total_onchain_amount"] == 909_561_398.24664
    assert api["total_reserve_amount_usd"] == 911_545_202.68
    assert api["cash_usd"] + api["treasury_usd"] == arithmetic["cash_plus_treasury_usd"]
    assert round(api["total_reserve_amount_usd"] - api["total_onchain_amount"], 5) == round(arithmetic["reserve_total_minus_supply_usd"], 5)


def test_bridge_marketing_and_api_supply_disagreement_is_not_averaged():
    data = load()["reserve_reconciliation"]["marketing_page_disagreement"]
    assert data["displayed_circulation_usd"] == 468_000_000
    assert data["exact_timestamp"] is None
    assert "do not average" in data["interpretation"]


def test_august_attestation_does_not_attest_post_launch_november_reserves():
    data = load()["reserve_reconciliation"]["attestation_status"]
    assert data["latest_visible_report_month"] == "2026-08"
    assert data["launch_date"] == "2026-09-30"
    assert data["post_launch_independent_attestation_visible"] is False


def test_bridge_treasury_allocation_is_not_assumed_instantly_redeemable():
    text = load()["reserve_reconciliation"]["liquidity_interpretation"]
    assert "one business day" in text
    assert "24/7" in text


def test_xrp_relationship_hypotheses_keep_disconfirmation_and_no_forecast():
    data = load()
    assert data["xrp_relationship_assessment"]["xrpl_listed"] is False
    assert data["xrp_relationship_assessment"]["xrp_use_disclosed"] is False
    assert len(data["xrp_relationship_assessment"]["counter_hypotheses"]) == 4
    assert all(h["support"] and h["disconfirming_or_missing"] for h in data["xrp_relationship_assessment"]["counter_hypotheses"])
    assert data["admission"]["model_eligible"] is False
    assert data["admission"]["directional_forecast_issued"] is False


def test_sources_remain_model_ineligible_until_raw_receipts_exist():
    data = load()
    assert data["source_capture_policy"]["raw_bytes_preserved"] is False
    assert data["source_capture_policy"]["sha256_receipts"] is None
    assert all(source["model_eligible"] is False for source in data["source_registry"])
