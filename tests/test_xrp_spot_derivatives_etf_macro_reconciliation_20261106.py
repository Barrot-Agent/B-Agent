from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T074133Z-xrp-spot-derivatives-etf-macro-reconciliation.json"
)

RAW_KRAKEN_RENDERED = (
    '{"error":[],"result":{"XXRPZUSD":{"a":["1.18237000","90","90.000"],'
    '"b":["1.18236000","454","454.000"],"c":["1.18237000","8.41107000"],'
    '"v":["7833317.16798201","46371944.79678466"],'
    '"p":["1.20604343","1.24878496"],"t":[9834,44209],'
    '"l":["1.18210000","1.18210000"],"h":["1.22190000","1.32583000"],'
    '"o":"1.20567000"}}}'
)


@pytest.fixture(scope="module")
def data() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_rendered_response_hash_and_quote_arithmetic_are_reproducible(data: dict) -> None:
    market = data["observations"]["kraken_xrpusd"]
    digest = hashlib.sha256(RAW_KRAKEN_RENDERED.encode("utf-8")).hexdigest()
    assert digest == market["raw_capture"]["sha256"]
    assert market["last_usd"] == pytest.approx(1.18237)
    assert market["spread_bps"] == pytest.approx(
        (market["best_ask_usd"] - market["best_bid_usd"])
        / ((market["best_ask_usd"] + market["best_bid_usd"]) / 2)
        * 10_000,
        abs=1e-6,
    )
    assert market["last_vs_utc_day_open_pct"] == pytest.approx(-1.932535, abs=1e-6)
    assert market["last_vs_24h_vwap_pct"] == pytest.approx(-5.318366, abs=1e-6)
    assert market["distance_above_24h_low_pct"] == pytest.approx(0.022841, abs=1e-6)


def test_kraken_capture_is_not_mislabeled_as_byte_complete_or_event_time(data: dict) -> None:
    market = data["observations"]["kraken_xrpusd"]
    assert market["provider_event_timestamp_utc"] is None
    assert market["raw_capture"]["byte_complete_original_http_body"] is False
    assert market["raw_capture"]["response_headers_captured"] is False
    assert market["semantics"]["ticker_open"] == "UTC-day open, not a rolling 24-hour open"
    assert market["model_eligible"] is False


def test_tradradar_oi_and_liquidation_components_reconcile_without_claiming_independence(data: dict) -> None:
    derivatives = data["observations"]["tradradar_xrp_perpetuals"]
    oi_sum = sum(derivatives["oi_by_exchange_usd_millions"].values())
    assert oi_sum == pytest.approx(1883.51)
    assert oi_sum == pytest.approx(derivatives["oi_by_exchange_sum_usd_millions"])
    assert derivatives["liquidations_24h_usd_lower_bound"] == pytest.approx(
        derivatives["long_liquidations_24h_usd"] + derivatives["short_liquidations_24h_usd"],
        abs=10_000,
    )
    assert derivatives["coverage"]["oi_exchanges"] == 7
    assert derivatives["coverage"]["independence_group"] == "tradradar_aggregator"
    assert derivatives["reconciliation"]["account_ratio_is_not_notional_exposure"] is True
    assert derivatives["model_eligible"] is False


def test_etf_partial_day_and_distinct_universes_are_not_promoted_to_complete_cash_flows(data: dict) -> None:
    partial = data["observations"]["cryptokeyhole_xrp_etf_flows"]
    broad = data["observations"]["xrp_insights_etf_flows"]
    assert partial["nov5_status"] == "partial"
    assert partial["nov5_published_funds"] == 2
    assert partial["nov5_expected_funds"] == 4
    assert partial["nov5_daily_total_complete"] is False
    assert broad["page_data_as_of_date"] == "2026-11-04"
    assert broad["page_last_dataset_date"] == "2026-11-05"
    assert broad["nov5_row_status"] == "provisional_until_re_settled"
    assert broad["settled_window_flow_xrp"] == -259701
    assert partial["source_independence_group"] != broad["source_independence_group"]
    assert partial["model_eligible"] is False
    assert broad["model_eligible"] is False


def test_shared_issuer_inputs_are_explicitly_not_independent_confirmation(data: dict) -> None:
    independence = data["source_independence"]
    statements = " ".join(independence["explicit_non_independence"]).lower()
    assert "issuer-published data" in statements
    assert "not independent primary confirmations" in statements
    assert "not seven independent" in statements


def test_macro_and_bls_event_are_context_only_until_release_and_event_study(data: dict) -> None:
    macro = data["observations"]["macro_reuters"]
    event = data["observations"]["bls_upcoming_event"]
    assert macro["published_at_utc"] == "2026-11-06T01:24:00Z"
    assert macro["model_eligible"] is False
    assert event["scheduled_release_utc"] == "2026-11-06T13:30:00Z"
    assert event["status_at_market_cutoff"] == "upcoming_not_yet_published"


def test_hypotheses_retain_disconfirming_evidence_and_do_not_claim_causality(data: dict) -> None:
    hypotheses = data["competing_hypotheses"]
    assert len(hypotheses) >= 5
    assert all(item["supporting_evidence"] for item in hypotheses)
    assert all(item["disconfirming_or_limiting_evidence"] for item in hypotheses)
    assert all(item["status"] == "plausible_not_causally_established" for item in hypotheses if item["id"] in {"H1", "H2"})


def test_no_directional_forecast_or_model_admission_is_created(data: dict) -> None:
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_probability"] is None
    assert data["forecast"]["target"] is None
    assert data["forecast"]["horizon"] is None
    assert data["model_eligibility"]["artifact_model_eligible"] is False
