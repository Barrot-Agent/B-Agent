from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


ARTIFACT = Path("research/xrp_intelligence/20261105-xrp-late-session-market-cutoff-followup.json")


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_rendered_body_hash_and_spot_arithmetic():
    data = load_artifact()
    spot = data["market_snapshot"]["kraken_xrp_usd"]
    assert hashlib.sha256(spot["raw_response_body_text"].encode()).hexdigest() == spot["raw_response_body_text_sha256"]
    values = spot["values"]
    assert values["last_trade_usd"] == 1.2111
    assert values["spread_bps"] == pytest.approx(2.14703915)
    assert values["rolling_24h_volume_xrp"] == 40578515.209945
    assert values["utc_day_open_usd"] == 1.3041
    assert values["last_vs_utc_day_open_pct"] == pytest.approx(-7.13135496)
    assert spot["retrieval_time_utc"] is None
    assert data["capture_time_policy"]["captured_at_utc"] is None


def test_derivatives_coverage_and_counterevidence_are_preserved():
    data = load_artifact()
    derivatives = data["derivatives"]
    latest = derivatives["latest"]
    assert derivatives["provider_page_update_time_utc"] == "2026-11-05T22:35:00Z"
    assert derivatives["display_delay_minutes"] == 15
    assert latest["open_interest_7_exchanges_usd"] == 1_940_000_000
    assert latest["open_interest_change_24h_pct"] == -5.59
    assert latest["long_liquidations_usd"] > latest["short_liquidations_usd"]
    assert latest["funding_pct_per_8h"] > 0
    assert latest["long_account_share_pct"] == 80.1
    assert "USD-notional OI changes with mark price." in derivatives["limitations"]


def test_spot_and_derivatives_are_not_misrepresented_as_synchronized():
    data = load_artifact()
    alignment = data["cross_source_alignment"]
    assert alignment["synchronized"] is False
    assert alignment["cross_venue_basis_computed"] is False
    assert alignment["combined_return_series_computed"] is False
    assert data["model_admission"]["model_eligible"] is False


def test_no_forecast_or_trade_is_created_from_ineligible_observations():
    data = load_artifact()
    assert data["directional_forecast_issued"] is False
    assert data["forecast"]["issued"] is False
    assert data["forecast"]["target"] is None
    assert data["forecast"]["horizon"] is None
    assert data["forecast"]["probabilities"] is None
    assert data["paper_trade_executed"] is False
    assert data["real_money_action"] is False
    assert data["external_mutation"] is False
    assert len(data["competing_hypotheses"]) == 5
