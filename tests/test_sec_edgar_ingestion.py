from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from barrot_agent.evolution.sec_edgar import (
    SEC_ISSUERS, SECEdgarError, capture_sec_edgar, fetch_sec_json,
    parse_companyfacts, parse_submissions,
)
from barrot_agent.evolution.xrp_public_ingestion import RawReceiptArchive

CAPTURED = "2026-11-18T05:00:00Z"


def _submission_payload(issuer, accession, *, acceptance="2026-11-17T07:44:14.000Z"):
    return {
        "cik": int(issuer["cik"]), "name": issuer["legal_name"],
        "filings": {"recent": {
            "accessionNumber": [accession], "filingDate": ["2026-11-17"],
            "reportDate": ["2026-11-17"], "acceptanceDateTime": [acceptance],
            "form": ["8-K"], "primaryDocument": ["primary.htm"], "items": ["1.01, 3.02"],
            "size": [12345], "isXBRL": [1], "isInlineXBRL": [1],
        }},
    }


def test_parse_submissions_preserves_accession_and_acceptance_time():
    issuer = SEC_ISSUERS[0]
    events, by_accession, latest = parse_submissions(
        _submission_payload(issuer, "0001628280-26-074355"), issuer, captured_at_utc=CAPTURED
    )
    event = events[0]
    assert event["accession_number"] == "0001628280-26-074355"
    assert event["known_at_utc"] == "2026-11-17T07:44:14Z"
    assert event["known_at_basis"] == "sec_acceptance_datetime"
    assert event["primary_document_url"].endswith("/primary.htm")
    assert event["filing_index_url"].endswith("/0001628280-26-074355-index.htm")
    assert by_accession[event["accession_number"]] is event
    assert latest == "2026-11-17T07:44:14Z"
    assert event["model_eligible"] is False


def test_parse_submissions_falls_back_to_capture_time_and_rejects_bad_identity():
    issuer = SEC_ISSUERS[0]
    events, _, latest = parse_submissions(
        _submission_payload(issuer, "0001628280-26-074355", acceptance=""),
        issuer, captured_at_utc=CAPTURED,
    )
    assert events[0]["known_at_utc"] == CAPTURED
    assert events[0]["known_at_basis"] == "capture_time_only"
    assert latest is None
    payload = _submission_payload(issuer, "0001628280-26-074355")
    payload["cik"] = 1679788
    with pytest.raises(SECEdgarError):
        parse_submissions(payload, issuer, captured_at_utc=CAPTURED)
    payload = _submission_payload(issuer, "0001628280-26-074355")
    payload["filings"]["recent"]["primaryDocument"] = ["../escape.htm"]
    with pytest.raises(SECEdgarError):
        parse_submissions(payload, issuer, captured_at_utc=CAPTURED)


def test_companyfacts_are_accession_linked_and_do_not_infer_xrp_use():
    issuer = SEC_ISSUERS[0]
    _, by_accession, _ = parse_submissions(
        _submission_payload(issuer, "0001628280-26-074355"), issuer, captured_at_utc=CAPTURED
    )
    payload = {
        "cik": int(issuer["cik"]), "entityName": issuer["legal_name"],
        "facts": {"us-gaap": {
            "ProceedsFromIssuanceOfLongTermDebt": {
                "label": "Proceeds from issuance of long-term debt, net",
                "units": {"USD": [{
                    "accn": "0001628280-26-074355", "filed": "2026-11-17",
                    "form": "8-K", "start": "2026-10-13", "end": "2026-10-13", "val": 29000000,
                }]},
            },
            "WarrantsExercised": {
                "label": "Warrants exercised",
                "units": {"shares": [{
                    "accn": "0001628280-26-074355", "filed": "2026-11-17",
                    "form": "8-K", "end": "2026-11-09", "val": 3073366,
                }]},
            },
        }},
    }
    facts, truncated = parse_companyfacts(payload, issuer, by_accession, captured_at_utc=CAPTURED)
    assert truncated is False and len(facts) == 2
    debt = next(item for item in facts if item["instrument_type"] == "debt")
    assert debt["reported_value"] == 29000000
    assert debt["gross_net_basis"] == "net"
    assert debt["known_at_utc"] == "2026-11-17T07:44:14Z"
    assert debt["event_date"] == "2026-10-13"
    assert debt["use_of_proceeds"] is None
    assert debt["xrp_purchase_or_collateral_linkage"] == "not_established"
    warrant = next(item for item in facts if item["instrument_type"] == "warrant")
    assert warrant["reported_share_quantity"] == 3073366
    assert warrant["model_eligible"] is False


def test_fetch_sec_json_rejects_non_sec_hosts_without_network():
    with pytest.raises(SECEdgarError):
        fetch_sec_json("sec_edgar_test", "https://example.com/data.json")


def test_capture_sec_edgar_stores_raw_receipts_and_filing_events(tmp_path):
    captured = datetime(2026, 11, 18, 5, 0, tzinfo=timezone.utc)
    accessions = {
        "evernorth": "0001628280-26-074355",
        "coinbase": "0001679788-26-000100",
        "circle": "0001876042-26-000100",
    }
    calls = []
    def fetcher(source_id, url):
        calls.append(source_id)
        issuer_id = source_id.rsplit("_", 1)[-1]
        issuer = next(item for item in SEC_ISSUERS if item["entity_id"] == issuer_id)
        payload = (
            _submission_payload(issuer, accessions[issuer_id])
            if source_id.startswith("sec_edgar_submissions_")
            else {"cik": int(issuer["cik"]), "entityName": issuer["legal_name"], "facts": {}}
        )
        raw = json.dumps(payload, sort_keys=True).encode("utf-8")
        return {
            "raw_bytes": raw, "payload": payload, "received_at_utc": CAPTURED,
            "http_date": "Wed, 18 Nov 2026 05:00:00 GMT",
            "http_headers": {"content-type": "application/json"},
        }
    archive = RawReceiptArchive(tmp_path / "raw")
    result = capture_sec_edgar(
        fetcher=fetcher, archive=archive, captured_at=captured, include_companyfacts=True
    )
    assert result["summary"]["status"] == "COMPLETED"
    assert result["summary"]["submissions_source_count"] == 3
    assert result["summary"]["companyfacts_source_count"] == 3
    assert result["summary"]["filing_event_count"] == 3
    assert result["summary"]["raw_receipt_count"] == 6
    assert len(result["receipts"]) == 6 and len(calls) == 6
    assert all(event["raw_content_sha256"] and event["receipt_id"] for event in result["filing_events"])
    assert all(event["model_eligible"] is False for event in result["filing_events"])
    assert archive.verify()["valid"] is True
