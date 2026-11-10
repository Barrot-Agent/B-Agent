"""Regression tests for the November 10, 2026 XRP macro/SBIC evidence artifact."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261110T142828Z-run132-october-cpi-sbic-primary-recheck-and-market-staleness.json"
)


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_run132_cpi_preserves_missing_year_over_year_values_and_monthly_vintages():
    data = _load()
    event = data["macro_event"]
    values = event["values"]
    assert event["publication_time"] == "2026-11-10T13:30:00Z"
    assert values["headline_cpi_mom_sa_pct"] == 0.4
    assert values["prior_month_headline_cpi_mom_sa_pct"] == 0.6
    assert values["core_cpi_mom_sa_pct"] == 0.3
    assert values["core_cpi_yoy_pct"] is None
    assert values["headline_cpi_yoy_pct"] is None
    assert "did not collect October 2025" in event["missing_data_reason"]


def test_run132_market_quotes_preserve_provider_time_and_are_not_model_eligible():
    data = _load()
    observations = {item["instrument"]: item for item in data["market_observations"]}
    assert observations["XRP/USD"]["provider_event_time"] is None
    assert observations["XRP-USDT"]["provider_event_time"] == "2026-11-10T14:21:43.065Z"
    assert observations["USDT/USD"]["provider_event_time"] is None
    assert all(item["model_eligible"] is False for item in observations.values())
    assert all(item["raw_wire_sha256"] is None for item in observations.values())
    assert data["derived_cross_venue_check"]["difference_basis_points"] > 0
    assert "Not executable arbitrage" in data["derived_cross_venue_check"]["interpretation"]


def test_run132_sbic_east_central_west_are_distinct_legal_entities():
    data = _load()
    entities = {item["id"]: item for item in data["sbic_identity"]["entities"]}
    assert entities["SBIC_EAST"]["legal_name"].startswith("Tokyo Small and Medium")
    assert entities["SBIC_EAST"]["corporate_number"] == "9011001030621"
    assert entities["SBIC_CENTRAL"]["legal_name"].startswith("Nagoya Small and Medium")
    assert entities["SBIC_WEST"]["legal_name"].startswith("Osaka Small and Medium")
    assert entities["SBI_HOLDINGS"]["legal_name"] == "SBI Holdings, Inc."
    assert entities["SBI_HOLDINGS"]["established"] == "1999-07-08"
    edges = data["sbic_identity"]["relationships"]
    assert any(edge["from"] == "SBIC_EAST" and edge["to"] == "SBIC_CENTRAL" and edge["type"] == "sister_company" for edge in edges)
    assert any(edge["from"] == "SBI_HOLDINGS" and edge["to"] == "SBIC_EAST" and edge["status"] == "not_established" for edge in edges)


def test_run132_chatgpt_sbic_event_is_education_not_openai_partnership():
    data = _load()
    edge = next(edge for edge in data["sbic_identity"]["relationships"] if edge["type"] == "educational_seminar_topic")
    assert edge["date"] == "2025-02-26"
    assert "Microsoft Japan" in edge["note"]
    assert "not as partner or sponsor" in edge["note"]


def test_run132_source_receipt_hashes_cover_surfaced_text_not_claimed_wire_bytes():
    data = _load()
    for receipt in data["source_receipts"]:
        assert receipt["raw_bytes_captured"] is False
        assert receipt["raw_byte_sha256"] is None
        if "normalized_excerpt" in receipt:
            actual = hashlib.sha256(receipt["normalized_excerpt"].encode("utf-8")).hexdigest()
            assert actual == receipt["normalized_excerpt_sha256"]
        if "surfaced_response_text" in receipt:
            actual = hashlib.sha256(receipt["surfaced_response_text"].encode("utf-8")).hexdigest()
            assert actual == receipt["surfaced_response_sha256"]


def test_run132_forecast_remains_not_issued_without_synchronized_event_dataset():
    data = _load()
    forecast = data["forecast"]
    assert forecast["status"] == "NOT_ISSUED"
    assert forecast["directional_probability"] is None
    assert forecast["model_feature_admission"] is False
