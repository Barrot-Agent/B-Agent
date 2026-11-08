from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T101200Z-xrpl-validator-signing-key-rotation-amendment-vote-integrity.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_upstream_issue_receipt_hash_matches_and_issue_is_open():
    data = load_artifact()
    receipt = data["source_receipts"][0]
    assert hashlib.sha256(receipt["normalized_excerpt"].encode("utf-8")).hexdigest() == receipt["normalized_excerpt_sha256"]
    assert receipt["normalized_excerpt_sha256"] == "70905247af12ca403748d21af22b715586e68496e754b80981c6fa713fec4ef6"
    assert data["issue"]["number"] == 8534
    assert data["issue"]["state"] == "open"
    assert data["issue"]["comments"] == 0
    assert data["issue"]["linked_pull_requests_observed"] == 0


def test_reported_mainnet_vote_denominator_example_is_preserved_with_counterevidence():
    data = load_artifact()
    row = data["reported_mainnet_observation"]
    assert row["validator_list_trusted_keys"] == 35
    assert row["validator_list_current_signing_keys"] == 35
    assert row["one_node_admin_feature_validations"] == 33
    assert row["one_node_admin_feature_threshold"] == 26
    assert row["amendment_vote_count"] == 28
    assert "no amendment's pass/fail outcome currently differs" in row["issue_counterevidence"]


def test_current_develop_code_recheck_preserves_reported_mechanism():
    data = load_artifact()
    row = data["current_code_recheck"]
    assert row["commit"] == "192b77d456ef0c14faf6095454b9bbc9476f4ce3"
    assert "recordedVotes_ remains keyed by PublicKey" in row["files"]["amendment_table"]["observations"]
    assert "val->getSignerPublic()" in row["files"]["amendment_table"]["observations"][1]
    assert "non-empty TrustChanges.added or TrustChanges.removed" in row["files"]["network_ops"]["observation"]
    assert "non-empty trustChanges.added or trustChanges.removed" in row["files"]["validator_list"]["observation"]


def test_lending_protocol_counts_are_qualified_not_declared_wrong():
    data = load_artifact()
    row = data["relevance_to_xrp_research"]
    assert "21/35" in row["relation_to_prior_lending_tracker"]
    assert "does not prove those specific counts are wrong" in row["relation_to_prior_lending_tracker"]
    assert len(row["verification_needed"]) >= 3
    assert data["model_admission"]["eligible"] is False


def test_no_forecast_or_production_validator_action():
    data = load_artifact()
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_probability_issued"] is False
    assert data["external_actions"]["validator_restart"] is False
    assert data["external_actions"]["production_rpc_mutation"] is False
    assert data["external_actions"]["real_money"] is False
