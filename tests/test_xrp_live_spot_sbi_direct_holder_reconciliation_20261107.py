from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T203431Z-xrp-live-spot-and-sbi-direct-holder-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_rendered_primary_api_response_hashes_match() -> None:
    artifact = load_artifact()
    receipts = {item["source_id"]: item for item in artifact["source_receipts"]}
    for source_id in ("kraken_xrpusd_ticker", "okx_xrpusdt_ticker"):
        receipt = receipts[source_id]
        assert receipt["raw_capture_status"] == "rendered_response_text_only"
        assert receipt["raw_wire_bytes_and_headers_retained"] is False
        assert hashlib.sha256(receipt["raw_response_text"].encode("utf-8")).hexdigest() == receipt["raw_response_sha256"]


def test_live_market_snapshot_fails_closed_on_timestamp_quality() -> None:
    artifact = load_artifact()
    market = artifact["market_snapshot"]
    kraken = market["observations"]["kraken"]
    okx = market["observations"]["okx"]
    assert kraken["timestamp_status"] == "NOT_SUPPLIED"
    assert kraken["model_eligible"] is False
    assert okx["age_seconds_at_reference_clock"] > market["freshness_limit_seconds"]
    assert okx["timestamp_status"] == "STALE"
    assert okx["model_eligible"] is False
    assert market["reconciliation"]["raw_difference_is_arbitrage_signal"] is False
    assert market["reconciliation"]["order_book_depth"]["executable_multi_level_depth_admitted"] is False


def test_sbi_holdings_usa_form3_is_not_double_counted() -> None:
    form3 = load_artifact()["sbi_evernorth_beneficial_ownership"]["sbi_holdings_usa_form3"]
    assert form3["direct_class_a_shares"] == 6_529_787
    assert form3["direct_class_c_shares"] == 1_633_180
    assert form3["class_c_underlying_class_a_shares"] == 1_633_180
    assert form3["underlying_class_a_included_in_table_i"] is False
    assert "One reporting person only" in form3["filing_scope"]


def test_sbi_group_residual_is_arithmetic_only_and_not_attributed() -> None:
    ownership = load_artifact()["sbi_evernorth_beneficial_ownership"]
    schedule = ownership["latest_published_schedule"]["pro_forma_at_closing"]
    direct = ownership["sbi_holdings_usa_form3"]
    residual = ownership["derived_residual_not_entity_specific"]
    assert schedule["sbi_group_class_a_shares"] - direct["direct_class_a_shares"] == residual["aggregate_class_a_minus_sbi_holdings_usa_direct_class_a"] == 2_902_127
    assert schedule["sbi_group_class_c_shares"] - direct["direct_class_c_shares"] == residual["aggregate_class_c_minus_sbi_holdings_usa_direct_class_c"] == 725_858
    assert residual["status"] == "ARITHMETIC_RESIDUAL_ONLY"
    assert "not assigned to any" in residual["limitation"]


def test_advance_funding_class_a_reconciles_to_other_subscriber_table() -> None:
    funding = load_artifact()["sbi_evernorth_beneficial_ownership"]["advance_funding_share_reconciliation"]
    assert funding["total_advance_funding_shares"] == funding["total_advance_funding_class_a"] + funding["sbi_group_class_c"]
    assert funding["total_advance_funding_class_a"] - funding["sbi_group_class_a"] == funding["non_sbi_advance_funding_class_a_residual"] == 1_237_722
    assert funding["non_sbi_advance_funding_class_a_residual"] + funding["delayed_funding_class_a_shares"] == funding["other_advance_and_delayed_subscribers_class_a_table_row"] == 2_316_335
    assert funding["status"] == "ARITHMETIC_RECONCILIATION"


def test_sbi_voting_power_and_common_stock_are_not_conflated() -> None:
    schedule = load_artifact()["sbi_evernorth_beneficial_ownership"]["latest_published_schedule"]
    closing = schedule["pro_forma_at_closing"]
    later = schedule["principal_securityholder_table_as_of_2026_10_22"]
    assert closing["sbi_voting_power_percent"] == 39.9
    assert closing["sbi_pubco_common_stock_percent"] == 21.4
    assert later["sbi_class_a_percent_of_class"] == 36.1
    assert later["sbi_class_c_percent_of_class"] == 7.5
    assert closing["total_class_a_shares"] != later["total_class_a_shares"]


def test_unresolved_ownership_allocation_and_oi_disagreement_are_preserved() -> None:
    artifact = load_artifact()
    ownership = artifact["sbi_evernorth_beneficial_ownership"]["prior_8k_vs_later_424b3"]
    assert ownership["aggregate_sbi_shares_both_filings"] == 11_790_952
    assert ownership["class_a_increase"] == ownership["class_c_decrease"] == 546_621
    assert ownership["status"] == "UNRESOLVED_CROSS_FILING_CLASS_ALLOCATION"
    oi = artifact["derivatives_and_etf_context"]["disagreement"]
    assert oi["open_interest_values_are_directly_comparable"] is False
    assert oi["status"] == "UNRESOLVED_PROVIDER_SCOPE_AND_TIMESTAMP_DIFFERENCE"


def test_all_sec_excerpt_hashes_and_forecast_boundary() -> None:
    artifact = load_artifact()
    receipts = {item["source_id"]: item for item in artifact["source_receipts"]}
    form3 = receipts["evernorth_sbi_holdings_usa_form3"]
    assert hashlib.sha256(form3["captured_excerpt_text"].encode("utf-8")).hexdigest() == form3["captured_excerpt_sha256"]
    prospectus = receipts["evernorth_424b3_ownership_and_advance_funding"]
    assert hashlib.sha256(prospectus["captured_excerpt_text"].encode("utf-8")).hexdigest() == prospectus["captured_excerpt_sha256"]
    assert hashlib.sha256(prospectus["advance_funding_excerpt_text"].encode("utf-8")).hexdigest() == prospectus["advance_funding_excerpt_sha256"]
    assert artifact["model_admission"]["admitted"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["paper_or_real_money_actions"] == "NONE"
