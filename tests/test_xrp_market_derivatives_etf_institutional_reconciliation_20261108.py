from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T090727Z-xrp-market-etf-derivatives-institutional-reconciliation.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_source_excerpt_hashes_match():
    data = load_artifact()
    ids = [row["source_id"] for row in data["source_receipts"]]
    assert len(ids) == len(set(ids))
    for row in data["source_receipts"]:
        assert hashlib.sha256(row["excerpt"].encode("utf-8")).hexdigest() == row["excerpt_sha256"]


def test_spot_timestamp_absence_is_not_imputed():
    data = load_artifact()
    spot = data["market_observations"]["spot"]
    assert spot["provider_event_timestamp_utc"] is None
    assert spot["retrieval_time_utc"] is None
    assert spot["eligibility"] == "RESEARCH_ONLY_TIMESTAMP_MISSING"
    assert data["data_quality"]["synchronized_market_cutoff"] is False


def test_derivatives_oi_and_funding_universes_remain_separate():
    data = load_artifact()
    rows = data["market_observations"]["derivatives"]["provider_observations"]
    oi = {row["provider"]: row["open_interest_usd"] for row in rows}
    assert oi["TradRadar"] == 1_910_000_000
    assert oi["Liqwall"] == 1_380_000_000
    assert oi["Bentley Markets"] == 1_620_000_000
    assert oi["Kodexius"] == 775_070_000
    assert data["market_observations"]["derivatives"]["cross_provider_reconciliation"]["status"] == "UNRESOLVED_DO_NOT_AVERAGE"
    assert data["market_observations"]["derivatives"]["cross_provider_reconciliation"]["oi_change_sign_disagreement"] is True


def test_etf_flow_partial_coverage_and_future_vintage_are_quarantined():
    data = load_artifact()
    providers = {row["provider"]: row for row in data["market_observations"]["etf_flows"]["providers"]}
    assert providers["CryptoKeyhole"]["nov6_coverage"] == "3 of 4; Franklin Templeton XRPZ missing"
    assert providers["CryptoKeyhole"]["future_issuer_file_stamp_quarantined"] is True
    assert providers["Alpha Finance"]["nov6_flow_usd"] == 0
    assert providers["XRP Insights"]["nov6_flow_xrp"] == -663_043
    assert "not independent confirmations" in data["market_observations"]["etf_flows"]["source_independence"]


def test_institutional_access_is_not_mislabeled_as_xrp_capital_flow():
    data = load_artifact()
    rel = data["institutional_relationships"]
    assert "RLUSD collateral use on Coinbase Global Exchange" in rel["ripple_coinbase_rlusd"]["future_at_launch"]
    assert rel["bny_ripple_custody"]["status"] == "CUSTODY_SUPPORT_ANNOUNCED"
    assert "different accounting line items" in rel["circle_coinbase_q3_2026"]["reconciliation"]
    assert "not XRP purchases" in rel["circle_coinbase_q3_2026"]["xrp_implication"]


def test_forecast_and_external_actions_remain_disabled():
    data = load_artifact()
    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["external_actions"] == {
        "paper_trade": False,
        "real_money": False,
        "external_model_transfer": False,
    }
    assert len(data["competing_hypotheses"]) >= 5
