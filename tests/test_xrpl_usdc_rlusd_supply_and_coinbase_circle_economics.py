import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = "data/xrp_intelligence/snapshots/20261101T164842Z-xrpl-usdc-rlusd-circle-coinbase-economics.json"


def load():
    return json.loads((ROOT / PATH).read_text(encoding="utf-8"))


def test_same_indexer_reports_rlusd_supply_materially_above_usdc():
    snap = load()
    tokens = snap["xrpl_tokens"]
    assert tokens["usdc"]["supply"] == 6_020_000
    assert tokens["rlusd"]["supply"] == 712_520_000
    assert tokens["comparisons"]["rlusd_to_usdc_xrpl_supply_multiple"] == 118.36
    assert tokens["comparisons"]["usdc_xrpl_share_of_circle_global_circulation_pct"] == 0.0086
    assert "same-indexer" in tokens["comparisons"]["caveat"].lower()


def test_permissionless_stablecoin_and_xrp_amm_pools_are_not_corporate_partnerships():
    snap = load()
    usdc = snap["xrpl_tokens"]["usdc"]["largest_amm_pools"]
    rlusd = snap["xrpl_tokens"]["rlusd"]["largest_amm_pools"]
    assert usdc[0]["pair"] == "USDC/XRP"
    assert rlusd[0]["pair"] == "RLUSD/XRP"
    assert usdc[1]["pair"] == "USDC/RLUSD"
    assert rlusd[1]["pair"] == "RLUSD/USDC"
    assert usdc[1]["trades_30d"] == 144
    assert "not formal" in " ".join(snap["hypotheses"][2]["counter_evidence"] for _ in [0]).lower() or snap["hypotheses"][2]["classification"] == "CONFIRMED_POOL_EXISTS"


def test_circle_global_redemptions_are_not_attributed_to_xrp():
    circle = load()["circle_global_usdc"]
    assert circle["circulation_usd"] == 70_000_000_000
    assert circle["reserve_assets_usd"] == 71_400_000_000
    assert circle["issuance_redemption"]["days_30"]["net_usd"] == -3_100_000_000
    assert "not evidence of rotation into XRP" in circle["interpretation"]


def test_circle_and_coinbase_financial_dependencies_are_separate_and_period_tagged():
    snap = load()
    circle = snap["circle_q2_2026_sec"]
    coinbase = snap["coinbase_q3_2026_sec"]
    assert circle["reserve_income_share_of_total_revenue_q2_pct"] == 95.2
    assert circle["distribution_costs_to_coinbase_q2_usd"] == 324_600_000
    assert circle["distribution_costs_to_coinbase_h1_usd"] == 655_300_000
    assert coinbase["consumer_spot_volume_q3_yoy_change_pct"] == -59
    assert coinbase["institutional_spot_volume_q3_yoy_change_pct"] == -53
    assert coinbase["net_income_q3_usd"] == 718_697_000
    assert coinbase["gains_on_crypto_assets_held_for_investment_q3_usd"] == 715_022_000
    assert "2026-06-30" == circle["period_end"]
    assert "2026-09-30" == coinbase["period_end"]


def test_no_xrp_forecast_or_predictive_feature_admission():
    snap = load()
    assert snap["data_quality"]["feature_admission"] == "NONE"
    assert snap["model_controls"]["forecast_status"] == "NOT_ISSUED"


def test_x402_micro_payment_cohort_matches_named_merchants_without_spam_attribution():
    correction = json.loads(
        (ROOT / "data" / "xrp_intelligence" / "research_ledger_addenda" /
         "20261101T211500Z-x402-cluster-reclassification-correction.json").read_text(encoding="utf-8")
    )
    rows = correction["exact_address_crosswalk"]
    assert {row["address"] for row in rows} == {
        "rBi1QrVjwaNofisZAQnovoXdHkS73FG1tJ",
        "ra9b6JX5aPVbdJhogDDddsRAcasWg7gzC3",
        "rMPwy3Ntx56Nyc2fKGNm7VRWdmpHSB92Z7",
    }
    assert {row["x402_merchant"] for row in rows} == {
        "Heurist Inference Router", "AskSurf", "Heurist Mesh"
    }
    classification = correction["correction"]["revised_classification"]
    assert classification.startswith("X402_COMPATIBLE_AGENT_MICROPAYMENT_COHORT")
    assert classification.endswith("NO_MALICIOUS_INTENT_INFERRED.")


def test_x402_batch_sessions_are_separate_from_raw_payment_counts():
    correction = json.loads(
        (ROOT / "data" / "xrp_intelligence" / "research_ledger_addenda" /
         "20261101T211500Z-x402-cluster-reclassification-correction.json").read_text(encoding="utf-8")
    )
    batch = correction["batch_settlement"]
    assert batch["paid_requests"] == 213008
    assert batch["sessions"] == 3162
    assert batch["ledger_transactions"] == 6324
    assert batch["calculated_requests_per_ledger_transaction"] > 33
    assert batch["causal_status"] == "PLAUSIBLE_MEASUREMENT_BREAK_NOT_PROVEN_FOR_THE_110_WALLETS"


