from __future__ import annotations

import html
import re
from datetime import datetime


class CFTCTFFParseError(ValueError):
    """Raised when a CFTC TFF XRP contract section cannot be reconciled."""


CFTC_CONTRACTS = (
    {
        "label": "XRP - CHICAGO MERCANTILE EXCHANGE",
        "code": "176740",
        "slug": "cme_xrp",
        "name": "XRP - Chicago Mercantile Exchange",
        "venue": "CME",
        "contract_multiplier_xrp": 50_000,
    },
    {
        "label": "NANO XRP - COINBASE DERIVATIVES, LLC",
        "code": "176LM1",
        "slug": "coinbase_nano_xrp",
        "name": "Nano XRP - Coinbase Derivatives",
        "venue": "Coinbase Derivatives",
        "contract_multiplier_xrp": 500,
    },
    {
        "label": "NANO XRP PERP STYLE - COINBASE DERIVATIVES, LLC",
        "code": "176LM3",
        "slug": "coinbase_nano_xrp_perp_style",
        "name": "Nano XRP Perp Style - Coinbase Derivatives",
        "venue": "Coinbase Derivatives",
        "contract_multiplier_xrp": 500,
    },
)

# This legacy XRP contract is optional in the current report. Its absence must
# be resolved against the CFTC weekly added/dropped-contract index, never zero-filled.
CFTC_OPTIONAL_CONTRACTS = (
    {
        "label": "XRP - COINBASE DERIVATIVES, LLC",
        "code": "176LM2",
        "slug": "coinbase_xrl_standard",
        "name": "XRP - Coinbase Derivatives",
        "venue": "Coinbase Derivatives",
        "contract_multiplier_xrp": 10_000,
    },
)

CFTC_POSITION_CATEGORIES = (
    ("dealer_intermediary", "Dealer/Intermediary", 0, 1, 2),
    ("asset_manager_institutional", "Asset Manager/Institutional", 3, 4, 5),
    ("leveraged_funds", "Leveraged Funds", 6, 7, 8),
    ("other_reportables", "Other Reportables", 9, 10, 11),
    ("nonreportable", "Nonreportable", 12, 13, None),
)


def _parse_integer(token: str, field: str) -> int:
    if not isinstance(token, str) or not re.fullmatch(
        r"-?(?:\d{1,3}(?:,\d{3})+|\d+)", token.strip()
    ):
        raise CFTCTFFParseError(f"{field} is not a valid integer")
    return int(token.replace(",", ""))


def _parse_optional_integer(token: str, field: str) -> int | None:
    if isinstance(token, str) and token.strip() == ".":
        return None
    return _parse_integer(token, field)


def _plain_text(html_text: str) -> str:
    cleaned = re.sub(r"(?is)<(script|style)\b[^>]*>.*?</\1>", " ", html_text)
    cleaned = re.sub(
        r"(?i)<br\s*/?>|</(?:pre|p|div|tr|td|th|h[1-6])\s*>",
        "\n",
        cleaned,
    )
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = html.unescape(cleaned).replace("\xa0", " ")
    return " ".join(
        " ".join(line.split()).upper()
        for line in cleaned.splitlines()
        if line.strip()
    )


def _codes_in_section(plain: str, start_heading: str, end_heading: str) -> list[str]:
    start = plain.find(start_heading)
    if start < 0:
        return []
    start += len(start_heading)
    end = plain.find(end_heading, start)
    if end < 0:
        end = len(plain)
    return list(dict.fromkeys(re.findall(r"\b[A-Z0-9]{6}\b", plain[start:end])))


def parse_cftc_contract_status(html_text: str) -> dict:
    """Parse the CFTC weekly futures-only and combined added/dropped contract index."""
    if not isinstance(html_text, str) or not html_text.strip():
        raise CFTCTFFParseError("CFTC contract-status HTML text must be non-empty")
    plain = _plain_text(html_text)
    combined_added_heading = "NEW FUTURES AND OPTIONS COMBINED MARKETS ADDED THIS WEEK"
    combined_dropped_heading = (
        "NEW FUTURES AND OPTIONS COMBINED MARKETS DROPPED FROM REPORTING THIS WEEK"
    )
    reports_heading = "REPORTS DATED "
    report_date_match = re.search(
        r"REPORTS DATED\\s+([A-Z]+\\s+\\d{1,2},\\s+\\d{4})", plain
    )
    report_date = None
    if report_date_match:
        try:
            report_date = datetime.strptime(
                report_date_match.group(1).title(), "%B %d, %Y"
            ).date().isoformat()
        except ValueError as exc:
            raise CFTCTFFParseError("CFTC contract-status report date is invalid") from exc
    return {
        "reports_dated": report_date,
        "futures_only_added": _codes_in_section(
            plain,
            "NEW FUTURES MARKETS ADDED THIS WEEK",
            "FUTURES MARKETS DROPPED FROM REPORTING THIS WEEK",
        ),
        "futures_only_dropped": _codes_in_section(
            plain,
            "FUTURES MARKETS DROPPED FROM REPORTING THIS WEEK",
            combined_added_heading,
        ),
        "futures_and_options_combined_added": _codes_in_section(
            plain, combined_added_heading, combined_dropped_heading
        ),
        "futures_and_options_combined_dropped": _codes_in_section(
            plain, combined_dropped_heading, reports_heading
        ),
    }


