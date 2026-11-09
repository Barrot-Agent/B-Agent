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


def parse_cftc_tff_report(html_text: str) -> dict:
    """Parse three XRP futures-only TFF sections and reconcile OI/position totals.

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

    labels = [spec["label"] for spec in CFTC_CONTRACTS]
    contracts = []
    for spec in CFTC_CONTRACTS:
        start = plain.find(spec["label"])
        if start < 0:
            raise CFTCTFFParseError(
                f"CFTC TFF report is missing contract {spec['code']}"
            )
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
            r"TOTAL CHANGE IS:\s+(-?\d[\d,]*)\s+"
            r"((?:-?\d[\d,]*\s+){13}-?\d[\d,]*)",
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
        change_tokens = re.findall(r"-?\d[\d,]*", changes_match.group(3))
        if len(position_tokens) != 14 or len(change_tokens) != 14:
            raise CFTCTFFParseError(
                f"CFTC TFF contract {spec['code']} must have exactly 14 position and change values"
            )
        positions = [_parse_integer(token, "position") for token in position_tokens]
        changes = [_parse_integer(token, "position change") for token in change_tokens]
        if any(value < 0 for value in positions):
            raise CFTCTFFParseError(
                f"CFTC TFF contract {spec['code']} positions cannot be negative"
            )

        open_interest = _parse_integer(oi_match.group(1), "open interest")
        open_interest_change = _parse_integer(
            changes_match.group(2), "total open-interest change"
        )
        spreading = sum(positions[index] for index in (2, 5, 8, 11))
        long_total = sum(positions[index] for index in (0, 3, 6, 9, 12)) + spreading
        short_total = sum(positions[index] for index in (1, 4, 7, 10, 13)) + spreading
        spreading_change = sum(changes[index] for index in (2, 5, 8, 11))
        long_change_total = (
            sum(changes[index] for index in (0, 3, 6, 9, 12)) + spreading_change
        )
        short_change_total = (
            sum(changes[index] for index in (1, 4, 7, 10, 13)) + spreading_change
        )
        if long_total != open_interest or short_total != open_interest:
            raise CFTCTFFParseError(
                f"CFTC TFF contract {spec['code']} position totals do not reconcile to open interest"
            )
        if (
            long_change_total != open_interest_change
            or short_change_total != open_interest_change
        ):
            raise CFTCTFFParseError(
                f"CFTC TFF contract {spec['code']} weekly changes do not reconcile to open-interest change"
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
            categories[slug] = {
                "name": name,
                "long_contracts": long_value,
                "short_contracts": short_value,
                "spreading_contracts": spreading_value,
                "net_long_short_contracts": long_value - short_value,
                "long_change_contracts": long_change,
                "short_change_contracts": short_change,
                "spreading_change_contracts": spreading_change_value,
                "net_long_short_change_contracts": long_change - short_change,
            }
        contracts.append(
            {
                **spec,
                "open_interest_contracts": open_interest,
                "open_interest_change_contracts": open_interest_change,
                "change_from_date": change_from_date.isoformat(),
                "positions": categories,
            }
        )

    return {
        "report_type": "traders_in_financial_futures_futures_only",
        "positions_as_of_date": as_of_date.isoformat(),
        "timestamp_precision": "date_only",
        "contracts": contracts,
        "model_eligible": False,
    }