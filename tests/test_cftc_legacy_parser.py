from __future__ import annotations

from pathlib import Path

import pytest

from barrot_agent.evolution.cftc_legacy import (
    CFTCLegacyParseError,
    parse_cftc_legacy_futures_only_report,
)


REPORT = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "cftc_legacy_xrp_20261103.html"
).read_text(encoding="utf-8")

STATUS_HTML = """<html><body>
<h2>New Futures Markets Added This Week</h2>
<table><tr><td>123456</td><td>EXAMPLE NEW FUTURE</td></tr></table>
<h2>Futures Markets Dropped From Reporting This Week</h2>
<table><tr><td>176740</td><td>XRP - CHICAGO MERCANTILE EXCHANGE</td></tr></table>
<h2>New Futures and Options Combined Markets Added This Week</h2>
<table><tr><td>234567</td><td>EXAMPLE COMBINED FUTURE</td></tr></table>
<h2>New Futures and Options Combined Markets Dropped From Reporting This Week</h2>
<table><tr><td>176740</td><td>XRP - CHICAGO MERCANTILE EXCHANGE</td></tr></table>
<h2>Reports Dated November 03, 2026</h2>
</body></html>"""


def test_legacy_futures_only_parser_reconciles_xrp_positions_changes_and_concentration():
    contract = parse_cftc_legacy_futures_only_report(REPORT)["contract"]
    assert contract["reporting_status"] == "reported"
    assert contract["code"] == "176740"
    assert contract["positions_as_of_date"] == "2026-11-03"
    assert contract["contract_multiplier_xrp"] == 50_000
    assert contract["open_interest_contracts"] == 7_216
    assert contract["open_interest_xrp_equivalent"] == 360_800_000
    assert contract["open_interest_change_contracts"] == -845
    assert contract["open_interest_change_xrp_equivalent"] == -42_250_000
    assert contract["change_from_date"] == "2026-10-27"
    assert contract["total_traders"] == 29
    assert contract["positions"]["non_commercial"]["net_long_short_contracts"] == 1_465
    assert contract["positions"]["non_commercial"]["net_long_short_change_contracts"] == 185
    assert contract["positions"]["commercial"]["net_long_short_contracts"] == -1_322
    assert contract["positions"]["commercial"]["net_long_short_change_contracts"] == -53
    assert contract["positions"]["nonreportable"]["net_long_short_contracts"] == -143
    assert contract["positions"]["nonreportable"]["net_long_short_change_contracts"] == -132
    assert contract["positions"]["reportable_total"]["long_contracts"] == 7_132
    assert contract["positions"]["reportable_total"]["short_contracts"] == 6_989
    assert contract["position_reconciliation_status"] == "passed"
    assert contract["change_reconciliation_status"] == "passed"
    assert contract["concentration"]["gross_4_or_less_long_pct"] == 81.0
    assert contract["concentration"]["gross_4_or_less_short_pct"] == 67.4
    assert contract["concentration"]["gross_8_or_less_long_pct"] == 95.1
    assert contract["concentration"]["net_8_or_less_short_pct"] == 87.5


def test_legacy_futures_only_parser_preserves_suppressed_changes_as_null():
    contract = parse_cftc_legacy_futures_only_report(REPORT.replace("-281", ".", 1))["contract"]
    assert contract["open_interest_change_contracts"] == -845
    assert contract["positions"]["non_commercial"]["long_change_contracts"] is None
    assert contract["positions"]["non_commercial"]["net_long_short_change_contracts"] is None
    assert contract["change_reconciliation_status"] == "not_verifiable_suppressed_values"


def test_legacy_futures_only_parser_rejects_open_interest_reconciliation_mismatch():
    corrupted = REPORT.replace("All  :     7,216:", "All  :     7,217:", 1)
    with pytest.raises(CFTCLegacyParseError, match="do not reconcile to open interest"):
        parse_cftc_legacy_futures_only_report(corrupted)


def test_legacy_futures_only_parser_rejects_weekly_change_reconciliation_mismatch():
    corrupted = REPORT.replace("-845", "-844", 1)
    with pytest.raises(CFTCLegacyParseError, match="do not reconcile to open-interest change"):
        parse_cftc_legacy_futures_only_report(corrupted)


def test_legacy_futures_only_parser_rejects_wrong_contract_multiplier():
    corrupted = REPORT.replace("Contracts of 50,000 XRP", "Contracts of 10,000 XRP", 1)
    with pytest.raises(CFTCLegacyParseError, match="multiplier differs"):
        parse_cftc_legacy_futures_only_report(corrupted)


def test_legacy_futures_only_parser_rejects_contract_status_date_mismatch():
    stale = STATUS_HTML.replace("November 03, 2026", "October 27, 2026")
    with pytest.raises(CFTCLegacyParseError, match="does not match the Futures-Only report date"):
        parse_cftc_legacy_futures_only_report(REPORT, stale)


def test_missing_legacy_contract_is_never_zero_filled():
    without_xrp = REPORT.replace(
        "XRP - CHICAGO MERCANTILE EXCHANGE",
        "BITCOIN - CHICAGO MERCANTILE EXCHANGE",
        1,
    ).replace("Code-176740", "Code-133741", 1).replace(
        "Contracts of 50,000 XRP", "Contracts of 5 Bitcoin", 1
    )
    unknown = parse_cftc_legacy_futures_only_report(without_xrp)["contract"]
    dropped = parse_cftc_legacy_futures_only_report(without_xrp, STATUS_HTML)["contract"]
    assert unknown["reporting_status"] == "not_reported_status_unverified"
    assert dropped["reporting_status"] == "dropped_from_reporting"
    for contract in (unknown, dropped):
        assert contract["open_interest_contracts"] is None
        assert contract["open_interest_xrp_equivalent"] is None
        assert contract["positions"] is None
        assert contract["model_eligible"] is False


def test_legacy_futures_only_parser_rejects_duplicate_xrp_sections():
    with pytest.raises(CFTCLegacyParseError, match="duplicate XRP CME sections"):
        parse_cftc_legacy_futures_only_report(REPORT + REPORT)