def _missing_optional_contract(spec: dict, contract_status: dict | None) -> dict:
    dropped = bool(
        contract_status
        and spec["code"] in contract_status.get("futures_only_dropped", [])
    )
    return {
        **spec,
        "reporting_status": (
            "dropped_from_reporting" if dropped else "not_reported_status_unverified"
        ),
        "open_interest_contracts": None,
        "open_interest_xrp_equivalent": None,
        "open_interest_change_contracts": None,
        "change_from_date": None,
        "total_traders": None,
        "positions": None,
        "model_eligible": False,
    }


def parse_cftc_tff_report(
    html_text: str, contract_status_html: str | None = None
) -> dict:
    """Parse XRP futures-only TFF sections without zero-filling dropped contracts.

    The result is deliberately research-only. CFTC TFF is a weekly, date-only
    futures-position report, not spot-flow, cash-capital, or collateral data.
    """
    if not isinstance(html_text, str) or not html_text.strip():
        raise CFTCTFFParseError("CFTC TFF HTML text must be non-empty")
    plain = _plain_text(html_text)
    as_of_match = re.search(r"POSITIONS AS OF\s+([A-Z]+\s+\d{1,2},\s+\d{4})", plain)
    if as_of_match is None:
        raise CFTCTFFParseError("CFTC TFF report has no positions-as-of date")
    try:
        as_of_date = datetime.strptime(as_of_match.group(1).title(), "%B %d, %Y").date()
    except ValueError as exc:
        raise CFTCTFFParseError("CFTC TFF positions-as-of date is invalid") from exc

    contract_status = (
        parse_cftc_contract_status(contract_status_html)
        if contract_status_html is not None
        else None
    )
    if contract_status is not None and contract_status["reports_dated"] != as_of_date.isoformat():
        raise CFTCTFFParseError(
            "CFTC contract-status report date does not match the TFF report date"
        )
    all_specs = CFTC_CONTRACTS + CFTC_OPTIONAL_CONTRACTS
    labels = [spec["label"] for spec in all_specs]
    required_codes = {spec["code"] for spec in CFTC_CONTRACTS}
    contracts = []

    for spec in all_specs:
        start = plain.find(spec["label"])
        if start < 0:
            if spec["code"] in required_codes:
                raise CFTCTFFParseError(
                    f"CFTC TFF report is missing contract {spec['code']}"
                )
            contracts.append(_missing_optional_contract(spec, contract_status))
            continue
        if plain.find(spec["label"], start + len(spec["label"])) >= 0:
            raise CFTCTFFParseError(
                f"CFTC TFF report has duplicate contract {spec['code']}"
            )
        next_starts = [
            plain.find(label, start + len(spec["label"]))
            for label in labels
            if label != spec["label"]
            and plain.find(label, start + len(spec["label"])) >= 0
        ]
        end = min(next_starts) if next_starts else len(plain)
        segment = plain[start:end]

        code_match = re.search(r"CFTC CODE #([A-Z0-9]+)", segment)
        oi_match = re.search(r"OPEN INTEREST IS\s+([\d,]+)", segment)
        positions_match = re.search(
            r"\bPOSITIONS\b\s+((?:-?\d[\d,]*\s+){14})CHANGES FROM:",
            segment,
        )
        changes_match = re.search(
            r"CHANGES FROM:\s+([A-Z]+\s+\d{1,2},\s+\d{4})\s+"
            r"TOTAL CHANGE IS:\s+(-?\d[\d,]*|\.)\s+"
            r"((?:(?:-?\d[\d,]*|\.)\s+){14})",
            segment,
        )
        if not (code_match and oi_match and positions_match and changes_match):
            raise CFTCTFFParseError(
                f"CFTC TFF contract {spec['code']} has incomplete numeric rows"
            )
        if code_match.group(1) != spec["code"]:
            raise CFTCTFFParseError(
                f"CFTC TFF contract code mismatch for {spec['label']}"
            )
        try:
            change_from_date = datetime.strptime(
                changes_match.group(1).title(), "%B %d, %Y"
            ).date()
        except ValueError as exc:
            raise CFTCTFFParseError(
                f"CFTC TFF contract {spec['code']} change-from date is invalid"
            ) from exc
        if change_from_date >= as_of_date:
            raise CFTCTFFParseError(
                f"CFTC TFF contract {spec['code']} change-from date is not earlier than report date"
            )

        position_tokens = re.findall(r"-?\d[\d,]*", positions_match.group(1))
        change_tokens = re.findall(r"-?\d[\d,]*|\.", changes_match.group(3))
        if len(position_tokens) != 14 or len(change_tokens) != 14:
            raise CFTCTFFParseError(
                f"CFTC TFF contract {spec['code']} must have exactly 14 position and change values"
            )
        positions = [_parse_integer(token, "position") for token in position_tokens]
        changes = [
            _parse_optional_integer(token, "position change")
            for token in change_tokens
        ]
        if any(value < 0 for value in positions):
            raise CFTCTFFParseError(
                f"CFTC TFF contract {spec['code']} positions cannot be negative"
            )

        open_interest = _parse_integer(oi_match.group(1), "open interest")
        open_interest_change = _parse_optional_integer(
            changes_match.group(2), "total open-interest change"
        )
        spreading = sum(positions[index] for index in (2, 5, 8, 11))
        long_total = sum(positions[index] for index in (0, 3, 6, 9, 12)) + spreading
        short_total = sum(positions[index] for index in (1, 4, 7, 10, 13)) + spreading
        if long_total != open_interest or short_total != open_interest:
            raise CFTCTFFParseError(
                f"CFTC TFF contract {spec['code']} position totals do not reconcile to open interest"
            )

        changes_complete = (
            open_interest_change is not None
            and all(value is not None for value in changes)
        )
        if changes_complete:
            numeric_changes = [int(value) for value in changes]
            spreading_change = sum(numeric_changes[index] for index in (2, 5, 8, 11))
            long_change_total = (
                sum(numeric_changes[index] for index in (0, 3, 6, 9, 12))
                + spreading_change
            )
            short_change_total = (
                sum(numeric_changes[index] for index in (1, 4, 7, 10, 13))
                + spreading_change
            )
            if (
                long_change_total != open_interest_change
                or short_change_total != open_interest_change
            ):
                raise CFTCTFFParseError(
                    f"CFTC TFF contract {spec['code']} weekly changes do not reconcile to open-interest change"
                )

        trader_count_match = re.search(r"TOTAL TRADERS:\s*([\d,]+)", segment)
        total_traders = (
            _parse_integer(trader_count_match.group(1), "total traders")
            if trader_count_match
            else None
        )

        categories = {}
        for slug, name, long_index, short_index, spread_index in CFTC_POSITION_CATEGORIES:
            long_value = positions[long_index]
            short_value = positions[short_index]
            spreading_value = positions[spread_index] if spread_index is not None else 0
            long_change = changes[long_index]
            short_change = changes[short_index]
            spreading_change_value = (
                changes[spread_index] if spread_index is not None else 0
            )
            net_change = (
                long_change - short_change
                if long_change is not None and short_change is not None
                else None
            )
            categories[slug] = {
                "name": name,
                "long_contracts": long_value,
                "short_contracts": short_value,
                "spreading_contracts": spreading_value,
                "net_long_short_contracts": long_value - short_value,
                "long_change_contracts": long_change,
                "short_change_contracts": short_change,
                "spreading_change_contracts": spreading_change_value,
                "net_long_short_change_contracts": net_change,
            }
        contracts.append(
            {
                **spec,
                "reporting_status": "reported",
                "open_interest_contracts": open_interest,
                "open_interest_xrp_equivalent": (
                    open_interest * spec["contract_multiplier_xrp"]
                ),
                "open_interest_change_contracts": open_interest_change,
                "change_from_date": change_from_date.isoformat(),
                "total_traders": total_traders,
                "positions": categories,
                "model_eligible": False,
            }
        )

    reported_contracts = [
        item for item in contracts if item["reporting_status"] == "reported"
    ]
    return {
        "report_type": "traders_in_financial_futures_futures_only",
        "positions_as_of_date": as_of_date.isoformat(),
        "timestamp_precision": "date_only",
        "contracts": contracts,
        "contract_status": contract_status,
        "reported_contract_count": len(reported_contracts),
        "reported_xrp_equivalent_open_interest_total": sum(
            item["open_interest_xrp_equivalent"] for item in reported_contracts
        ),
        "model_eligible": False,
    }
