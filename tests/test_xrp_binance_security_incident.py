"""Regression tests for the Binance security-incident XRP evidence overlay."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261104T191500Z-binance-security-incident-xrp-flow-and-recovery.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_primary_incident_and_fbi_attribution_remain_distinct():
    data = load()
    sources = {item["source_id"]: item for item in data["sources"]}
    claims = {item["claim_id"]: item for item in data["claims"]}
    incident = claims["BINANCE-INCIDENT-ESTIMATE"]
    assert incident["amount_usd"] == 6_300_000_000
    assert incident["source_ids"] == ["BINANCE-INCIDENT-UPDATE-2"]
    assert "no evidence" in " ".join(incident["limitations"]).lower()
    attribution = claims["FBI-ATTRIBUTION"]
    assert attribution["source_ids"] == ["FBI-TRADERTRAITOR-ADVISORY"]
    assert attribution["counterclaim_source_ids"] == ["REUTERS-NORTH-KOREA-DENIAL"]
    assert sources["FBI-TRADERTRAITOR-ADVISORY"]["source_independence_group"] != sources["BINANCE-INCIDENT-UPDATE-2"]["source_independence_group"]


def test_xrp_transfers_preserve_timestamp_conflict_and_provider_label_limits():
    data = load()
    claims = {item["claim_id"]: item for item in data["claims"]}
    first = claims["XRP-TRANSFER-3AAA"]
    second = claims["XRP-TRANSFER-DC8D"]
    assert first["amount_xrp"] == 40_000_000
    assert first["event_time_utc"] == "2026-11-02T03:56:21Z"
    assert first["transaction_hash"].startswith("3AAA")
    assert first["sender_address"] == "rK21t6nGLy4MNDqhvy3pGwcLFy25qgfzMx"
    assert first["receiver_address"] == "rhXtRtpfZRAKVayWd5Z5kRJ2YXYkcuxNRD"
    assert first["attribution_status"] == "provider_label_not_identity_proof"
    assert first["sale_evidenced"] is False
    assert first["exchange_deposit_evidenced"] is False
    assert second["amount_xrp"] == 40_000_000
    assert second["event_time_utc"] is None
    assert second["timestamp_conflict"]
    assert second["transaction_hash"].startswith("DC8D")
    assert "03:55:31" in second["timestamp_conflict"]


def test_separate_binance_50m_transfer_is_not_added_to_hack_linked_xrp():
    data = load()
    claims = {item["claim_id"]: item for item in data["claims"]}
    separate = claims["SEPARATE-50M-XRP-TRANSFER"]
    assert separate["amount_xrp"] == 50_000_000
    assert separate["include_in_hack_total"] is False
    assert separate["status"] == "not_linked_to_exploit"


def test_recovery_updates_distinguish_xrp_backing_rlusd_network_and_aggregate_replenishment():
    data = load()
    claims = {item["claim_id"]: item for item in data["claims"]}
    backing = claims["BINANCE-RECOVERY-UPDATE-3-XRP-BACKING"]
    assert "XRP" in backing["assets_reported_100pct_backed"]
    xrpl = claims["BINANCE-RECOVERY-UPDATE-6-XRPL-RLUSD"]
    assert xrpl["network"] == "XRP"
    assert xrpl["asset"] == "RLUSD"
    assert "native XRP withdrawals" in " ".join(xrpl["limitations"])
    recovery = claims["BINANCE-RECOVERY-UPDATE-7-98PCT"]
    assert recovery["replenished_pct"] == 98
    assert recovery["remaining_pct"] == 2
    assert recovery["por_covered_token_count"] == 44
    assert recovery["proof_generation_estimate_hours"] == [50, 60]


def test_artifact_is_research_only_and_preserves_source_quality_gaps():
    data = load()
    quality = data["data_quality"]
    assert data["forecast_issued"] is False
    assert data["prediction_status"] == "NOT_ISSUED"
    assert data["model_eligible"] is False
    assert quality["raw_bytes_retained"] is False
    assert quality["raw_source_sha256"] is None
    assert quality["second_transfer_timestamp_verified"] is False
    assert quality["recipient_exchange_attribution_verified"] is False
    assert quality["whale_alert_and_secondary_article_independent"] is False
    assert sum(item["amount_xrp"] for item in data["claims"] if item["claim_id"] in {"XRP-TRANSFER-3AAA", "XRP-TRANSFER-DC8D"}) == 80_000_000
