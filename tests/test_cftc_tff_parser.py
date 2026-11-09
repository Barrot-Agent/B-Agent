from __future__ import annotations

import pytest

from barrot_agent.evolution.cftc_tff import CFTCTFFParseError, parse_cftc_tff_report


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


def test_cftc_tff_parser_reconciles_three_xrp_contracts_and_categories() -> None:
    result = parse_cftc_tff_report(REPORT)
    contracts = {item["slug"]: item for item in result["contracts"]}

    assert result["positions_as_of_date"] == "2026-11-03"
    assert result["timestamp_precision"] == "date_only"
    assert result["model_eligible"] is False
    assert contracts["cme_xrp"]["open_interest_contracts"] == 7216
    assert contracts["cme_xrp"]["open_interest_change_contracts"] == -845
    assert contracts["coinbase_nano_xrp"]["open_interest_contracts"] == 32505
    assert contracts["coinbase_nano_xrp"]["open_interest_change_contracts"] == -32864
    assert contracts["coinbase_nano_xrp"]["contract_multiplier_xrp"] == 500
    assert contracts["coinbase_nano_xrp"]["positions"]["leveraged_funds"]["net_long_short_contracts"] == -2308
    assert contracts["coinbase_nano_xrp_perp_style"]["open_interest_contracts"] == 38392
    assert contracts["coinbase_nano_xrp_perp_style"]["positions"]["other_reportables"]["net_long_short_contracts"] == 26005


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


def test_cftc_tff_parser_rejects_missing_xrp_contract_section() -> None:
    corrupted = REPORT.split("NANO XRP - COINBASE DERIVATIVES, LLC", 1)[0]
    with pytest.raises(CFTCTFFParseError, match="missing contract 176LM1"):
        parse_cftc_tff_report(corrupted)
