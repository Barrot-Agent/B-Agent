import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T090251Z-xrp-market-risk-off-and-capital-facility-source-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_exchange_raw_receipts_match_exact_sha256_and_byte_counts():
    artifact = load_artifact()
    for source in artifact["sources"]:
        raw = source["raw_json"].encode("utf-8")
        assert len(raw) == source["raw_bytes"]
        assert hashlib.sha256(raw).hexdigest() == source["sha256"]


def test_kraken_timestamp_absence_and_daily_open_semantics_are_preserved():
    kraken = load_artifact()["sources"][0]
    assert kraken["provider_timestamp_utc"] is None
    assert kraken["freshness"] == "UNVERIFIABLE_PROVIDER_TIMESTAMP_MISSING"
    assert kraken["metrics"]["daily_open_usd"] == 1.17749
    assert "not a rolling-24h open" in kraken["field_warning"]


def test_okx_timestamp_and_spread_recompute():
    artifact = load_artifact()
    okx = artifact["sources"][1]
    provider = datetime.fromisoformat(okx["provider_timestamp_utc"].replace("Z", "+00:00"))
    captured = datetime.fromisoformat(artifact["captured_at_utc"].replace("Z", "+00:00"))
    age = (captured - provider).total_seconds()
    assert abs(age - okx["provider_age_seconds"]) < 0.001
    assert age < okx["freshness_limit_seconds"]
    m = okx["metrics"]
    expected = (m["ask_usdt"] - m["bid_usdt"]) / ((m["ask_usdt"] + m["bid_usdt"]) / 2) * 10000
    assert abs(expected - m["spread_bps"]) < 1e-8


def test_binance_funding_is_stale_and_not_a_live_feature():
    source = load_artifact()["sources"][2]
    assert source["provider_age_seconds"] == 592.999
    assert source["freshness"] == "STALE_EXCEEDS_300_SECOND_LIMIT"
    assert source["metrics"]["funding_pct_per_8h"] == 0.007829
    assert load_artifact()["market_reconciliation"]["model_eligible"] is False


def test_cross_currency_gap_is_not_arbitrage_and_depth_is_not_inferred():
    artifact = load_artifact()
    m = artifact["market_reconciliation"]
    expected = (1.17702 / 1.176 - 1) * 100
    assert abs(expected - m["raw_kraken_usd_okx_usdt_last_gap_pct"]) < 1e-8
    assert "not executable arbitrage" in m["interpretation"]
    assert m["depth"] == "NOT_CAPTURED"


def test_liquidation_claim_is_secondary_and_preserves_upstream_lineage():
    claim = next(x for x in load_artifact()["secondary_claims"] if x["id"] == "xrp_liquidations_20261107")
    assert claim["values"]["total_usd"] == 16_750_000
    assert claim["values"]["long_usd"] == 16_010_000
    assert claim["values"]["short_usd"] == 746_000
    assert "CoinGlass -> U.Today -> CryptoTicker" in claim["source_lineage"]
    assert claim["status"] == "SECONDARY_ATTRIBUTION_ONLY"
    assert claim["model_eligible"] is False


def test_okx_positioning_claims_are_quarantined_for_link_target_mismatch():
    claim = next(x for x in load_artifact()["secondary_claims"] if x["id"] == "okx_positioning_claims_20261107")
    assert claim["link_findings"][0]["resolved_page"] == "Long-short ratio for Bitcoin"
    assert claim["link_findings"][0]["resolved_source"] == "Binance Futures"
    assert claim["link_findings"][1]["resolved_page"] == "Bitcoin open interest across five exchanges"
    assert claim["status"] == "QUARANTINED_PRIMARY_LINK_MISMATCH"
    assert claim["model_eligible"] is False


def test_etf_reposts_from_same_upstream_are_not_independent():
    claim = next(x for x in load_artifact()["secondary_claims"] if x["id"] == "xrp_etf_zero_flow_claim_20261107")
    assert claim["lineage"] == "SoSoValue -> CoinGape -> CryptoTicker"
    assert claim["status"] == "SECONDARY_SINGLE_UPSTREAM_FEED"


def test_future_dated_binance_outflow_claim_is_quarantined():
    claim = next(x for x in load_artifact()["secondary_claims"] if x["id"] == "future_dated_binance_outflow_claim_20261107")
    assert datetime.fromisoformat(claim["publication_date"]).date() < datetime(2026, 11, 9).date()
    assert claim["status"] == "QUARANTINED_FUTURE_DATED_EVENT"


def test_sec_eloc_capacity_is_not_misreported_as_actual_cash_raised():
    facility = load_artifact()["capital_reconciliation"]["evernorth_cantor_eloc"]
    assert facility["max_shares"] == 5_218_935
    assert facility["illustrative_max_gross_usd"] == 76_800_000
    assert facility["actual_draw_verified_usd"] is None
    assert facility["status"] == "OPTIONAL_CAPACITY_NOT_PROOF_OF_DRAW"
    assert facility["upfront_fee_usd"] == 521_893.5
    assert facility["fee_non_refundable_even_if_no_purchases"] is True


def test_pik_note_net_cash_is_separate_debt_and_coinbase_designation_is_scoped():
    capital = load_artifact()["capital_reconciliation"]
    note = capital["evernorth_pik_note"]
    assert note["principal_usd"] == 30_000_000
    assert note["net_cash_received_usd"] == 29_000_000
    assert note["classification"] == "ACTUAL_NET_DEBT_PROCEEDS_RECEIVED"
    assert note["xrp_use"] == "NOT_ESTABLISHED"
    coinbase = capital["coinbase_principal_market"]
    assert coinbase["scope"].startswith("Issuer-specific accounting")
    assert "Coinbase is the only or universal XRP venue" in coinbase["not_proof_of"]


def test_macro_release_is_point_in_time_and_not_xrp_causality():
    events = load_artifact()["macro_events"]
    bls = events[0]
    assert bls["event_time_utc"] == "2026-11-06T13:30:00Z"
    assert bls["metrics"]["payroll_change"] == 165_000
    assert bls["metrics"]["unemployment_pct"] == 4.1
    assert bls["xrp_causality"] == "NOT_ESTABLISHED"
    assert "Published before the BLS" in events[1]["limits"][1]


def test_kamilah_candidate_stays_unverified_and_no_forecast_or_external_action_occurs():
    artifact = load_artifact()
    assert artifact["identity_updates"]["kamilah_youtube"]["identity"] == "UNVERIFIED"
    assert artifact["identity_updates"]["kamilah_youtube"]["video_inventory"] == "NOT_PERFORMED_IDENTITY_GATE_NOT_MET"
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["directional_forecast"] is None
    assert all(value is False for value in artifact["external_actions"].values())
