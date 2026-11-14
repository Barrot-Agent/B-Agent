from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105T121700Z-xrp-insights-row-status-admission-contract.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_flow_status_initial_and_excluded_are_not_zero_flows():
    statuses = load()["dataset_contract"]["flow_status"]
    assert "starting balance" in statuses["initial"]["meaning"]
    assert "Never coerce to zero" in statuses["excluded"]["feature_use"]


def test_provisional_and_reconstructed_rows_are_raw_only():
    statuses = load()["dataset_contract"]["row_status"]
    assert "Raw-only" in statuses["provisional"]["feature_use"]
    assert "Raw-only" in statuses["reconstructed"]["feature_use"]
    assert "day-by-day split is an estimate" in statuses["reconstructed"]["meaning"]


def test_product_structure_is_separated_from_pure_spot_etf_flows():
    products = load()["product_structure_and_known_exclusions"]
    assert "index rebalancing" in products["BITW"]["limitation"]
    assert "look-through" in products["XRPR"]["limitation"]
    assert "frozen" in products["GXRP"]["incident"]


def test_source_rounding_and_timestamp_vintages_are_explicit():
    data = load()["dataset_contract"]
    assert "100 XRP" in data["rounding"]["source_rule"]
    assert "first_seen_at" in data["timestamps"]
    assert "Do not backdate known_at" in data["timestamps"]["rule"]


def test_feature_admission_requires_settled_computed_rows_and_raw_receipts():
    policy = load()["feature_admission_contract"]
    assert policy["status"] == "DESIGNED_NOT_IMPLEMENTED_AS_A_LIVE_ETF_PARSER"
    assert "row_status equals settled" in policy["admit_flow_row_only_if"]
    assert "flow_status equals computed" in policy["admit_flow_row_only_if"]
    assert "raw source bytes are present and match the SHA-256 receipt" in policy["admit_flow_row_only_if"]


def test_methodology_artifact_is_not_a_model_feature_or_forecast():
    data = load()
    assert data["predictive_admission"]["model_eligible"] is False
    assert data["predictive_admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["source"]["raw_source_bytes_captured"] is False
    assert data["source"]["raw_content_sha256"] is None
