from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T200308Z-evernorth-sbi-ownership-cross-filing-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_later_424b3_is_latest_published_sbi_ownership_schedule() -> None:
    artifact = load_artifact()
    latest = artifact["latest_published_schedule"]
    assert latest["filing_date"] == "2026-10-30"
    assert latest["sbi_class_a_shares"] == 9_431_914
    assert latest["sbi_class_c_shares"] == 2_359_038
    assert latest["sbi_pubco_common_stock_percent"] == 21.4
    assert latest["sbi_voting_power_percent"] == 39.9
    assert latest["sbi_company_units"] == 0
    assert "not a majority holder" in latest["interpretation"]
    assert "SBI Holdings, Inc." in latest["sbi_entity_definition"]


def test_earlier_8k_snapshot_is_preserved_without_overwriting() -> None:
    prior = load_artifact()["prior_closing_schedule"]
    assert prior["filing_date"] == "2026-10-13"
    assert prior["sbi_class_a_shares"] == 8_885_293
    assert prior["sbi_class_c_shares"] == 2_905_659
    assert prior["sbi_percent_of_class_a"] == 39.9
    assert prior["sbi_percent_of_class_c"] == 9.0


def test_cross_filing_class_allocation_difference_is_explicit_and_unresolved() -> None:
    reconciliation = load_artifact()["reconciliation"]
    assert reconciliation["aggregate_sbi_class_a_plus_class_c_shares_in_both_filings"] == (
        11_790_952
    )
    assert reconciliation["class_a_increase_in_later_424b3"] == 546_621
    assert reconciliation["class_c_decrease_in_later_424b3"] == 546_621
    assert reconciliation["status"] == "UNRESOLVED_CROSS_FILING_CAP_TABLE_DIFFERENCE"
    assert "No explicit bridge" in reconciliation["conclusion"]


def test_latest_ownership_table_common_stock_and_voting_percentages_reconcile() -> None:
    holders = load_artifact()["latest_table_other_holders"]
    common = sum(item["common_stock_percent"] for item in holders.values())
    voting = sum(item["voting_power_percent"] for item in holders.values())
    assert round(common, 1) == 100.0
    assert round(voting, 1) == 100.0
    assert holders["sponsor"]["common_stock_percent"] == 61.4
    assert holders["sponsor"]["voting_power_percent"] == 19.9
    assert holders["spac_public_shareholders"]["voting_power_percent"] == 20.5


def test_sbi_stake_is_indirect_xrp_treasury_exposure_not_direct_xrp_ownership() -> None:
    relevance = load_artifact()["prediction_relevance"]
    assert "not the same as SBI Holdings directly holding" in relevance["xrp_direct_holding"]
    assert relevance["forecast_admission"] is False
    assert relevance["forecast_status"] == "NOT_ISSUED"


def test_source_excerpt_hashes_match() -> None:
    artifact = load_artifact()
    assert len(artifact["source_receipts"]) == 3
    for receipt in artifact["source_receipts"]:
        actual = hashlib.sha256(
            receipt["captured_excerpt_text"].encode("utf-8")
        ).hexdigest()
        assert actual == receipt["captured_excerpt_sha256"], receipt["source_id"]
