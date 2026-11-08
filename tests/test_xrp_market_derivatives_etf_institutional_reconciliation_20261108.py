from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T090727Z-xrp-market-etf-derivatives-institutional-reconciliation.json"
CORRECTION = ROOT / "research" / "xrp_intelligence" / "20261108T090727Z-xrp-source-vintage-and-hash-correction.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def load_correction() -> dict:
    return json.loads(CORRECTION.read_text(encoding="utf-8"))


def test_all_source_excerpt_hashes_match_or_have_append_only_correction():
    data = load_artifact()
    correction = load_correction()
    corrections = {row["source_id"]: row for row in correction["hash_corrections"]}
    ids = [row["source_id"] for row in data["source_receipts"]]
    assert len(ids) == len(set(ids))
    for row in data["source_receipts"]:
        actual = hashlib.sha256(row["excerpt"].encode("utf-8")).hexdigest()
        overlay = corrections.get(row["source_id"])
        if overlay:
            assert row["excerpt_sha256"] == overlay["prior_excerpt_sha256"]
            assert actual == overlay["corrected_excerpt_sha256"]
            assert overlay["excerpt_changed"] is False
        else:
            assert actual == row["excerpt_sha256"]
    for row in correction["source_receipts"]:
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


def test_source_vintage_overlay_quarantines_fundingrates_search_snippet():
    correction = load_correction()
    funding = correction["source_vintage_corrections"]["fundingrates_app"]
    assert funding["previous_search_snippet_claimed_as_of_utc"] == "2026-11-08T06:20:51.267Z"
    assert funding["rendered_page_as_of_utc"] == "2026-11-03T09:00:54.233Z"
    assert funding["disposition"] == "QUARANTINED_UNVERIFIED_SEARCH_SNIPPET"
    assert correction["latest_secondary_observations"]["fundingrates_app_current_cutoff"] == "UNVERIFIED_NO_NOV8_OBSERVATION"


def test_later_kodexius_and_undated_xrpinsights_observations_do_not_overwrite_history():
    correction = load_correction()
    kod = correction["source_vintage_corrections"]["kodexius"]
    assert kod["previous_open_interest_usd"] == 775_070_000
    assert kod["new_open_interest_usd"] == 785_200_000
    assert kod["new_snapshot_as_of_utc"] == "2026-11-08T08:29:00Z"
    insights = correction["source_vintage_corrections"]["xrp_insights"]
    assert insights["current_dashboard_undated_aum_usd"] == 1_407_230_000
    assert insights["current_dashboard_undated_xrp_locked"] == 1_195_180_000
    assert "separate undated observation" in insights["interpretation"]


def test_forecast_and_external_actions_remain_disabled():
    data = load_artifact()
    correction = load_correction()
    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert correction["model_admission"]["eligible"] is False
    assert correction["forecast"]["status"] == "NOT_ISSUED"
    assert correction["external_actions"] == {
        "paper_trade": False,
        "real_money": False,
        "external_model_transfer": False,
    }
    assert len(data["competing_hypotheses"]) >= 5
