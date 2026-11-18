"""Read-only SEC EDGAR ingestion for XRP-adjacent public-company capital evidence."""
from __future__ import annotations

import json
import math
import os
import re
from datetime import datetime, timezone
from typing import Any, Callable, Mapping
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

MAX_RESPONSE_BYTES = 10 * 1024 * 1024
SEC_ALLOWED_HOSTS = frozenset({"data.sec.gov"})
SEC_DEFAULT_USER_AGENT = "Barrot-Agent XRP research contact: barrot-hunter@users.noreply.github.com"
SEC_USER_AGENT = os.getenv("BARROT_SEC_USER_AGENT", SEC_DEFAULT_USER_AGENT).strip()
MAX_RECENT_FILINGS = 2000
MAX_CAPITAL_FACTS_PER_ISSUER = 1000

SEC_ISSUERS = (
    {"entity_id": "evernorth", "cik": "0002092592", "legal_name": "Evernorth Holdings Inc.", "role": "XRP treasury vehicle and financing disclosures"},
    {"entity_id": "coinbase", "cik": "0001679788", "legal_name": "Coinbase Global, Inc.", "role": "XRP exchange, custody, collateral and distribution infrastructure"},
    {"entity_id": "circle", "cik": "0001876042", "legal_name": "Circle Internet Group, Inc.", "role": "USDC issuer and stablecoin/payment infrastructure"},
)
SEC_RELEVANT_FORMS = frozenset({
    "8-K", "8-K/A", "10-Q", "10-Q/A", "10-K", "10-K/A", "S-1", "S-1/A",
    "F-1", "F-1/A", "6-K", "6-K/A", "20-F", "20-F/A", "424B1", "424B2",
    "424B3", "424B4", "424B5", "EFFECT", "D", "D/A", "SC 13D", "SC 13D/A",
    "SC 13G", "SC 13G/A", "13F-HR", "13F-HR/A", "4", "144",
})
CAPITAL_FACT_TERMS = (
    "cash", "proceeds", "debt", "warrant", "share", "stock", "equity",
    "convertible", "note", "capital", "cryptocurrency", "digitalasset",
    "digital_asset", "xrp", "token", "investment",
)
HTTP_PROVENANCE_HEADERS = frozenset({
    "age", "cache-control", "content-type", "content-encoding", "etag",
    "expires", "last-modified", "cf-cache-status", "x-cache",
})
_ACCESSION_RE = re.compile(r"^[0-9]{10}-[0-9]{2}-[0-9]{6}$")
_DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


class SECEdgarError(ValueError):
    """A public SEC response or filing record violates the ingestion contract."""


class _RejectRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise SECEdgarError("SEC redirects are disabled")


