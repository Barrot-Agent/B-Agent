from __future__ import annotations

import hashlib
import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T211245Z-bny-custody-and-market-flow-data-quality-addendum.json"
)


def test_bny_and_market_flow_excerpt_receipts_are_content_addressed():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["captured_at_utc"] == "2026-11-06T21:12:45Z"
    assert len(artifact["sources"]) == 6

    for source in artifact["sources"]:
        excerpt = source["excerpt_text"].encode("utf-8")
        assert len(excerpt) == source["excerpt_bytes"]
        assert hashlib.sha256(excerpt).hexdigest() == source["excerpt_sha256"]
        assert source["hash_scope"].startswith(
            "SHA-256 of the stored page excerpt text"
        )
        assert source["raw_source_bytes_retained"] is False


def test_bny_primary_sources_keep_circle_and_ripple_relationships_separate():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    findings = {item["id"]: item for item in artifact["findings"]}

    assert findings["bny_ripple_direct_relationship"]["status"] == "issuer_confirmed"
    assert "primary reserve custodian for RLUSD" in findings["bny_ripple_direct_relationship"]["statement"]
    assert findings["bny_circle_direct_relationship"]["status"] == "issuer_confirmed"
    assert "primary custodian of USDC reserves" in findings["bny_circle_direct_relationship"]["statement"]
    assert "not evidence of a direct Circle-Ripple partnership" in (
        findings["bny_circle_direct_relationship"]["limits"][0]
    )
    assert findings["xrp_collateral_scope"]["status"] == "not_established"


def test_binance_and_etf_flow_disagreements_remain_unresolved_and_model_ineligible():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    findings = {item["id"]: item for item in artifact["findings"]}

    assert findings["binance_withdrawal_vs_reserve_balance"]["status"] == (
        "unreconciled_metrics_not_directly_contradictory"
    )
    assert findings["xrp_etf_flow_disagreement"]["status"] == (
        "unresolved_coverage_and_methodology_mismatch"
    )
    assert artifact["data_quality"]["model_eligibility"] == (
        "raw_only_pending_per_fund_and_exchange_flow_reconciliation"
    )
    assert artifact["data_quality"]["forecast_issued"] is False
