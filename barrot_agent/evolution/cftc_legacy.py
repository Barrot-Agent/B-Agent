from __future__ import annotations

import html
import re
from datetime import datetime

from .cftc_tff import parse_cftc_contract_status


class CFTCLegacyParseError(ValueError):
    """Raised when the official CFTC Legacy Futures-Only XRP section is invalid."""


XRP_CME_LEGACY_CONTRACT = {
    "label": "XRP - CHICAGO MERCANTILE EXCHANGE",
    "code": "176740",
    "slug": "cme_xrp_legacy",
    "name": "XRP - Chicago Mercantile Exchange (Legacy Futures-Only)",
    "venue": "CME",
    "contract_multiplier_xrp": 50_000,
}


def _clean_lines(value: str) -> list[str]:
    value = re.sub(r"(?is)<(script|style)\b[^>]*>.*?</\1>", " ", value)
    value = re.sub(
        r"(?i)<br\s*/?>|</(?:pre|p|div|tr|td|th|h[1-6])\s*>", "\n", value
    )
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value).replace("\xa0", " ")
    return [
        re.sub(r"\s+", " ", line).strip().upper()
        for line in value.splitlines()
        if line.strip()
    ]


def _all_values(line: str, field: str, count: int) -> list[int | float | None] | None:
    match = re.match(r"^ALL\s*:\s*(.*)$", line)
    if match is None:
        return None
    tokens = re.findall(r"-?\d[\d,]*(?:\.\d+)?|\.", match.group(1))
    if len(tokens) != count:
        raise CFTCLegacyParseError(
            f"CFTC Legacy {field} row must contain {count} values"
        )
    values: list[int | float | None] = []
    for token in tokens:
        if token == ".":
            values.append(None)
        else:
            number = token.replace(",", "")
            values.append(float(number) if "." in number else int(number))
    return values


def _row(
    lines: list[str], start: int, end: int, field: str, count: int
) -> list[int | float | None]:
    for line in lines[start:end]:
        values = _all_values(line, field, count)
        if values is not None:
            return values
    raise CFTCLegacyParseError(f"CFTC Legacy report is missing the {field} All row")


def _date(value: str, field: str):
    try:
        return datetime.strptime(value.title(), "%B %d, %Y").date()
    except ValueError as exc:
        raise CFTCLegacyParseError(f"CFTC Legacy {field} is invalid") from exc


