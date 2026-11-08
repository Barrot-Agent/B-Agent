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


def test_initial_etf_artifact_preserves_its_original_file_date_assessment():
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


def test_primary_issuer_etf_observations_preserve_each_publisher_cutoff():
    path = ROOT / "research" / "xrp_intelligence" / "20261108T090727Z-xrp-etf-primary-issuer-holdings-reconciliation.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    issuers = {row["ticker"]: row for row in data["issuer_observations"]}
    assert issuers["GXRP"]["as_of_date"] == "2026-11-06"
    assert issuers["GXRP"]["xrp_units"] == 64_838_291.2993
    assert issuers["TOXR"]["xrp_units"] is None
    assert issuers["XRPZ"]["as_of_date"] == "2026-11-04"
    assert issuers["XRP"]["as_of_date"] == "2026-11-05"
    assert issuers["XRPC"]["nov6_daily_nav_table"]["shares_outstanding"] == 22_990_000
    assert issuers["XRPC"]["separate_holdings_section"]["shares_outstanding"] == 22_920_000
    assert issuers["XRPR"]["xrp_units"] is None


def test_canary_nov9_file_label_is_not_mislabeled_as_future_availability():
    data = json.loads(
        (ROOT / "research" / "xrp_intelligence" / "20261108T090727Z-xrp-etf-primary-issuer-holdings-reconciliation.json").read_text(encoding="utf-8")
    )
    correction = data["correction_to_prior_artifact"]
    assert correction["prior_interpretation"] == "QUARANTINED"
    assert correction["corrected_interpretation"] == (
        "FUTURE_FILE_DATE_LABEL_AVAILABLE_BEFORE_REFERENCE_TIME; "
        "EFFECTIVE_DATE_MAPPED_TO_2026-11-06_BY_PUBLISHER_METHOD"
    )
    windows = data["aggregator_reconciliation"]["file_availability_windows"]
    assert windows["canary_file_date_label"] == "2026-11-09"
    assert windows["canary_file_published_utc"][0] == "2026-11-07T05:07:00Z"
    assert windows["canary_effective_trading_date_by_publisher"] == "2026-11-06"


def test_crypto_keyhole_partial_flow_and_canary_share_conflict_are_not_resolved_by_assumption():
    data = json.loads(
        (ROOT / "research" / "xrp_intelligence" / "20261108T090727Z-xrp-etf-primary-issuer-holdings-reconciliation.json").read_text(encoding="utf-8")
    )
    partial = data["aggregator_reconciliation"]["nov6_partial"]
    assert partial["coverage"] == "3 of 4"
    assert partial["missing"] == "Franklin Templeton XRPZ"
    assert partial["partial_total_xrp"] == -752_048
    assert partial["complete_total"] is False
    assert data["primary_aggregator_disagreements"][0]["status"] == "UNRESOLVED_VINTAGE_AND_SHARE_COUNT_CONFLICT"


def test_grayscale_and_rex_are_not_silently_added_to_daily_spot_flow_universe():
    data = json.loads(
        (ROOT / "research" / "xrp_intelligence" / "20261108T090727Z-xrp-etf-primary-issuer-holdings-reconciliation.json").read_text(encoding="utf-8")
    )
    excluded = data["aggregator_reconciliation"]["excluded_from_daily_flow_universe"]
    assert "quarterly SEC holdings" in excluded["GXRP"]
    assert "not total underlying exposure" in excluded["XRPR"]
    assert data["data_quality"]["rex_total_underlying_xrp_unknown"] is True


def test_primary_issuer_excerpt_hashes_match():
    data = json.loads(
        (ROOT / "research" / "xrp_intelligence" / "20261108T090727Z-xrp-etf-primary-issuer-holdings-reconciliation.json").read_text(encoding="utf-8")
    )
    for row in data["source_receipts"]:
        assert hashlib.sha256(row["excerpt"].encode("utf-8")).hexdigest() == row["excerpt_sha256"]


def test_previous_future_stamp_interpretation_is_explicitly_superseded():
    data = json.loads(
        (ROOT / "research" / "xrp_intelligence" / "20261108T090727Z-xrp-etf-primary-issuer-holdings-reconciliation.json").read_text(encoding="utf-8")
    )
    assert data["correction_to_prior_artifact"]["artifact"] == (
        "20261108T090727Z-xrp-source-vintage-and-hash-correction.json"
    )
    assert "not future availability" in data["correction_to_prior_artifact"]["reason"]
    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"


def test_rex_is_mixed_direct_and_lookthrough_exposure_not_a_pure_spot_holding():
    path = ROOT / "research" / "xrp_intelligence" / "20261108T090727Z-xrpr-direct-and-lookthrough-exposure-correction.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    rex = data["rex_holdings"]
    assert rex["direct_xrp_units"] == 19_885_382
    assert rex["coinshares_etp_shares"] == 362_750
    assert rex["direct_xrp_pct"] == 59.49
    assert rex["coinshares_physical_xrp_pct"] == 40.49
    assert "not equivalent to investing directly in XRP" in rex["issuer_warning"]
    assert data["product_classification"]["corrected_label"] == (
        "Five direct XRP spot/ETP products, one mixed direct/indirect XRP-exposure fund, and one multi-asset index product."
    )


def test_xrpinsights_rex_amount_is_lookthrough_not_direct_custody():
    path = ROOT / "research" / "xrp_intelligence" / "20261108T090727Z-xrpr-direct-and-lookthrough-exposure-correction.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    look = data["lookthrough_reconciliation"]
    assert look["xrp_insights_reported_xrpr_lookthrough_xrp"] == 33_400_000
    assert look["rex_direct_xrp_units"] == 19_885_382
    assert look["implied_indirect_xrp_equivalent_from_dashboard"] == 13_514_618
    assert look["status"] == "SECONDARY_LOOKTHROUGH_ESTIMATE_NOT_PRIMARY_UNIT_DISCLOSURE"


def test_seven_product_aggregate_reconciliation_is_hypothesis_not_verified_total():
    path = ROOT / "research" / "xrp_intelligence" / "20261108T090727Z-xrpr-direct-and-lookthrough-exposure-correction.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    agg = data["aggregate_reconciliation_hypothesis"]
    assert agg["arithmetic_sum_xrp"] == 1_195_944_176.2993
    assert agg["xrp_insights_dashboard_total_xrp_undated"] == 1_195_180_000
    assert agg["difference_pct_of_dashboard"] < 0.1
    assert "not an exact verified total" in agg["interpretation"]


def test_primary_issuer_excerpts_hash_and_keep_rex_exclusion_method():
    path = ROOT / "research" / "xrp_intelligence" / "20261108T090727Z-xrpr-direct-and-lookthrough-exposure-correction.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for row in data["source_receipts"]:
        assert hashlib.sha256(row["excerpt"].encode("utf-8")).hexdigest() == row["excerpt_sha256"]
    ckh = data["source_receipts"][-1]["excerpt"]
    assert "neither its holdings nor a measure of its flows" in ckh
    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
