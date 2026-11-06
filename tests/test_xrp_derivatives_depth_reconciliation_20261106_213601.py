from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

import pytest


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T213601Z-xrp-derivatives-depth-reconciliation.json"
)


def test_derivatives_depth_excerpt_receipts_are_content_addressed():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert artifact["captured_at_utc"] == "2026-11-06T21:36:01Z"
    assert len(artifact["observations"]) == 2
    for observation in artifact["observations"]:
        excerpt = observation["normalized_excerpt"]
        encoded = excerpt.encode("utf-8")
        assert len(encoded) == observation["source_receipt_bytes"]
        assert hashlib.sha256(encoded).hexdigest() == observation["source_receipt_sha256"]
        assert "not the original HTML" in observation["source_receipt_hash_scope"]


def test_tradradar_venue_oi_and_liquidation_arithmetic_reconcile():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    trad = next(x for x in artifact["observations"] if x["provider"] == "TradRadar")
    parsed = trad["parsed"]

    oi_sum = sum(parsed["open_interest_by_exchange_usd_millions"].values()) * 1_000_000
    assert oi_sum == pytest.approx(artifact["reconciliation"]["tradradar_open_interest_by_exchange_sum_usd"], abs=0.01)
    assert round(oi_sum / 1_000_000_000, 2) == 1.90
    long_share = (
        parsed["long_liquidations_usd_rounded"]
        / (parsed["long_liquidations_usd_rounded"] + parsed["short_liquidations_usd"])
        * 100
    )
    assert long_share == pytest.approx(95.34, abs=0.01)
    assert parsed["funding_oi_weighted_pct_per_8h"] > 0
    assert any(rate < 0 for rate in parsed["funding_by_exchange_pct_per_8h"].values())
    assert parsed["liquidations_24h_usd_min"] >= (
        parsed["long_liquidations_usd_rounded"] + parsed["short_liquidations_usd"]
    )


def test_provider_universes_and_vintages_are_not_averaged():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    by_provider = {x["provider"]: x for x in artifact["observations"]}
    trad = by_provider["TradRadar"]
    aper = by_provider["Aperiodic"]

    assert trad["parsed"]["open_interest_change_24h_pct"] == -3.34
    assert aper["parsed"]["open_interest_change_24h_pct"] == 9.71
    assert trad["source_data_as_of_utc"] == "2026-11-06T20:55:00Z"
    assert aper["source_data_as_of_utc"] == "2026-11-06T18:40:00Z"

    capture = datetime.fromisoformat(artifact["captured_at_utc"].replace("Z", "+00:00"))
    trad_time = datetime.fromisoformat(trad["source_data_as_of_utc"].replace("Z", "+00:00"))
    aper_time = datetime.fromisoformat(aper["source_data_as_of_utc"].replace("Z", "+00:00"))
    assert (capture - trad_time).total_seconds() == 2461
    assert (capture - aper_time).total_seconds() == 10561

    warning = artifact["reconciliation"]["provider_scope_warning"]
    assert "seven-exchange" in warning and "three-venue" in warning
    assert artifact["model_eligibility"] == "research_context_only_not_admitted_as_a_point_in_time_model_feature"
    assert artifact["forecast_issued"] is False
    assert artifact["directional_forecast_eligible"] is False
    assert artifact["paper_trade_or_real_money_action"] is False
