from __future__ import annotations

import pytest

from barrot_agent.evolution.cftc_tff import (
    CFTCTFFParseError,
    parse_cftc_contract_status,
    parse_cftc_tff_report,
)


REPORT = """<html><title>CFTC Traders in Financial Futures</title><pre>
Traders in Financial Futures - Futures Only Positions as of November 3, 2026
XRP - CHICAGO MERCANTILE EXCHANGE (Contracts of 50,000 XRP)
CFTC Code #176740 Open Interest is 7,216
Positions
4,228 4,431 17 868 802 21 1,976 1,696 22 0 0 0 84 227
Changes from: October 27, 2026 Total Change is: -845
163 -210 0 -53 36 20 -410 -258 -501 0 0 0 -64 68
NANO XRP - COINBASE DERIVATIVES, LLC (500 XRP x $2.00 = $1000)
CFTC Code #176LM1 Open Interest is 32,505
Positions
0 0 0 0 0 0 29,317 31,625 120 2,693 601 0 375 159
Changes from: October 27, 2026 Total Change is: -32,864
0 0 0 0 0 0 -26,142 -28,053 -4,911 -1,607 28 0 -204 72
NANO XRP PERP STYLE - COINBASE DERIVATIVES, LLC (500 XRP x $2.00 = $1000)
CFTC Code #176LM3 Open Interest is 38,392
Positions
0 0 0 0 0 0 1,780 29,554 0 28,858 2,853 0 7,754 5,985
Changes from: October 27, 2026 Total Change is: -465
0 0 0 0 0 0 82 -1,313 0 -1,217 753 0 670 95
</pre></html>"""

HISTORICAL_REPORT = (
    REPORT.replace("October 27, 2026", "October 20, 2026")
    .replace("November 3, 2026", "October 27, 2026")
)

XRL_SECTION = """ 
XRP - COINBASE DERIVATIVES, LLC (10,000 XRP x $2.00 = $20,000)
CFTC Code #176LM2 Open Interest is 28,246
Positions
21,310 73 0 1,800 0 0 801 12,942 4,325 0 8,330 0 10 2,576
Changes from: October 20, 2026 Total Change is: .
. . . . . . . . . . . . . .
Percent of Open Interest Represented by Each Category of Trader
75.4 0.3 0.0 6.4 0.0 0.0 2.8 45.8 15.3 0.0 29.5 0.0 0.0 9.1
Number of Traders in Each Category Total Traders: 20
. . 0 . 0 0 4 11 5 0 . 0
"""

STATUS_HTML = """<html><body>
<h2>New Futures Markets Added This Week</h2>
<table><tr><td>123456</td><td>EXAMPLE NEW FUTURE</td></tr></table>
<h2>Futures Markets Dropped From Reporting This Week</h2>
<table><tr><td>176LM2</td><td>XRP - COINBASE DERIVATIVES, LLC</td></tr></table>
<h2>New Futures and Options Combined Markets Added This Week</h2>
<table><tr><td>234567</td><td>EXAMPLE COMBINED FUTURE</td></tr></table>
<h2>New Futures and Options Combined Markets Dropped From Reporting This Week</h2>
<table><tr><td>176LM2</td><td>XRP - COINBASE DERIVATIVES, LLC</td></tr></table>
<h2>Reports Dated November 03, 2026</h2>
</body></html>"""


