from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T220025Z-xrp-live-spot-etf-flow-vintage-reconciliation.json"
)
PRIOR_SPOT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T213601Z-xrp-kraken-okx-live-spot-cross-venue-snapshot.json"
)


def test_spot_receipts_are_content_addressed_and_quote_units_stay_separate():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert artifact["captured_at_utc"] == "2026-11-06T22:00:25Z"
    assert len(artifact["spot_observations"]) == 2
    for observation in artifact["spot_observations"]:
        raw = observation["raw_response_text"]
        encoded = raw.encode("utf-8")
        assert len(encoded) == observation["raw_response_bytes"]
        assert hashlib.sha256(encoded).hexdigest() == observation["raw_response_sha256"]
        assert json.loads(raw)

    by_venue = {item["venue"]: item for item in artifact["spot_observations"]}
    assert by_venue["Kraken"]["instrument"] == "XRP/USD"
    assert by_venue["Kraken"]["source_data_as_of_utc"] is None
    assert by_venue["Kraken"]["parsed"]["last_usd"] == 1.17706
    assert by_venue["OKX"]["instrument"] == "XRP-USDT"
    assert by_venue["OKX"]["source_data_as_of_utc"] == "2026-11-06T21:35:28.571Z"
    assert by_venue["OKX"]["parsed"]["last_usdt"] == 1.1741


def test_okx_stale_repeat_and_spot_arithmetic_are_explicit():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    prior = json.loads(PRIOR_SPOT.read_text(encoding="utf-8"))
    current_okx = next(x for x in artifact["spot_observations"] if x["venue"] == "OKX")
    prior_okx = next(x for x in prior["observations"] if x["venue"] == "OKX")

    assert current_okx["raw_response_sha256"] == prior_okx["raw_response_sha256"]
    assert current_okx["freshness"]["unchanged_provider_timestamp_from_prior_213601Z_capture"] is True
    assert current_okx["freshness"]["provider_timestamp_age_seconds"] == 1496.429
    assert artifact["spot_comparison"]["okx_last_vs_kraken_last_pct"] == -0.2515
    assert artifact["spot_comparison"]["okx_last_vs_rolling_24h_open_pct"] == -4.2489
    assert "not a multi-level depth ladder" in artifact["spot_comparison"]["liquidity_warning"].lower()
    assert current_okx["freshness"]["admission"] == "stale_repeat_not_a_new_OKX_market_observation"


def test_etf_flow_receipts_and_fund_universes_are_not_mixed():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    by_provider = {x["provider"]: x for x in artifact["etf_flow_observations"]}

    insights = by_provider["XRP Insights"]
    excerpt = insights["normalized_excerpt"]
    assert len(excerpt.encode("utf-8")) == insights["source_receipt_bytes"]
    assert hashlib.sha256(excerpt.encode("utf-8")).hexdigest() == insights["source_receipt_sha256"]
    metadata = insights["metadata_normalized_excerpt"]
    assert len(metadata.encode("utf-8")) == insights["metadata_receipt_bytes"]
    assert hashlib.sha256(metadata.encode("utf-8")).hexdigest() == insights["metadata_receipt_sha256"]
    assert insights["parsed"]["latest_daily_flow_xrp"] == 110214
    assert insights["parsed"]["nov2_to_nov5_net_flow_xrp"] == -149487
    assert insights["parsed"]["gxrp_flow_status"] == "excluded_due_to_prior_capture_gap"
    assert insights["parsed"]["non_creation_redemption_changes_counted"] is True

    keyhole = by_provider["CryptoKeyhole"]
    excerpt = keyhole["normalized_excerpt"]
    assert len(excerpt.encode("utf-8")) == keyhole["source_receipt_bytes"]
    assert hashlib.sha256(excerpt.encode("utf-8")).hexdigest() == keyhole["source_receipt_sha256"]
    assert keyhole["parsed"]["nov5_funds_reporting"] == 3
    assert keyhole["parsed"]["nov5_funds_in_universe"] == 4
    assert keyhole["parsed"]["nov5_partial_flow_xrp"] == -3339
    assert keyhole["parsed"]["nov6_funds_published_at_update"] == 0
    assert keyhole["parsed"]["bitw_included"] is False

    reconciliation = artifact["etf_flow_reconciliation"]
    assert reconciliation["comparison_status"] == "NOT_COMPARABLE_DIFFERENT_UNIVERSES_AND_COMPLETENESS"
    assert "Do not average" in reconciliation["warning"]
    assert "not independent economic evidence" in reconciliation["shared_underlying_lineage"]


def test_derivatives_vintage_and_forecast_gate_fail_closed():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    derivatives = artifact["derivatives_freshness"]
    capture = datetime.fromisoformat(artifact["captured_at_utc"].replace("Z", "+00:00"))
    trad = datetime.fromisoformat(derivatives["latest_prior_tradradar_source_as_of_utc"].replace("Z", "+00:00"))
    aper = datetime.fromisoformat(derivatives["latest_prior_aperiodic_source_as_of_utc"].replace("Z", "+00:00"))

    assert (capture - trad).total_seconds() == 3925
    assert (capture - aper).total_seconds() == 12025
    assert derivatives["new_search_render_is_older_than_archived_observation"] is True
    assert derivatives["admission"] == "no_newer_derivatives_observation_admitted"
    assert artifact["model_eligibility"] == "research_context_only_not_admitted_as_a_point_in_time_model_feature"
    assert artifact["forecast_issued"] is False
    assert artifact["directional_forecast_eligible"] is False
    assert artifact["paper_trade_or_real_money_action"] is False
