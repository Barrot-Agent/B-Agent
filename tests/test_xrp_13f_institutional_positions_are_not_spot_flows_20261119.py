"""Regression guard for interpreting XRP-linked 13F positions and stale market snapshots."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261119T052027Z_run37_sec13f_market_snapshot.json"
)


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_susquehanna_13f_positions_are_etf_shares_not_xrp_tokens() -> None:
    payload = _load()
    positions = payload["institutional_13f"]["susquehanna_q3"]["common_etf_share_positions"]
    total = payload["institutional_13f"]["susquehanna_q3"]["common_share_total"]

    assert all(item["unit"] == "ETF_SHARES" for item in positions)
    assert sum(item["shares"] for item in positions) == 1_813_253
    assert sum(item["reported_value_usd"] for item in positions) == 32_105_403
    assert total["shares"] == 1_813_253
    assert total["reported_value_usd"] == 32_105_403
    assert "xrp_token_quantity" not in total
    assert payload["model_eligibility"]["eligible"] is False


def test_options_are_separate_from_common_etf_share_positions() -> None:
    payload = _load()
    susq = payload["institutional_13f"]["susquehanna_q3"]
    jane = payload["institutional_13f"]["jane_street"]["q3_2026"]

    assert len(susq["separately_reported_options"]) == 5
    assert len(jane["separately_reported_options"]) == 5
    assert all("side" in item for item in jane["separately_reported_options"])
    assert all("side" not in item for item in jane["common_spot_etf_share_positions"])


def test_jane_street_bitwise_change_uses_same_fund_and_quarter_end_cutoffs() -> None:
    payload = _load()["institutional_13f"]["jane_street"]
    q2 = payload["q2_2026"]
    q3 = payload["q3_2026"]
    bitwise = next(item for item in payload["same_fund_share_count_changes"] if item["issuer"] == "Bitwise XRP ETF")

    assert q2["period_end"] == "2026-06-30"
    assert q3["period_end"] == "2026-09-30"
    assert bitwise["q2_shares"] == 1_205_067
    assert bitwise["q3_shares"] == 733_472
    assert bitwise["delta_shares"] == -471_595
    assert round(bitwise["pct_change"], 4) == -39.1343


def test_market_snapshot_is_not_model_eligible_or_full_depth() -> None:
    payload = _load()
    market = payload["market_snapshot"]

    assert market["depth_capture"]["full_order_book_captured"] is False
    assert all(not venue["model_eligible"] for venue in market["venues"])
    okx = next(venue for venue in market["venues"] if venue["venue"] == "OKX")
    assert okx["age_seconds_at_retrieval"] > 300
    kraken = next(venue for venue in market["venues"] if venue["venue"] == "Kraken")
    assert kraken["provider_timestamp"] is None
    assert "freshness is uncertain" in kraken["cache_warning"]
    assert payload["no_forecast_issued"] is True


def test_hashes_are_reproducible_and_explicitly_not_raw_source_hashes() -> None:
    payload = _load()
    filings = payload["institutional_13f"]["sources"]

    for filing in filings:
        normalized = "\n".join(filing["normalized_rows"]).encode("utf-8")
        assert hashlib.sha256(normalized).hexdigest() == filing["normalized_rows_sha256"]
        assert filing["raw_bytes_captured"] is False
        assert "not a hash of raw SEC response bytes" in filing["hash_scope"]

    for venue in payload["market_snapshot"]["venues"]:
        rendered = venue["rendered_response"].encode("utf-8")
        assert hashlib.sha256(rendered).hexdigest() == venue["rendered_response_sha256"]
        assert "not raw transport bytes" in venue["hash_scope"]