def parse_cftc_legacy_futures_only_report(
    html_text: str, contract_status_html: str | None = None
) -> dict:
    """Parse CME XRP Legacy Futures-Only COT; never map its categories to TFF.

    Weekly date-only positions remain research-only and model-ineligible.
    Suppressed values stay null, and a missing contract is never zero-filled.
    """
    if not isinstance(html_text, str) or not html_text.strip():
        raise CFTCLegacyParseError("CFTC Legacy HTML text must be non-empty")

    lines = _clean_lines(html_text)
    plain = " ".join(lines)
    date_match = re.search(
        r"COMMITMENTS OF TRADERS - FUTURES ONLY,\s*([A-Z]+\s+\d{1,2},\s+\d{4})",
        plain,
    )
    if date_match is None:
        raise CFTCLegacyParseError("CFTC Legacy report has no Futures-Only report date")
    report_date = _date(date_match.group(1), "report date")
    report_date_s = report_date.isoformat()

    status = None
    if contract_status_html is not None:
        try:
            status = parse_cftc_contract_status(contract_status_html)
        except ValueError as exc:
            raise CFTCLegacyParseError("CFTC Legacy contract-status index is invalid") from exc
        if status.get("reports_dated") != report_date_s:
            raise CFTCLegacyParseError(
                "CFTC Legacy contract-status report date does not match the Futures-Only report date"
            )

    headers = [
        i for i, line in enumerate(lines)
        if XRP_CME_LEGACY_CONTRACT["label"] in line
        and f"CODE-{XRP_CME_LEGACY_CONTRACT['code']}" in line
    ]
    if len(headers) > 1:
        raise CFTCLegacyParseError("CFTC Legacy report has duplicate XRP CME sections")
    if not headers:
        dropped = bool(
            status
            and XRP_CME_LEGACY_CONTRACT["code"] in status.get("futures_only_dropped", [])
        )
        contract = {
            **XRP_CME_LEGACY_CONTRACT,
            "reporting_status": (
                "dropped_from_reporting" if dropped else "not_reported_status_unverified"
            ),
            "positions_as_of_date": report_date_s,
            "change_from_date": None,
            "open_interest_contracts": None,
            "open_interest_xrp_equivalent": None,
            "open_interest_change_contracts": None,
            "open_interest_change_xrp_equivalent": None,
            "total_traders": None,
            "positions": None,
            "percent_of_open_interest": None,
            "trader_counts": None,
            "concentration": None,
            "position_reconciliation_status": "not_available",
            "change_reconciliation_status": "not_available",
            "model_eligible": False,
        }
        return {
            "report_type": "legacy_futures_only",
            "positions_as_of_date": report_date_s,
            "timestamp_precision": "date_only",
            "contract": contract,
            "contract_status": status,
            "model_eligible": False,
        }

    start = headers[0]
    end = next(
        (
            i for i in range(start + 1, len(lines))
            if "CHICAGO MERCANTILE EXCHANGE" in lines[i] and "CODE-" in lines[i]
        ),
        len(lines),
    )
    section = lines[start:end]
    section_text = " ".join(section)
    section_date = re.search(
        r"COMMITMENTS OF TRADERS - FUTURES ONLY,\s*([A-Z]+\s+\d{1,2},\s+\d{4})",
        section_text,
    )
    if section_date is None or _date(section_date.group(1), "XRP section date") != report_date:
        raise CFTCLegacyParseError("CFTC Legacy XRP section date does not match report date")

    multiplier = re.search(r"CONTRACTS OF\s+([\d,]+)\s+XRP", section_text)
    if multiplier is None or int(multiplier.group(1).replace(",", "")) != 50_000:
        raise CFTCLegacyParseError(
            "CFTC Legacy XRP contract multiplier differs from the verified CME specification"
        )

    heading_text = {
        "changes": "CHANGES IN COMMITMENTS FROM:",
        "percent": "PERCENT OF OPEN INTEREST REPRESENTED BY EACH CATEGORY",
        "traders": "NUMBER OF TRADERS IN EACH CATEGORY",
        "concentration": "PERCENT OF OPEN INTEREST HELD BY THE INDICATED NUMBER",
    }
    indexes = {
        key: next((i for i, line in enumerate(section) if text in line), None)
        for key, text in heading_text.items()
    }
    if any(value is None for value in indexes.values()):
        raise CFTCLegacyParseError("CFTC Legacy XRP section is missing a required long-report heading")

    changes_i = indexes["changes"]
    percent_i = indexes["percent"]
    traders_i = indexes["traders"]
    concentration_i = indexes["concentration"]
    position_row = _row(section, 1, changes_i, "positions", 10)
    change_row = _row(section, changes_i + 1, percent_i, "position changes", 10)
    percent_row = _row(section, percent_i + 1, traders_i, "open-interest percentages", 10)
    trader_row = _row(section, traders_i + 1, concentration_i, "trader counts", 8)
    concentration_row = _row(
        section, concentration_i + 1, len(section), "concentration", 8
    )

    if any(value is None or not isinstance(value, int) for value in position_row):
        raise CFTCLegacyParseError("CFTC Legacy XRP core positions contain suppressed values")
    if any(value < 0 for value in position_row):
        raise CFTCLegacyParseError("CFTC Legacy XRP positions cannot be negative")

    (
        oi, nc_long, nc_short, nc_spread, comm_long, comm_short,
        reportable_long, reportable_short, nr_long, nr_short,
    ) = position_row
    if reportable_long != nc_long + nc_spread + comm_long:
        raise CFTCLegacyParseError("CFTC Legacy XRP reportable long positions do not reconcile")
    if reportable_short != nc_short + nc_spread + comm_short:
        raise CFTCLegacyParseError("CFTC Legacy XRP reportable short positions do not reconcile")
    if oi != reportable_long + nr_long or oi != reportable_short + nr_short:
        raise CFTCLegacyParseError(
            "CFTC Legacy XRP long/short totals do not reconcile to open interest"
        )

    change_date_match = re.search(
        r"CHANGES IN COMMITMENTS FROM:\s*([A-Z]+\s+\d{1,2},\s+\d{4})",
        section[changes_i],
    )
    if change_date_match is None:
        raise CFTCLegacyParseError("CFTC Legacy XRP change-from date is missing")
    change_date = _date(change_date_match.group(1), "change-from date")
    if change_date >= report_date:
        raise CFTCLegacyParseError("CFTC Legacy XRP change-from date is not earlier than report date")

    (
        oi_change, nc_long_change, nc_short_change, nc_spread_change,
        comm_long_change, comm_short_change, reportable_long_change,
        reportable_short_change, nr_long_change, nr_short_change,
    ) = change_row
    change_status = "not_verifiable_suppressed_values"
    if all(value is not None for value in change_row):
        if reportable_long_change != nc_long_change + nc_spread_change + comm_long_change:
            raise CFTCLegacyParseError("CFTC Legacy XRP reportable long changes do not reconcile")
        if reportable_short_change != nc_short_change + nc_spread_change + comm_short_change:
            raise CFTCLegacyParseError("CFTC Legacy XRP reportable short changes do not reconcile")
        if (
            oi_change != reportable_long_change + nr_long_change
            or oi_change != reportable_short_change + nr_short_change
        ):
            raise CFTCLegacyParseError(
                "CFTC Legacy XRP weekly position changes do not reconcile to open-interest change"
            )
        change_status = "passed"

    if any(v is not None and not 0 <= float(v) <= 100 for v in percent_row):
        raise CFTCLegacyParseError("CFTC Legacy XRP open-interest percentages are outside 0-100")
    if percent_row[0] is not None and abs(float(percent_row[0]) - 100.0) > 0.05:
        raise CFTCLegacyParseError("CFTC Legacy XRP open-interest percentage total is not 100")
    if any(v is not None and (not isinstance(v, int) or v < 0) for v in trader_row):
        raise CFTCLegacyParseError("CFTC Legacy XRP trader counts are invalid")
    if any(v is not None and not 0 <= float(v) <= 100 for v in concentration_row):
        raise CFTCLegacyParseError("CFTC Legacy XRP concentration percentages are outside 0-100")

    nc = {
        "long_contracts": nc_long, "short_contracts": nc_short,
        "spreading_contracts": nc_spread, "net_long_short_contracts": nc_long - nc_short,
        "long_change_contracts": nc_long_change, "short_change_contracts": nc_short_change,
        "spreading_change_contracts": nc_spread_change,
        "net_long_short_change_contracts": (
            nc_long_change - nc_short_change
            if nc_long_change is not None and nc_short_change is not None else None
        ),
    }
    commercial = {
        "long_contracts": comm_long, "short_contracts": comm_short,
        "net_long_short_contracts": comm_long - comm_short,
        "long_change_contracts": comm_long_change, "short_change_contracts": comm_short_change,
        "net_long_short_change_contracts": (
            comm_long_change - comm_short_change
            if comm_long_change is not None and comm_short_change is not None else None
        ),
    }
    nonreportable = {
        "long_contracts": nr_long, "short_contracts": nr_short,
        "net_long_short_contracts": nr_long - nr_short,
        "long_change_contracts": nr_long_change, "short_change_contracts": nr_short_change,
        "net_long_short_change_contracts": (
            nr_long_change - nr_short_change
            if nr_long_change is not None and nr_short_change is not None else None
        ),
    }
    contract = {
        **XRP_CME_LEGACY_CONTRACT,
        "reporting_status": "reported",
        "positions_as_of_date": report_date_s,
        "change_from_date": change_date.isoformat(),
        "open_interest_contracts": oi,
        "open_interest_xrp_equivalent": oi * 50_000,
        "open_interest_change_contracts": oi_change,
        "open_interest_change_xrp_equivalent": oi_change * 50_000 if oi_change is not None else None,
        "total_traders": trader_row[0],
        "positions": {
            "non_commercial": nc,
            "commercial": commercial,
            "reportable_total": {
                "long_contracts": reportable_long, "short_contracts": reportable_short,
                "long_change_contracts": reportable_long_change,
                "short_change_contracts": reportable_short_change,
            },
            "nonreportable": nonreportable,
        },
        "percent_of_open_interest": {
            "non_commercial_long_pct": percent_row[1],
            "non_commercial_short_pct": percent_row[2],
            "non_commercial_spreading_pct": percent_row[3],
            "commercial_long_pct": percent_row[4],
            "commercial_short_pct": percent_row[5],
            "reportable_long_pct": percent_row[6],
            "reportable_short_pct": percent_row[7],
            "nonreportable_long_pct": percent_row[8],
            "nonreportable_short_pct": percent_row[9],
        },
        "trader_counts": {
            "total_traders": trader_row[0],
            "non_commercial_long_traders": trader_row[1],
            "non_commercial_short_traders": trader_row[2],
            "non_commercial_spreading_traders": trader_row[3],
            "commercial_long_traders": trader_row[4],
            "commercial_short_traders": trader_row[5],
            "reportable_long_traders": trader_row[6],
            "reportable_short_traders": trader_row[7],
        },
        "concentration": {
            "gross_4_or_less_long_pct": concentration_row[0],
            "gross_4_or_less_short_pct": concentration_row[1],
            "gross_8_or_less_long_pct": concentration_row[2],
            "gross_8_or_less_short_pct": concentration_row[3],
            "net_4_or_less_long_pct": concentration_row[4],
            "net_4_or_less_short_pct": concentration_row[5],
            "net_8_or_less_long_pct": concentration_row[6],
            "net_8_or_less_short_pct": concentration_row[7],
        },
        "position_reconciliation_status": "passed",
        "change_reconciliation_status": change_status,
        "model_eligible": False,
    }
    return {
        "report_type": "legacy_futures_only",
        "positions_as_of_date": report_date_s,
        "timestamp_precision": "date_only",
        "contract": contract,
        "contract_status": status,
        "model_eligible": False,
    }
