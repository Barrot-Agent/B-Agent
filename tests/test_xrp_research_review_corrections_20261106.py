from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "research" / "xrp_intelligence" / "20261106T100440Z-research-review-correction-bundle.json"
SBIC_EARLY_ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T0425Z-sbic-evernorth-actual-capital-identity-reconciliation.json"
SBIC_ADDENDUM = ROOT / "research" / "xrp_intelligence" / "20261106T094856Z-sbic-regional-company-primary-profile-vs-sbi-holdings-addendum.json"
SBIC_PRIOR_CORRECTION = ROOT / "research" / "xrp_intelligence" / "20261106T095354Z-sbic-corporate-number-and-capital-source-correction.json"
XRP_TARGET = ROOT / "research" / "xrp_intelligence" / "20261106T093925Z-xrp-spot-perpetuals-etf-macro-vintage-update.json"
FUELMAPS_SOURCE = ROOT / "research" / "xrp_intelligence" / "20261106T081536Z-xrp-live-spot-depth-derivatives-event-snapshot.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = b"blob " + str(len(payload)).encode("ascii") + b"\0"
    return hashlib.sha1(header + payload).hexdigest()


def test_sbic_central_japanese_capital_is_converted_without_inserting_eighty_million() -> None:
    bundle = load(BUNDLE)
    correction = bundle["corrections"][0]
    primary = correction["primary_source_reconciliation"]
    conversion = primary["conversion"]
    supersession = correction["supersession"]

    assert correction["correction_id"] == "SBIC_CENTRAL_CAPITAL_NUMERAL_CONVERSION_20261106"
    assert primary["profile_displayed_capital"] == "43億80万円"
    assert primary["history_displayed_capital"] == "43億80万円"
    assert conversion["oku_component_jpy"] == 4_300_000_000
    assert conversion["man_component_jpy"] == 800_000
    assert conversion["corrected_total_jpy"] == 4_300_800_000
    assert supersession["previously_recorded_official_profile_value_jpy"] == 4_380_800_000
    assert supersession["corrected_official_profile_value_jpy"] == 4_300_800_000
    assert supersession["secondary_directory_value_jpy"] == 4_800_800_000
    assert supersession["corrected_absolute_difference_jpy"] == 500_000_000
    assert supersession["selected_value_jpy"] == 4_300_800_000
    assert supersession["original_artifacts_modified"] is False

    # The earlier records remain intact and are explicitly superseded, not silently rewritten.
    assert load(SBIC_EARLY_ARTIFACT)["sbic_identity"]["companies"][1]["capital_jpy"] == 4_380_800_000
    assert load(SBIC_ADDENDUM)["entity_resolution"]["entities"][1]["capital_jpy"] == 4_380_800_000
    assert load(SBIC_PRIOR_CORRECTION)["capital_disagreement"]["selected_value_jpy"] == 4_380_800_000
    assert git_blob_sha(SBIC_EARLY_ARTIFACT) == correction["correction_of"][0]["git_blob_sha"]
    assert git_blob_sha(SBIC_ADDENDUM) == correction["correction_of"][1]["git_blob_sha"]
    assert git_blob_sha(SBIC_PRIOR_CORRECTION) == correction["correction_of"][2]["git_blob_sha"]

    assert bundle["overall_model_eligibility"]["eligible"] is False
    assert bundle["forecast_status"]["directional_forecast_issued"] is False


def test_kraken_quote_is_derived_from_the_exact_rendered_response() -> None:
    bundle = load(BUNDLE)
    correction = bundle["corrections"][1]
    capture = correction["kraken_rendered_ticker_capture"]
    raw_text = capture["rendered_response_text"]
    assert hashlib.sha256(raw_text.encode("utf-8")).hexdigest() == capture["rendered_response_sha256"]

    ticker = json.loads(raw_text)["result"]["XXRPZUSD"]
    quote = capture["parsed_quote"]
    bid = Decimal(ticker["b"][0])
    ask = Decimal(ticker["a"][0])
    last = Decimal(ticker["c"][0])
    vwap = Decimal(ticker["p"][1])
    low = Decimal(ticker["l"][1])
    day_open = Decimal(ticker["o"])

    assert quote["last_trade_usd"] == pytest.approx(float(last))
    assert quote["best_bid_usd"] == pytest.approx(float(bid))
    assert quote["best_ask_usd"] == pytest.approx(float(ask))
    assert quote["rolling_24h_volume_xrp"] == pytest.approx(float(Decimal(ticker["v"][1])))
    assert quote["rolling_24h_vwap_usd"] == pytest.approx(float(vwap))
    assert quote["rolling_24h_low_usd"] == pytest.approx(float(low))
    assert quote["rolling_24h_high_usd"] == pytest.approx(float(Decimal(ticker["h"][1])))
    assert quote["utc_day_open_usd"] == pytest.approx(float(day_open))
    assert quote["spread_bps"] == pytest.approx(float((ask - bid) / ((ask + bid) / 2) * Decimal("10000")))
    assert quote["last_vs_utc_day_open_pct"] == pytest.approx(float((last / day_open - 1) * 100))
    assert quote["last_vs_rolling_24h_vwap_pct"] == pytest.approx(float((last / vwap - 1) * 100))
    assert quote["last_above_rolling_24h_low_pct"] == pytest.approx(float((last / low - 1) * 100))

    assert capture["provider_event_timestamp_utc"] is None
    assert capture["raw_http_wire_bytes_captured"] is False
    assert capture["model_eligibility"]["eligible"] is False
    assert capture["forecast_status"]["directional_forecast_issued"] is False


def test_fuelmaps_historical_depth_has_a_git_blob_bound_source_lineage() -> None:
    bundle = load(BUNDLE)
    correction = bundle["corrections"][1]["historical_depth_lineage_correction"]
    source = load(FUELMAPS_SOURCE)

    assert git_blob_sha(FUELMAPS_SOURCE) == correction["source_artifact_git_blob_sha"]
    assert source["artifact_id"] == "xrp_live_spot_depth_derivatives_event_snapshot_20261106T081536Z"
    depth = source["order_book_depth"]
    assert depth["source_id"] == correction["source_id"]
    assert depth["snapshot_time_utc"] == correction["snapshot_time_utc"]
    two_pct = next(level for level in depth["levels"] if level["band"] == "±2%")
    assert two_pct["bid_depth_usd"] == correction["plus_minus_2pct_bid_depth_usd"]
    assert two_pct["ask_depth_usd"] == correction["plus_minus_2pct_ask_depth_usd"]
    assert depth["venue_coverage_count"] == len(correction["venue_coverage"])
    assert correction["status"] == "HISTORICAL_CONTEXT_ONLY_STALE_AT_LATER_KRAKEN_CAPTURE"
    assert correction["original_artifact_modified"] is False
    assert bundle["overall_model_eligibility"]["eligible"] is False
