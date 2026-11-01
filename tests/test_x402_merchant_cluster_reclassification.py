import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "xrp_intelligence"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_bitquery_collectors_exactly_match_x402_merchants():
    correction = read_json(DATA / "research_ledger_addenda" / "20261101T211500Z-x402-cluster-reclassification-correction.json")
    rows = correction["exact_address_crosswalk"]
    assert {row["address"] for row in rows} == {
        "rBi1QrVjwaNofisZAQnovoXdHkS73FG1tJ",
        "ra9b6JX5aPVbdJhogDDddsRAcasWg7gzC3",
        "rMPwy3Ntx56Nyc2fKGNm7VRWdmpHSB92Z7",
    }
    assert {row["x402_merchant"] for row in rows} == {
        "Heurist Inference Router", "AskSurf", "Heurist Mesh"
    }
    assert correction["correction"]["revised_classification"].startswith("X402_COMPATIBLE_AGENT_MICROPAYMENT_COHORT")


def test_batch_settlement_is_recorded_as_a_measurement_break_not_proven_causality():
    correction = read_json(DATA / "research_ledger_addenda" / "20261101T211500Z-x402-cluster-reclassification-correction.json")
    batch = correction["batch_settlement"]
    assert batch["mainnet_beta_start"] == "2026-10-14"
    assert batch["paid_requests"] == 213008
    assert batch["sessions"] == 3162
    assert batch["ledger_transactions"] == 6324
    assert batch["causal_status"] == "PLAUSIBLE_MEASUREMENT_BREAK_NOT_PROVEN_FOR_THE_110_WALLETS"
    assert correction["forecast_status"] == "NOT_ISSUED"


def test_binance_wallet_labels_do_not_become_corporate_attribution():
    correction = read_json(DATA / "research_ledger_addenda" / "20261101T211500Z-x402-cluster-reclassification-correction.json")
    assert "not proof Binance corporate" in correction["retained_facts"]["binance_label_scope"]


def test_x402_graph_keeps_coinbase_circle_ripple_and_mastercard_as_open_standard_members():
    graph = read_json(DATA / "relationship_graph_addenda" / "20261101T211500Z-x402-coinbase-circle-ripple-mastercard-network.json")
    pairs = {(edge["from"], edge["to"]) for edge in graph["edges"]}
    assert ("Coinbase", "x402 protocol") in pairs
    assert ("Coinbase", "x402 Foundation") in pairs
    assert ("Circle", "x402 Foundation") in pairs
    assert ("Ripple", "x402 Foundation") in pairs
    assert ("Mastercard", "x402 Foundation") in pairs
    assert graph["non_edges_and_limits"]


def test_x402_feature_policy_keeps_paid_requests_and_ledger_transactions_separate():
    policy = read_json(DATA / "xrp_intelligence" / "architecture_decisions" / "20261101T211500Z-x402-payment-count-and-session-feature-policy.json")
    assert policy["admission_status"] == "DESIGNED_NOT_EXECUTED"
    assert any("CheckCreate and CheckCash counts" in item for item in policy["required_features"])
    assert policy["prediction_status"] == "NOT_ISSUED"
