from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORRECTION = ROOT / "research" / "xrp_intelligence" / "20261106T031200Z-xrp-etf-provider-completeness-and-scope-correction.json"
SOURCE_ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T030136Z-xrp-spot-depth-exchange-wallet-etf-reconciliation.json"


def load_correction() -> dict:
    return json.loads(CORRECTION.read_text(encoding="utf-8"))


def test_maketo_nov4_zero_is_complete_and_oct24_is_the_missing_day():
    correction = load_correction()
    item = next(x for x in correction["corrections"] if x["correction_id"] == "MAKETO_NOV4_ZERO_IS_COMPLETE_NOV4_BLANK_DAY_IS_OCT24")
    values = item["additional_observations"]
    assert values["nov4_net_flow_usd"] == 0
    assert values["nov4_reporting_funds"] == values["nov4_total_funds"] == 5
    assert values["oct24_reporting_funds"] == 0
    assert values["oct24_total_funds"] == 5
    assert values["past_week_net_flow_usd"] == 7_400_000
    assert values["past_month_net_flow_usd"] == 18_000_000


def test_alpha_and_maketo_rolling_windows_are_not_averaged():
    data = load_correction()["cross_provider_etf_window_reconciliation"]
    alpha = data["alpha_finance"]
    maketo = data["maketo"]
    assert alpha["last_30_sessions_usd"] == 78_900_000
    assert maketo["past_month_usd"] == 18_000_000
    assert alpha["last_7_sessions_usd"] == 4_800_000
    assert maketo["past_week_usd"] == 7_400_000
    assert "not the same window" in data["interpretation"]


def test_corpstacking_nciq_inclusion_is_unresolved_not_asserted():
    item = next(x for x in load_correction()["corrections"] if x["correction_id"] == "CORPSTACKING_NCIQ_INCLUSION_IN_HEADLINE_TOTAL_UNRESOLVED")
    fields = item["corrected_fields"]
    assert fields["included_nciq_index_etf_in_headline_total"] == "UNRESOLVED"
    assert fields["methodology_says_index_funds_excluded"] is True
    assert fields["nciq_appears_in_largest_holders_list"] is True
    assert fields["status"] == "QUARANTINED_SCOPE_COUNT_AMBIGUITY"
    evernorth = item["stale_evernorth_note"]
    assert evernorth["later_reported_xrp_approximate"] == 473_000_000
    assert evernorth["later_reported_xrp_as_of"] == "2026-10-09"


def test_thexrpinvestor_is_search_extract_only_not_a_proven_internal_error():
    item = next(x for x in load_correction()["corrections"] if x["correction_id"] == "THEXRPINVESTOR_SEARCH_EXTRACT_NOT_ENOUGH_TO_PROVE_CATEGORY_ERROR")
    assert item["capture_status"] == "SEARCH_RESULT_ONLY_DIRECT_PAGE_UNREADABLE"
    assert item["observed_search_extract"]["products"] == 12
    assert item["observed_search_extract"]["category_sum"] == 11
    assert item["corrected_status"] == "UNVERIFIED_SEARCH_EXTRACT_SCOPE_GAP"
    assert item["model_eligible"] is False


def test_correction_is_bound_to_exact_original_blob_and_does_not_rewrite_it():
    correction = load_correction()
    source = correction["source_artifact"]
    original = json.loads(SOURCE_ARTIFACT.read_text(encoding="utf-8"))
    assert source["path"].endswith("20261106T030136Z-xrp-spot-depth-exchange-wallet-etf-reconciliation.json")
    assert source["git_blob_sha1"] == "200ce1ac5d5812b30d2e1e61a333539f14f1c814"
    assert source["correction_mode"] == "APPEND_ONLY_EXACT_BLOB_BOUND"
    assert source["original_artifact_modified"] is False
    assert original["artifact_id"] == "xrp_spot_depth_exchange_wallet_and_etf_vintage_reconciliation_20261106T030136Z"
    assert correction["model_eligibility"]["eligible"] is False
    assert correction["model_eligibility"]["forecast_issued"] is False