def test_x402_foundation_graph_preserves_coinbase_circle_ripple_and_mastercard_roles():
    graph = json.loads(
        (ROOT / "data" / "xrp_intelligence" / "relationship_graph_addenda" /
         "20261101T211500Z-x402-coinbase-circle-ripple-mastercard-network.json").read_text(encoding="utf-8")
    )
    pairs = {(edge["from"], edge["to"]) for edge in graph["edges"]}
    assert ("Coinbase", "x402 protocol") in pairs
    assert ("Coinbase", "x402 Foundation") in pairs
    assert ("Circle", "x402 Foundation") in pairs
    assert ("Ripple", "x402 Foundation") in pairs
    assert ("Mastercard", "x402 Foundation") in pairs
    assert graph["non_edges_and_limits"]


def test_x402_feature_policy_does_not_treat_rlusd_volume_as_proportional_xrp_demand():
    policy = json.loads(
        (ROOT / "data" / "xrp_intelligence" / "architecture_decisions" /
         "20261101T211500Z-x402-payment-count-and-session-feature-policy.json").read_text(encoding="utf-8")
    )
    assert policy["admission_status"] == "DESIGNED_NOT_EXECUTED"
    assert any("CheckCreate and CheckCash counts" in item for item in policy["required_features"])
    assert policy["prediction_status"] == "NOT_ISSUED"


def test_live_x402_checkcash_is_recorded_without_claiming_cohort_migration():
    observation = json.loads(
        (ROOT / "data" / "xrp_intelligence" / "snapshots" /
         "20261101T211900Z-t54-live-checkcash-observation.json").read_text(encoding="utf-8")
    )
    assert observation["observation"]["transaction_hash"] == "384D9F00D96D61A2F19025D80793BD5D74E61E6CA95D2A2132B6BDE1A1E558AE"
    assert observation["observation"]["transaction_type"] == "CheckCash"
    assert observation["observation"]["amount_rlusd"] == 0.67376
    assert observation["observation"]["intent_status"] == "Unverified"
    assert "not proof" in observation["interpretation"].lower() or "not that the earlier 110-wallet cohort migrated" in observation["interpretation"].lower()


def test_ripple_escrow_post_release_relock_uses_pinned_ledger_and_corrects_stale_summary():
    snapshot = json.loads(
        (ROOT / "data" / "xrp_intelligence" / "snapshots" /
         "20261101T212500Z-escrow-post-release-relock-and-supply-breakdown.json").read_text(encoding="utf-8")
    )
    escrow = snapshot["escrow"]
    assert escrow["preferred_observation"]["ledger_index"] == 108052148
    assert escrow["preferred_observation"]["ripple_owned_escrow_xrp"] == 31_100_000_000
    assert escrow["preferred_observation"]["objects"] == 99
    assert escrow["same_day_events"]["released_xrp"] == 1_000_000_000
    assert escrow["same_day_events"]["re_escrowed_xrp"] == 700_000_000
    assert escrow["same_day_events"]["net_out_of_escrow_xrp"] == 300_000_000
    assert escrow["rolling_12_releases"]["reescrow_pct"] == 70
    assert escrow["rolling_12_releases"]["net_out_xrp"] == 3_600_000_000
    assert escrow["conflicting_summary"]["difference_xrp"] == 700_000_000
    assert escrow["schedule"]["unlock_objects_left"] == 32
    assert escrow["schedule"]["last_unlock"] == "2029-07-01"


def test_ripple_escrow_supply_correction_keeps_net_release_separate_from_sales():
    correction = json.loads(
        (ROOT / "data" / "xrp_intelligence" / "research_ledger_addenda" /
         "20261101T212500Z-escrow-700m-relock-and-circulating-supply-correction.json").read_text(encoding="utf-8")
    )
    assert correction["forecast_status"] == "NOT_ISSUED"
    assert any(item["id"] == "E3" and item["status"] == "NOT_ESTABLISHED" for item in correction["hypotheses"])
    assert any("not proof of 300M XRP sold" in item["text"] for item in correction["findings"])


def test_xrpl_rwa_headline_separates_distributed_float_from_registry_notional():
    snapshot = json.loads(
        (ROOT / "data" / "xrp_intelligence" / "snapshots" /
         "20261101T212500Z-escrow-post-release-relock-and-supply-breakdown.json").read_text(encoding="utf-8")
    )
    rwa = snapshot["market_structure"]["rwa"]
    assert rwa["combined_usd"] == 4_330_000_000
    assert rwa["distributed_usd"] == 276_000_000
    assert rwa["represented_usd"] == 4_060_000_000
    assert rwa["distributed_share_pct"] < 7
    assert rwa["represented_share_pct"] > 93