def _iso(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise SECEdgarError("SEC capture time must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise SECEdgarError(f"{field} must be a timezone-aware ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise SECEdgarError(f"{field} is not valid ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SECEdgarError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _date(value: Any, field: str, *, required: bool = False) -> str | None:
    if value in (None, "") and not required:
        return None
    if not isinstance(value, str) or not _DATE_RE.fullmatch(value):
        raise SECEdgarError(f"{field} must be an ISO date")
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise SECEdgarError(f"{field} is not a valid calendar date") from exc
    return value


def _cik(value: Any) -> str:
    if isinstance(value, bool):
        raise SECEdgarError("SEC CIK must be numeric")
    try:
        number = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise SECEdgarError("SEC CIK must be numeric") from exc
    if number <= 0 or number > 9_999_999_999:
        raise SECEdgarError("SEC CIK is outside the supported range")
    return f"{number:010d}"


def _normalized_name(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower()) if isinstance(value, str) else ""


def _accession(value: Any) -> str:
    if not isinstance(value, str) or not _ACCESSION_RE.fullmatch(value):
        raise SECEdgarError("SEC accession number is malformed")
    return value


def _primary_document(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str) or value in {".", ".."} or "/" in value or "\\" in value or ".." in value or any(ord(c) < 32 for c in value):
        raise SECEdgarError("SEC primary document path is unsafe")
    return value


def _capture_http_headers(headers: Any) -> dict[str, str]:
    if headers is None or not hasattr(headers, "items"):
        return {}
    captured = {}
    for raw_name, raw_value in headers.items():
        name, value = str(raw_name).strip().lower(), str(raw_value).strip()
        if name in HTTP_PROVENANCE_HEADERS and value and len(value) <= 512 and not any(ord(c) < 32 or ord(c) == 127 for c in value):
            captured[name] = value
    return dict(sorted(captured.items()))


def _open_sec_request(request: Request, *, timeout: int = 20):
    return build_opener(_RejectRedirectHandler()).open(request, timeout=timeout)


def fetch_sec_json(source_id: str, url: str) -> dict[str, Any]:
    """Fetch only allowlisted SEC JSON endpoints with an identifying contact User-Agent."""
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in SEC_ALLOWED_HOSTS or parsed.username is not None or parsed.password is not None or parsed.port is not None:
        raise SECEdgarError("SEC URL is not an allowlisted public HTTPS endpoint")
    if not SEC_USER_AGENT or len(SEC_USER_AGENT) > 256 or not _EMAIL_RE.search(SEC_USER_AGENT):
        raise SECEdgarError("BARROT_SEC_USER_AGENT must identify Barrot and include a contact email")
    request = Request(url, headers={"Accept": "application/json", "User-Agent": SEC_USER_AGENT, "Cache-Control": "no-cache"})
    try:
        with _open_sec_request(request, timeout=20) as response:
            final_url = urlsplit(response.geturl())
            if final_url.scheme != "https" or final_url.hostname not in SEC_ALLOWED_HOSTS:
                raise SECEdgarError("SEC response redirected outside the allowlisted host")
            if "json" not in response.headers.get("Content-Type", "").lower():
                raise SECEdgarError("SEC response content type is not JSON")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            http_date = response.headers.get("Date")
            headers = _capture_http_headers(response.headers)
    except SECEdgarError:
        raise
    except Exception as exc:
        status = getattr(exc, "code", None)
        if status is not None:
            raise SECEdgarError(f"SEC request failed with HTTP {status}") from None
        raise SECEdgarError(f"SEC request failed: {type(exc).__name__}") from None
    if not raw or len(raw) > MAX_RESPONSE_BYTES:
        raise SECEdgarError("SEC JSON response is empty or exceeds the 10 MiB limit")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise SECEdgarError("SEC response is not valid UTF-8 JSON") from exc
    if not isinstance(payload, Mapping):
        raise SECEdgarError("SEC JSON root must be an object")
    return {"raw_bytes": raw, "payload": payload, "http_date": http_date, "http_headers": headers}


def parse_submissions(payload: Mapping[str, Any], issuer: Mapping[str, str], *, captured_at_utc: str):
    """Parse recent SEC filing metadata without backdating to filing-date midnight."""
    if not isinstance(payload, Mapping) or _cik(payload.get("cik")) != issuer["cik"]:
        raise SECEdgarError("SEC submissions CIK does not match the configured issuer")
    if _normalized_name(payload.get("name")) != _normalized_name(issuer["legal_name"]):
        raise SECEdgarError("SEC submissions legal name does not match the configured issuer")
    filings = payload.get("filings")
    recent = filings.get("recent") if isinstance(filings, Mapping) else None
    if not isinstance(recent, Mapping):
        raise SECEdgarError("SEC submissions recent-filings object is missing")
    arrays, lengths = {}, set()
    for field in ("accessionNumber", "filingDate", "form", "primaryDocument"):
        values = recent.get(field)
        if not isinstance(values, list):
            raise SECEdgarError(f"SEC submissions {field} must be an array")
        arrays[field] = values
        lengths.add(len(values))
    if len(lengths) != 1:
        raise SECEdgarError("SEC submissions required arrays have different lengths")
    count = lengths.pop()
    if count > MAX_RECENT_FILINGS:
        raise SECEdgarError("SEC submissions recent-filings array exceeds the configured limit")
    for field in ("reportDate", "acceptanceDateTime", "items", "size", "isXBRL", "isInlineXBRL"):
        values = recent.get(field)
        if values is None:
            arrays[field] = [None] * count
        elif isinstance(values, list) and len(values) == count:
            arrays[field] = values
        else:
            raise SECEdgarError(f"SEC submissions optional {field} array has an invalid length")
    captured = _utc(captured_at_utc, "captured_at_utc")
    events, by_accession, latest_acceptance = [], {}, None
    for index in range(count):
        form = arrays["form"][index].strip().upper() if isinstance(arrays["form"][index], str) else ""
        if form not in SEC_RELEVANT_FORMS:
            continue
        accession = _accession(arrays["accessionNumber"][index])
        filing_date = _date(arrays["filingDate"][index], "filingDate", required=True)
        report_date = _date(arrays["reportDate"][index], "reportDate")
        primary = _primary_document(arrays["primaryDocument"][index])
        acceptance = None
        raw_acceptance = arrays["acceptanceDateTime"][index]
        if isinstance(raw_acceptance, str) and raw_acceptance.strip():
            try:
                acceptance = _utc(raw_acceptance, "acceptanceDateTime")
            except SECEdgarError:
                acceptance = None
        if acceptance is not None and acceptance > captured:
            raise SECEdgarError("SEC acceptance timestamp is later than capture time")
        known_at = _iso(acceptance) if acceptance else _iso(captured)
        known_basis = "sec_acceptance_datetime" if acceptance else "capture_time_only"
        cik_number, compact = str(int(issuer["cik"])), accession.replace("-", "")
        index_url = f"https://www.sec.gov/Archives/edgar/data/{cik_number}/{compact}/{accession}-index.htm"
        primary_url = f"https://www.sec.gov/Archives/edgar/data/{cik_number}/{compact}/{primary}" if primary else None
        size = arrays["size"][index]
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            size = None
        event = {
            "event_type": "sec_filing_published", "entity_id": issuer["entity_id"],
            "entity_name": issuer["legal_name"], "cik": issuer["cik"], "form": form,
            "accession_number": accession, "filing_date": filing_date, "report_date": report_date,
            "event_date": report_date or filing_date, "event_date_precision": "date_only",
            "acceptance_datetime_utc": _iso(acceptance) if acceptance else None,
            "known_at_utc": known_at, "known_at_basis": known_basis,
            "primary_document": primary, "primary_document_url": primary_url,
            "filing_index_url": index_url,
            "items": arrays["items"][index] if isinstance(arrays["items"][index], str) else None,
            "filing_size_bytes": size,
            "is_xbrl": bool(arrays["isXBRL"][index]) if arrays["isXBRL"][index] is not None else None,
            "is_inline_xbrl": bool(arrays["isInlineXBRL"][index]) if arrays["isInlineXBRL"][index] is not None else None,
            "model_eligible": False,
            "capital_event_interpretation": "filing_metadata_only; inspect primary document before classifying economic execution",
        }
        events.append(event)
        by_accession[accession] = event
        if acceptance is not None:
            latest_acceptance = max(latest_acceptance, acceptance) if latest_acceptance else acceptance
    return events, by_accession, _iso(latest_acceptance) if latest_acceptance else None


def _capital_fact_category(fact_name: str, label: str) -> tuple[str, str, str]:
    combined = f"{fact_name} {label}".lower()
    if "warrant" in combined:
        return "warrant_related_fact", "warrant", combined
    if any(term in combined for term in ("convertible", "debt", "note payable", "notes payable")):
        return ("reported_debt_proceeds_fact" if "proceeds" in combined else "debt_related_fact"), "debt", combined
    if any(term in combined for term in ("share", "stock", "equity")):
        return ("reported_equity_proceeds_fact" if "proceeds" in combined else "equity_related_fact"), "equity", combined
    if "proceeds" in combined:
        return "reported_proceeds_fact", "unspecified", combined
    if "cash" in combined:
        return "cash_balance_fact", "cash", combined
    return "capital_related_fact", "unspecified", combined


def parse_companyfacts(payload: Mapping[str, Any], issuer: Mapping[str, str], filings_by_accession: Mapping[str, Mapping[str, Any]], *, captured_at_utc: str):
    """Extract recent accession-linked capital facts; all remain research-only."""
    if not isinstance(payload, Mapping) or _cik(payload.get("cik")) != issuer["cik"]:
        raise SECEdgarError("SEC companyfacts CIK does not match the configured issuer")
    if _normalized_name(payload.get("entityName")) != _normalized_name(issuer["legal_name"]):
        raise SECEdgarError("SEC companyfacts legal name does not match the configured issuer")
    facts = payload.get("facts")
    if not isinstance(facts, Mapping):
        raise SECEdgarError("SEC companyfacts facts object is missing")
    _utc(captured_at_utc, "captured_at_utc")
    output, truncated = [], False
    for taxonomy, concepts in facts.items():
        if not isinstance(taxonomy, str) or not isinstance(concepts, Mapping):
            continue
        for fact_name, fact in concepts.items():
            if not isinstance(fact_name, str) or not isinstance(fact, Mapping):
                continue
            label = fact.get("label") if isinstance(fact.get("label"), str) else ""
            combined = f"{fact_name} {label}".lower()
            if not any(term in combined for term in CAPITAL_FACT_TERMS):
                continue
            units = fact.get("units")
            if not isinstance(units, Mapping):
                continue
            for unit, observations in units.items():
                if not isinstance(unit, str) or not isinstance(observations, list):
                    continue
                for observation in observations:
                    if not isinstance(observation, Mapping):
                        continue
                    accession = observation.get("accn")
                    filing = filings_by_accession.get(accession) if isinstance(accession, str) else None
                    if filing is None:
                        continue
                    value = observation.get("val")
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                        continue
                    filed = _date(observation.get("filed"), "companyfacts filed date")
                    start = _date(observation.get("start"), "companyfacts start date")
                    end = _date(observation.get("end"), "companyfacts end date")
                    category, instrument, combined_label = _capital_fact_category(fact_name, label)
                    gross_net = "net" if re.search(r"\bnet\b", combined_label) else "gross" if re.search(r"\bgross\b", combined_label) else "not_disclosed_in_fact_label"
                    share_quantity = value if unit.lower() in {"shares", "share"} and any(term in combined_label for term in ("exercise", "warrant", "issu")) else None
                    event_date = end or start or filed or filing.get("event_date")
                    output.append({
                        "event_type": category, "entity_id": issuer["entity_id"],
                        "entity_name": issuer["legal_name"], "cik": issuer["cik"],
                        "taxonomy": taxonomy, "fact_name": fact_name, "fact_label": label or None,
                        "accession_number": accession, "form": filing["form"],
                        "filing_date": filing["filing_date"], "report_date": filing.get("report_date"),
                        "event_date": event_date, "event_date_precision": "date_only" if event_date else "unknown",
                        "period_start": start, "period_end": end,
                        "known_at_utc": filing["known_at_utc"], "known_at_basis": filing["known_at_basis"],
                        "fact_filed_date": filed, "reported_value": value, "reported_unit": unit,
                        "reported_share_quantity": share_quantity, "instrument_type": instrument,
                        "gross_net_basis": gross_net, "use_of_proceeds": None,
                        "use_of_proceeds_status": "requires_primary_filing_text_review",
                        "xrp_quantity": None, "xrp_purchase_or_collateral_linkage": "not_established",
                        "filing_primary_document_url": filing.get("primary_document_url"),
                        "model_eligible": False,
                        "interpretation_limit": "XBRL fact only; do not infer cash deployment, XRP acquisition, collateral use or use of proceeds",
                    })
                    if len(output) >= MAX_CAPITAL_FACTS_PER_ISSUER:
                        truncated = True
                        return output, truncated
    return output, truncated


def capture_sec_edgar(*, fetcher: Callable[[str, str], Mapping[str, Any]], archive: Any, captured_at: datetime, include_companyfacts: bool = False) -> dict[str, Any]:
    """Capture SEC submissions and optional companyfacts into the existing raw receipt chain."""
    if captured_at.tzinfo is None or captured_at.utcoffset() is None:
        raise SECEdgarError("captured_at must be timezone-aware")
    if not isinstance(include_companyfacts, bool):
        raise SECEdgarError("include_companyfacts must be a boolean")
    receipts, failures, raw_only, filing_events, capital_facts = [], [], [], [], []
    latest_capture = captured_at
    submissions_count = companyfacts_count = 0
    truncated_issuers = []

    def capture_endpoint(source_id, url, parser):
        nonlocal latest_capture
        response, raw_bytes, received = None, None, captured_at
        try:
            response = fetcher(source_id, url)
            if not isinstance(response, Mapping):
                raise SECEdgarError("SEC fetcher response must be an object")
            raw_bytes = response.get("raw_bytes")
            if not isinstance(raw_bytes, bytes) or not raw_bytes:
                raise SECEdgarError("SEC fetcher must preserve non-empty raw bytes")
            payload = response.get("payload")
            if not isinstance(payload, Mapping):
                raise SECEdgarError("SEC payload must be an object")
            if response.get("received_at_utc") is not None:
                received = _utc(response["received_at_utc"], "received_at_utc")
            latest_capture = max(latest_capture, received)
            parsed, source_as_of = parser(payload, received)
        except Exception as exc:
            if isinstance(raw_bytes, bytes) and raw_bytes:
                receipt = archive.store(
                    source_id=source_id, source_uri=url, captured_at_utc=_iso(received),
                    raw_bytes=raw_bytes, source_data_as_of_utc=None, model_eligible=False,
                    raw_only_reason=f"sec_processing_failure:{type(exc).__name__}",
                    source_http_date=response.get("http_date") if isinstance(response, Mapping) else None,
                    source_http_headers=response.get("http_headers", {}) if isinstance(response, Mapping) else {},
                )
                receipts.append(receipt)
                raw_only.append({"source_id": source_id, "reason": f"sec_processing_failure:{type(exc).__name__}", "receipt_id": receipt["receipt_id"]})
            failures.append({
                "source_id": source_id, "source_uri": url, "captured_at_utc": _iso(received),
                "failure_class": type(exc).__name__, "failure_detail": " ".join(str(exc).split())[:240],
                "retryable": type(exc).__name__ in {"TimeoutError", "URLError", "HTTPError", "OSError"},
            })
            return None
        receipt = archive.store(
            source_id=source_id, source_uri=url, captured_at_utc=_iso(received),
            raw_bytes=raw_bytes, source_data_as_of_utc=source_as_of, model_eligible=False,
            raw_only_reason="sec_edgar_primary_regulatory_data_research_only_not_market_feature",
            source_http_date=response.get("http_date"), source_http_headers=response.get("http_headers", {}),
        )
        receipts.append(receipt)
        raw_only.append({"source_id": source_id, "reason": "sec_edgar_primary_regulatory_data_research_only_not_market_feature", "receipt_id": receipt["receipt_id"]})
        for item in parsed:
            item.update({
                "source_id": source_id, "source_uri": url,
                "raw_content_sha256": receipt["raw_content_sha256"],
                "receipt_id": receipt["receipt_id"], "raw_bytes_retained": receipt["raw_bytes_retained"],
                "captured_at_utc": _iso(received), "source_independence_group": "sec_edgar",
            })
        return parsed

    for issuer in SEC_ISSUERS:
        submissions_id = f"sec_edgar_submissions_{issuer['entity_id']}"
        submissions_url = f"https://data.sec.gov/submissions/CIK{issuer['cik']}.json"
        def submissions_parser(payload, received, issuer=issuer):
            events, by_accession, as_of = parse_submissions(payload, issuer, captured_at_utc=_iso(received))
            return (events, by_accession), as_of
        parsed_submissions = capture_endpoint(submissions_id, submissions_url, submissions_parser)
        filings_by_accession = {}
        if parsed_submissions is not None:
            events, filings_by_accession = parsed_submissions
            filing_events.extend(events)
            submissions_count += 1
        if include_companyfacts:
            companyfacts_id = f"sec_edgar_companyfacts_{issuer['entity_id']}"
            companyfacts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{issuer['cik']}.json"
            def companyfacts_parser(payload, received, issuer=issuer, filings_by_accession=filings_by_accession):
                facts, truncated = parse_companyfacts(payload, issuer, filings_by_accession, captured_at_utc=_iso(received))
                return (facts, truncated), None
            parsed_companyfacts = capture_endpoint(companyfacts_id, companyfacts_url, companyfacts_parser)
            if parsed_companyfacts is not None:
                facts, truncated = parsed_companyfacts
                capital_facts.extend(facts)
                companyfacts_count += 1
                if truncated:
                    truncated_issuers.append(issuer["entity_id"])

    status = "COMPLETED" if not failures else ("PARTIAL" if receipts else "FAILED")
    summary = {
        "status": status, "issuer_count": len(SEC_ISSUERS),
        "issuer_ids": [issuer["entity_id"] for issuer in SEC_ISSUERS],
        "submissions_source_count": submissions_count,
        "companyfacts_source_count": companyfacts_count,
        "companyfacts_requested": include_companyfacts,
        "filing_event_count": len(filing_events), "capital_fact_count": len(capital_facts),
        "capital_fact_truncated_issuers": truncated_issuers,
        "source_failure_count": len(failures), "raw_receipt_count": len(receipts),
        "model_eligible": False,
        "limitations": [
            "Only recent SEC submissions arrays are captured; older submission-history files are not fetched.",
            "Individual filing primary documents and custom inline-XBRL extension taxonomies are not downloaded by this adapter.",
            "Companyfacts contains reported XBRL facts only; it does not establish actual cash receipt, gross/net treatment, use of proceeds or XRP acquisition.",
            "Warrant exercises, in-kind XRP contributions, facility capacity and use-of-proceeds language require accession-specific primary filing-text review.",
            "No SEC data is promoted to the XRP market feature store or used to issue forecasts.",
        ],
    }
    return {"summary": summary, "receipts": receipts, "failures": failures, "raw_only": raw_only,
            "filing_events": filing_events, "capital_facts": capital_facts,
            "latest_source_capture_at_utc": _iso(latest_capture)}
