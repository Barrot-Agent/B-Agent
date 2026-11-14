from __future__ import annotations

import json
from pathlib import Path

from barrot_agent.evolution.forecast_ledger import (
    READINESS_POLICY_ID,
    _MAX_WEIGHTED_CALIBRATION_ERROR,
    _MIN_HORIZON_MULTIPLE,
    _MIN_OOS_SAMPLES,
    _MIN_SHADOW_SAMPLES,
    _MIN_SOURCE_GROUPS,
    _REQUIRED_BASELINES,
)

from barrot_agent.evolution.xrp_public_ingestion import (
    DIGEST_ONLY_RAW_SOURCE_REASONS,
    ENDPOINTS,
    SCHEDULED_ENDPOINTS,
    WEEKLY_ENDPOINTS,
)


ROOT = Path(__file__).resolve().parents[1]


def test_feature_store_contract_endpoint_counts_match_registry() -> None:
    contract = (ROOT / "research" / "xrp_intelligence" / "feature-store-contract.md").read_text(
        encoding="utf-8"
    )
    assert len(ENDPOINTS) == 50
    assert len(SCHEDULED_ENDPOINTS) == 45
    assert len(WEEKLY_ENDPOINTS) == 3
    assert len(ENDPOINTS) == len(SCHEDULED_ENDPOINTS) + len(WEEKLY_ENDPOINTS) + 2
    assert "50 public endpoint records: 45 hourly scheduled sources, three weekly scheduled CFTC sources" in contract
    assert "Thus 48 sources are scheduled (45 hourly plus three weekly) and two public-node endpoints are excluded from the default schedule." in contract
    assert "40 endpoint records: 36 hourly scheduled sources" not in contract
    assert "two free non-commercial XRPL public-node endpoints excluded by default" in contract


def test_exchange_wallet_balance_source_is_scheduled_digest_only() -> None:
    all_sources = {source_id for source_id, _ in ENDPOINTS}
    scheduled_sources = {source_id for source_id, _ in SCHEDULED_ENDPOINTS}
    assert "xrp_exchange_balances_json" in all_sources
    assert "xrp_exchange_balances_json" in scheduled_sources
    assert "xrp_exchange_balances_json" in DIGEST_ONLY_RAW_SOURCE_REASONS
    assert "SHA-256 receipt only" in DIGEST_ONLY_RAW_SOURCE_REASONS["xrp_exchange_balances_json"]


def test_primary_mission_is_xrp_priority_one_on_barrot_v3() -> None:
    mission = json.loads(
        (ROOT / "barrot_agent" / "data" / "missions" / "primary_mission.json").read_text(
            encoding="utf-8"
        )
    )
    assert mission["mission_id"] == "xrp_intelligence_prediction_engine"
    assert mission["priority"] == 1
    assert mission["status"] == "active"
    assert mission["foundation"]["id"] == "barrot_v3"
    assert mission["foundation"]["preserve"] is True
    assert mission["foundation"]["responsibilities"] == [
        "execution",
        "orchestration",
        "safety",
        "verification",
    ]

def test_primary_mission_requires_specific_approval_for_paper_simulation() -> None:
    mission = json.loads(
        (ROOT / "barrot_agent" / "data" / "missions" / "primary_mission.json").read_text(
            encoding="utf-8"
        )
    )
    guardrails = mission["guardrails"]
    assert any(
        "Paper-trade or simulation execution is prohibited unless the exact action, product, source SHA, scope and run are explicitly approved" in item
        for item in guardrails
    )
    assert any("No guaranteed returns or real-money actions" in item for item in guardrails)
    assert not any(item == "No guaranteed returns, real-money actions or paper trades." for item in guardrails)


def test_forecast_admission_policy_matches_fail_closed_ledger() -> None:
    mission = json.loads(
        (ROOT / "barrot_agent" / "data" / "missions" / "primary_mission.json").read_text(
            encoding="utf-8"
        )
    )
    policy = mission["forecast_admission_policy"]

    assert policy["policy_id"] == READINESS_POLICY_ID
    assert policy["minimum_training_samples"] == _MIN_OOS_SAMPLES
    assert policy["minimum_out_of_sample_samples"] == _MIN_OOS_SAMPLES
    assert policy["minimum_shadow_evaluation_samples"] == _MIN_SHADOW_SAMPLES
    assert policy["minimum_oos_effective_sample_size"] == _MIN_HORIZON_MULTIPLE
    assert policy["minimum_shadow_effective_sample_size"] == _MIN_HORIZON_MULTIPLE
    assert policy["minimum_oos_span_horizons"] == _MIN_HORIZON_MULTIPLE
    assert policy["minimum_shadow_span_horizons"] == _MIN_HORIZON_MULTIPLE
    assert policy["minimum_independent_source_groups"] == _MIN_SOURCE_GROUPS
    assert policy["minimum_source_clusters"] == _MIN_SOURCE_GROUPS
    assert policy["minimum_origins_per_source_cluster"] >= policy["block_length_origins"]
    assert policy["paired_uncertainty_method"] == "paired_temporal_and_source_clustered_moving_block_bootstrap_v1"
    assert policy["familywise_confidence_level"] == 0.95
    assert policy["familywise_comparison_count"] == 8
    assert policy["multiplicity_method"] == "bonferroni"
    assert policy["minimum_individual_confidence_level"] >= 0.99375
    assert policy["minimum_bootstrap_replicates"] >= 10000
    assert policy["required_evaluation_windows"] == ["out_of_sample", "shadow_evaluation"]
    assert policy["require_temporal_and_source_clustered_intervals"] is True
    assert policy["require_upper_confidence_bounds_below_zero"] is True
    assert policy["maximum_weighted_calibration_error"] == _MAX_WEIGHTED_CALIBRATION_ERROR
    assert policy["required_baselines"] == list(_REQUIRED_BASELINES)
    assert policy["candidate_must_beat_each_baseline_on"] == [
        "mean_brier_score",
        "mean_log_loss",
    ]
    assert policy["required_statuses"] == {
        "leakage_checks": "PASS",
        "drift": "STABLE",
        "shadow_evaluation": "PASS",
        "paired_uncertainty": "PASS",
        "independent_evaluator_attestation": "VALID_ED25519",
    }
    assert policy["forecast_issuance_enabled"] is False
    assert policy["status"] == "NOT_SATISFIED"

def test_forecast_ledger_contract_documents_policy_v6() -> None:
    contract = (ROOT / "research" / "xrp_intelligence" / "forecast-ledger-contract.md").read_text(
        encoding="utf-8"
    )
    assert "# XRP fixed-horizon forecast ledger contract v6" in contract
    assert "BARROT_XRP_MODEL_READINESS_V6" in contract
    assert "minimum_origins_per_source_cluster >= block_length_origins" in contract
    assert "Coverage simulations, cluster-count sensitivity and block-length sensitivity" in contract