def test_cftc_tff_parser_reconciles_three_xrp_contracts_and_categories() -> None:
    result = parse_cftc_tff_report(REPORT)
    contracts = {item["slug"]: item for item in result["contracts"]}

    assert result["positions_as_of_date"] == "2026-11-03"
    assert result["timestamp_precision"] == "date_only"
    assert result["model_eligible"] is False
    assert result["reported_contract_count"] == 3
    assert result["reported_xrp_equivalent_open_interest_total"] == 396_248_500
    assert contracts["cme_xrp"]["open_interest_contracts"] == 7216
    assert contracts["cme_xrp"]["open_interest_change_contracts"] == -845
    assert contracts["cme_xrp"]["open_interest_xrp_equivalent"] == 360_800_000
    assert contracts["coinbase_nano_xrp"]["open_interest_contracts"] == 32505
    assert contracts["coinbase_nano_xrp"]["open_interest_change_contracts"] == -32864
    assert contracts["coinbase_nano_xrp"]["contract_multiplier_xrp"] == 500
    assert contracts["coinbase_nano_xrp"]["positions"]["leveraged_funds"]["net_long_short_contracts"] == -2308
    assert contracts["coinbase_nano_xrp_perp_style"]["open_interest_contracts"] == 38392
    assert contracts["coinbase_nano_xrp_perp_style"]["positions"]["other_reportables"]["net_long_short_contracts"] == 26005
    assert contracts["coinbase_xrl_standard"]["reporting_status"] == "not_reported_status_unverified"
    assert contracts["coinbase_xrl_standard"]["open_interest_contracts"] is None
    assert contracts["coinbase_xrl_standard"]["open_interest_xrp_equivalent"] is None


def test_cftc_contract_status_distinguishes_futures_only_and_combined_universe() -> None:
    status = parse_cftc_contract_status(STATUS_HTML)

    assert status["futures_only_added"] == ["123456"]
    assert status["futures_only_dropped"] == ["176LM2"]
    assert status["futures_and_options_combined_added"] == ["234567"]
    assert status["futures_and_options_combined_dropped"] == ["176LM2"]


def test_absent_optional_contract_is_dropped_only_with_primary_status_evidence() -> None:
    result = parse_cftc_tff_report(REPORT, STATUS_HTML)
    contracts = {item["slug"]: item for item in result["contracts"]}
    xrl = contracts["coinbase_xrl_standard"]

    assert xrl["reporting_status"] == "dropped_from_reporting"
    assert xrl["open_interest_contracts"] is None
    assert xrl["open_interest_xrp_equivalent"] is None
    assert xrl["open_interest_change_contracts"] is None
    assert xrl["total_traders"] is None
    assert xrl["positions"] is None
    assert result["contract_status"]["futures_only_dropped"] == ["176LM2"]


def test_historical_xrl_dot_changes_and_trader_count_are_preserved_as_null_and_count() -> None:
    result = parse_cftc_tff_report(HISTORICAL_REPORT + XRL_SECTION)
    contracts = {item["slug"]: item for item in result["contracts"]}
    xrl = contracts["coinbase_xrl_standard"]

    assert result["positions_as_of_date"] == "2026-10-27"
    assert xrl["reporting_status"] == "reported"
    assert xrl["open_interest_contracts"] == 28_246
    assert xrl["contract_multiplier_xrp"] == 10_000
    assert xrl["open_interest_xrp_equivalent"] == 282_460_000
    assert xrl["open_interest_change_contracts"] is None
    assert xrl["total_traders"] == 20
    assert xrl["positions"]["dealer_intermediary"]["long_change_contracts"] is None
    assert xrl["positions"]["leveraged_funds"]["net_long_short_change_contracts"] is None


def test_cftc_tff_parser_rejects_open_interest_reconciliation_mismatch() -> None:
    corrupted = REPORT.replace("Open Interest is 7,216", "Open Interest is 7,217", 1)
    with pytest.raises(CFTCTFFParseError, match="do not reconcile to open interest"):
        parse_cftc_tff_report(corrupted)


def test_cftc_tff_parser_rejects_incomplete_position_row() -> None:
    corrupted = REPORT.replace(
        "4,228 4,431 17 868 802 21 1,976 1,696 22 0 0 0 84 227",
        "4,228 4,431 17 868 802 21 1,976 1,696 22 0 0 0 84",
        1,
    )
    with pytest.raises(CFTCTFFParseError, match="incomplete numeric rows"):
        parse_cftc_tff_report(corrupted)


def test_cftc_tff_parser_rejects_missing_required_xrp_contract_section() -> None:
    corrupted = REPORT.split("NANO XRP - COINBASE DERIVATIVES, LLC", 1)[0]
    with pytest.raises(CFTCTFFParseError, match="missing contract 176LM1"):
        parse_cftc_tff_report(corrupted)
