import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261108T025908Z-binance-hack-xrp-ledger-and-market-reconciliation.json"
)
CORRECTION = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261108T031500Z-xrp-market-receipt-hash-correction.json"
)


def _load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _corrections():
    data = json.loads(CORRECTION.read_text(encoding="utf-8"))
    return {item["field_path"]: item for item in data["corrections"]}


def test_direct_exchange_receipts_hash_and_quarantine():
    data = _load()
    fixes = _corrections()
    assert data["artifact_type"] == "xrp_security_event_and_market_snapshot"
    assert data["captured_at_utc"] == "2026-11-08T02:59:08Z"
    venues = {item["source_id"]: item for item in data["market_snapshot"]["venue_observations"]}
    paths = {
        "kraken_xrp_usd_ticker": "market_snapshot.venue_observations[kraken_xrp_usd_ticker].raw_response_sha256",
        "okx_xrp_usdt_ticker": "market_snapshot.venue_observations[okx_xrp_usdt_ticker].raw_response_sha256",
    }
    for source_id, item in venues.items():
        fix = fixes[paths[source_id]]
        assert item["raw_response_sha256"] == fix["original_value"]
        digest = hashlib.sha256(item["raw_response"].encode("utf-8")).hexdigest()
        assert digest == fix["corrected_value"]
        assert item["model_eligible"] is False
    kraken = venues["kraken_xrp_usd_ticker"]
    okx = venues["okx_xrp_usdt_ticker"]
    assert kraken["provider_event_time_utc"] is None
    assert kraken["timestamp_quality"] == "unknown_provider_event_time"
    assert okx["provider_event_age_seconds"] > data["data_quality"]["freshness_threshold_seconds"]
    assert okx["timestamp_quality"] == "stale_over_300_seconds"
    assert abs(kraken["last_vs_daily_open_pct"] - (-0.6865461053)) < 1e-8
    assert abs(okx["last_vs_rolling_24h_open_pct"] - (-1.2730690362)) < 1e-8
    assert data["market_snapshot"]["derived_comparison"]["arbitrage_claim_permitted"] is False
    registry = next(item for item in data["source_registry"] if item["id"] == "kraken_xrp_usd_ticker")
    registry_fix = fixes["source_registry[kraken_xrp_usd_ticker].raw_body_hash"]
    assert registry["raw_body_hash"] == registry_fix["original_value"]
    assert registry_fix["corrected_value"] == "sha256:" + hashlib.sha256(kraken["raw_response"].encode("utf-8")).hexdigest()


def test_rendered_source_excerpt_hashes_are_preserved():
    data = _load()
    for source in data["source_registry"]:
        if "excerpt" in source:
            digest = hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest()
            assert digest == source["excerpt_sha256"]


def test_binance_xrp_theft_is_not_conflated_with_customer_replenishment():
    data = _load()
    claims = {item["id"]: item for item in data["claim_reconciliation"]}
    drain = claims["binance_xrp_drain"]
    replenishment = claims["binance_customer_replenishment"]
    assert "233.46M XRP" in drain["claim"]
    assert "not_recovery_proof" in replenishment["status"]
    assert "distinct from recovering the stolen XRP" in replenishment["limitations"][0]
    assert "rK21t6nGLy4MNDqhvy3pGwcLFy25qgfzMx" in claims["attacker_holding_account"]["claim"]


def test_misattributed_internal_sweep_is_not_accepted_as_recovery():
    data = _load()
    claim = next(item for item in data["claim_reconciliation"] if item["id"] == "utoday_internal_sweep")
    assert claim["status"] == "not_accepted_contradicted_by_sender_attribution"
    assert "No evidence establishes Binance control" in claim["limitations"][0]
    assert any("Recipient count is unresolved" in item["resolution"] for item in data["disagreements"] if item["id"] == "nov2_destination_count")


def test_source_independence_and_prediction_boundary_are_explicit():
    data = _load()
    source_ids = {item["id"] for item in data["source_registry"]}
    assert len(source_ids) == len(data["source_registry"])
    families = {item["id"]: item for item in data["source_independence"]["families"]}
    assert set(families["binance_official_incident_report"]["members"]) <= source_ids
    assert set(families["xrpl_public_ledger"]["members"]) <= source_ids
    assert data["prediction"]["issued"] is False
    assert data["prediction"]["status"] == "NOT_ISSUED"
    assert data["prediction"]["no_real_money_actions"] is True
    assert data["data_quality"]["source_disagreements_preserved"] is True
