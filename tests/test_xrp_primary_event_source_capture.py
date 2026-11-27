from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json

import pytest

from barrot_agent.evolution.xrp_public_ingestion import (
    ALLOWED_HOSTS,
    EVENT_SOURCE_CAPTURE_SPECS,
    RawReceiptArchive,
    XRPIngestionError,
    _capture_event_timeline_registry,
    _capture_public_event_sources,
    _event_source_capture_due,
)


def _event(spec):
    return {
        "event_id": spec["event_id"],
        "event_type": "corporate",
        "event_name": f"Primary-source event {spec['event_id']}",
        "hypothesis_id": "stablecoin-access-on-xrpl",
        "domain": "institutional-payments",
        "hypothesis": "Native stablecoin access may broaden XRPL payment and settlement options.",
        "counter_hypothesis": "Listing or network availability does not establish material XRP spot demand.",
        "claim": f"Primary publisher announcement: {spec['event_id']}.",
        "source_id": spec["source_id"],
        "source_name": spec["source_id"],
        "source_url": spec["source_uri"],
        "independence_group": spec["source_id"],
        "source_status": "verified",
        "stance": "supports",
        "event_status": "occurred",
        "event_time_utc": "2026-11-11T20:00:00Z",
        "source_published_at_utc": "2026-11-11T20:01:00Z",
        "available_at_utc": "2026-11-12T04:00:00.000000Z",
        "captured_at_utc": "2026-11-12T04:00:00.000000Z",
        "raw_source_sha256": None,
        "assumptions": ["The publisher's dated announcement is authentic."],
        "falsification_conditions": ["A publisher correction materially reverses the announcement."],
        "related_entities": ["Coinbase", "Circle", "Ripple", "XRPL"],
        "tags": ["XRP", "stablecoin", "payments"],
    }


def _write_registry(path, events):
    path.write_text(
        json.dumps(
            {
                "artifact_type": "barrot.xrp.event_registry",
                "schema_version": "1.0.0",
                "registry_version": "test-primary-event-capture",
                "captured_at_utc": "2026-11-12T04:00:00.000000Z",
                "events": events,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def _fetcher(*, received_at="2026-11-12T04:30:00.000000Z", marker_mismatch=()):
    specs = {spec["source_id"]: spec for spec in EVENT_SOURCE_CAPTURE_SPECS}

    def fetch(source_id, url):
        spec = specs[source_id]
        assert url == spec["source_uri"]
        markers = list(spec["required_markers"])
        if source_id in marker_mismatch:
            markers.pop()
        body = ("<html><body>" + " | ".join(markers) + "</body></html>").encode("utf-8")
        return {
            "raw_bytes": body,
            "payload": {"html_text": body.decode("utf-8")},
            "received_at_utc": received_at,
            "http_date": None,
            "http_headers": {"content-type": "text/html; charset=utf-8"},
        }

    return fetch


def _capture(tmp_path, *, received_at="2026-11-12T04:30:00.000000Z", marker_mismatch=()):
    registry = tmp_path / "events.json"
    _write_registry(registry, [_event(spec) for spec in EVENT_SOURCE_CAPTURE_SPECS])
    archive = RawReceiptArchive(tmp_path / "raw")
    receipts = []
    failures = []
    raw_only = []
    summary = _capture_public_event_sources(
        registry,
        fetcher=_fetcher(received_at=received_at, marker_mismatch=marker_mismatch),
        archive=archive,
        captured=datetime(2026, 11, 12, 4, 10, tzinfo=timezone.utc),
        receipts=receipts,
        failures=failures,
        raw_only=raw_only,
    )
    return registry, receipts, failures, raw_only, summary


def test_sbi_remit_primary_event_capture_spec_is_exact_and_allowlisted():
    spec = next(
        item for item in EVENT_SOURCE_CAPTURE_SPECS
        if item["source_id"] == "sbi_remit_xrp_odl_corridor_expansion_20230906"
    )
    assert spec["event_id"] == "sbi-remit-xrp-odl-corridors-2023-09-06"
    assert spec["source_uri"] == (
        "https://www.remit.co.jp/en/kaigaisoukin/information/release20230906/"
    )
    assert {
        "XRP-based International Money Transfer Service",
        "2023/09/06",
        "SBI Remit Co., Ltd.",
    }.issubset(set(spec["required_markers"]))
    assert "www.remit.co.jp" in ALLOWED_HOSTS


def test_primary_event_sources_create_digest_only_receipts_and_relink_at_capture_time(tmp_path):
    expected_count = len(EVENT_SOURCE_CAPTURE_SPECS)
    registry, receipts, failures, raw_only, capture = _capture(tmp_path)

    assert capture["status"] == "CAPTURED"
    assert capture["captured_event_count"] == expected_count
    assert capture["digest_only_receipt_count"] == expected_count
    assert capture["event_discovery_implemented"] is False
    assert failures == []
    assert len(receipts) == expected_count
    assert all(receipt["raw_bytes_retained"] is False for receipt in receipts)
    assert all(receipt["raw_payload_path"] is None for receipt in receipts)
    assert len(raw_only) == expected_count

    result = _capture_event_timeline_registry(
        registry,
        "2026-11-12T05:00:00.000000Z",
        raw_receipts=receipts,
    )
    assert result["event_count"] == expected_count
    assert result["receipt_complete"] is True
    assert result["public_receipt_relinkage"]["status"] == "LINKED"
    assert result["public_receipt_relinkage"]["linked_event_count"] == expected_count
    assert result["receipt_linkage"]["source_id_match_count"] == expected_count
    assert result["receipt_linkage"]["digest_only_verified_count"] == expected_count
    assert result["model_eligible"] is False
    assert result["forecast_status"] == "NOT_ISSUED"
    for event in result["timeline"]["event_timeline"]:
        assert event["known_at_utc"] == "2026-11-12T04:30:00.000000Z"
        assert event["receipt_status"] == "VERIFIED_CANONICAL_RECEIPT"
        assert event["receipt_source_id_match"] is True
        assert event["source_capture_history"][0]["captured_at_utc"] == "2026-11-12T04:00:00Z"
        assert event["source_capture_history"][-1]["captured_at_utc"] == "2026-11-12T04:30:00Z"
        assert event["source_capture_history"][-1]["raw_bytes_retained"] is False


def test_marker_mismatch_is_retained_as_unlinked_digest_only_evidence(tmp_path):
    expected_count = len(EVENT_SOURCE_CAPTURE_SPECS)
    mismatched_spec = EVENT_SOURCE_CAPTURE_SPECS[0]
    mismatched_source_id = mismatched_spec["source_id"]
    mismatched_event_id = mismatched_spec["event_id"]
    registry, receipts, failures, raw_only, capture = _capture(
        tmp_path,
        marker_mismatch=(mismatched_source_id,),
    )

    assert capture["status"] == "PARTIAL"
    assert capture["captured_event_count"] == expected_count - 1
    assert capture["marker_mismatch_count"] == 1
    # Marker-mismatched pages still retain an unlinked digest-only receipt.
    assert len(receipts) == expected_count
    assert len(failures) == 1
    assert failures[0]["raw_receipt_id"] in {receipt["receipt_id"] for receipt in receipts}

    result = _capture_event_timeline_registry(
        registry,
        "2026-11-12T05:00:00.000000Z",
        raw_receipts=receipts,
    )
    assert result["event_count"] == expected_count
    assert result["receipt_complete"] is False
    assert result["public_receipt_relinkage"]["linked_event_count"] == expected_count - 1
    statuses = {event["event_id"]: event["receipt_status"] for event in result["timeline"]["event_timeline"]}
    assert statuses[mismatched_event_id] == "MISSING_RAW_RECEIPT_HASH"


def test_future_primary_event_receipts_are_not_backdated_or_linked(tmp_path):
    expected_count = len(EVENT_SOURCE_CAPTURE_SPECS)
    registry, receipts, failures, raw_only, capture = _capture(
        tmp_path,
        received_at="2026-11-12T05:00:01.000000Z",
    )
    result = _capture_event_timeline_registry(
        registry,
        "2026-11-12T05:00:00.000000Z",
        raw_receipts=receipts,
    )
    assert result["event_count"] == expected_count
    assert result["receipt_complete"] is False
    assert result["public_receipt_relinkage"]["future_receipt_count"] == expected_count
    assert result["public_receipt_relinkage"]["linked_event_count"] == 0
    assert all(
        event["captured_at_utc"] == "2026-11-12T04:00:00Z"
        for event in result["timeline"]["event_timeline"]
    )


def test_tampered_primary_event_receipt_id_fails_closed(tmp_path):
    registry, receipts, failures, raw_only, capture = _capture(tmp_path)
    receipts[0]["receipt_id"] = "f" * 64
    with pytest.raises(XRPIngestionError, match="primary event receipt ID does not match canonical"):
        _capture_event_timeline_registry(
            registry,
            "2026-11-12T05:00:00.000000Z",
            raw_receipts=receipts,
        )


def test_primary_event_capture_schedule_is_daily_and_explicitly_overridable():
    before = datetime(2026, 11, 25, 0, 14, tzinfo=timezone.utc)
    daily = datetime(2026, 11, 25, 0, 15, tzinfo=timezone.utc)
    assert _event_source_capture_due(before, None) is False
    assert _event_source_capture_due(daily, None) is True
    assert _event_source_capture_due(daily, False) is False
    assert _event_source_capture_due(before, True) is True
    with pytest.raises(XRPIngestionError, match="capture_event_sources must be a boolean or None"):
        _event_source_capture_due(daily, "yes")


def test_ripple_coinbase_rlusd_primary_event_capture_spec_is_exact_and_allowlisted():
    spec = next(
        item for item in EVENT_SOURCE_CAPTURE_SPECS
        if item["source_id"] == "ripple_coinbase_rlusd_partnership_20261028"
    )
    assert spec["event_id"] == "ripple-coinbase-rlusd-partnership-2026-10-28"
    assert spec["source_uri"] == (
        "https://ripple.com/ripple-press/ripple-and-coinbase-partner-to-expand-access-to-rlusd/"
    )
    assert {
        "Ripple and Coinbase Partner to Expand Access to Ripple USD",
        "Oct 28, 2026",
        "Availability for Coinbase Global Exchange customers, including leveraging RLUSD as collateral, will follow.",
        "On Base, Ripple will provide liquidity to support the growth of RLUSD.",
    }.issubset(set(spec["required_markers"]))
    assert "ripple.com" in ALLOWED_HOSTS


def test_ripple_coinbase_primary_event_is_present_in_curated_registry():
    root = Path(__file__).resolve().parents[1]
    registry = json.loads(
        (root / "research" / "xrp_intelligence" / "event_registry_current.json").read_text(encoding="utf-8")
    )
    matches = [
        event for event in registry["events"]
        if event["event_id"] == "ripple-coinbase-rlusd-partnership-2026-10-28"
    ]
    assert len(matches) == 1
    event = matches[0]
    assert event["source_id"] == "ripple_coinbase_rlusd_partnership_20261028"
    assert event["source_url"] == (
        "https://ripple.com/ripple-press/ripple-and-coinbase-partner-to-expand-access-to-rlusd/"
    )
    assert event["source_status"] == "verified"
    assert event["raw_source_sha256"] is None
    assert event["captured_at_utc"] == "2026-11-26T13:13:03Z"


def test_ripple_xrp_holdings_primary_event_capture_spec_is_exact_and_allowlisted():
    spec = next(
        item for item in EVENT_SOURCE_CAPTURE_SPECS
        if item["source_id"] == "ripple_xrp_holdings_20260930"
    )
    assert spec["event_id"] == "ripple-xrp-holdings-2026-09-30"
    assert spec["source_uri"] == "https://ripple.com/xrp/"
    assert {
        "TOTAL XRP HELD BY RIPPLE: 36,809,481,946",
        "TOTAL XRP DISTRIBUTED: 63,176,123,712",
        "TOTAL XRP PLACED IN ESCROW: 31,700,000,000",
        "As of 09/30/26",
    }.issubset(set(spec["required_markers"]))
    assert "ripple.com" in ALLOWED_HOSTS


def test_ripple_xrp_holdings_event_is_present_in_curated_registry():
    root = Path(__file__).resolve().parents[1]
    registry = json.loads(
        (root / "research" / "xrp_intelligence" / "event_registry_current.json").read_text(encoding="utf-8")
    )
    matches = [
        event for event in registry["events"]
        if event["event_id"] == "ripple-xrp-holdings-2026-09-30"
    ]
    assert len(matches) == 1
    event = matches[0]
    assert event["source_id"] == "ripple_xrp_holdings_20260930"
    assert event["source_url"] == "https://ripple.com/xrp/"
    assert event["source_status"] == "verified"
    assert event["raw_source_sha256"] is None
    assert event["captured_at_utc"] == "2026-11-26T20:17:00Z"



@pytest.mark.parametrize(
    ("source_id", "event_id", "source_uri", "host", "markers"),
    [
        (
            "occ_ripple_national_trust_bank_cas_20261026",
            "ripple-national-trust-bank-occ-effective-2026-10-26",
            "https://apps.occ.gov/CAS/home/details?FilingID=RjzoD2gxmYOv&FilingSubtypeID=1093&FilingTypeID=2",
            "apps.occ.gov",
            ("2025-Charter-342347", "Ripple National Trust Bank", "Consummated/Effective", "10/26/2026"),
        ),
        (
            "occ_coinbase_national_trust_bank_20261106",
            "coinbase-national-trust-bank-occ-effective-2026-11-06",
            "https://apps.occ.gov/CAS/home/details?FilingID=3RAoRRek6o4j&FilingSubtypeID=1093&FilingTypeID=2",
            "apps.occ.gov",
            ("2025-Charter-343449", "Coinbase National Trust Company", "Consummated/Effective", "11/06/2026"),
        ),
        (
            "pnc_coinbase_usdc_pilot_20261109",
            "pnc-coinbase-usdc-incoming-pilot-2026-11-09",
            "https://pnc.mediaroom.com/2026-11-09-PNC-Bank-Launches-Incoming-Stablecoin-Payments-for-Corporate-and-Institutional-Banking-Clients",
            "pnc.mediaroom.com",
            ("Nov. 9, 2026", "USDC", "Ethereum blockchain", "Coinbase Payment products"),
        ),
        (
            "dbs_circle_usdc_access_20261118",
            "dbs-circle-usdc-institutional-access-2026-11-18",
            "https://www.dbs.com/newsroom/DBS_and_Circle_expand_institutional_access_to_USDC_in_Asia",
            "www.dbs.com",
            ("Singapore, 18 Nov 2026", "USDC", "24/7 USD-USDC settlement", "Project BLOOM"),
        ),
        (
            "sbi_holdings_circle_investment_release_20250609",
            "sbi-circle-investment-and-ripple-equity-stake-20250605",
            "https://www.sbigroup.co.jp/news/2025/0609_15491.html",
            "www.sbigroup.co.jp",
            ("2025年6月9日", "5,000万ドル", "SBIホールディングス", "Circle社", "約9%の株式を保有"),
        ),
        (
            "sbi_circle_holdings_jv_establishment_20250822",
            "sbi-circle-holdings-jv-established-20250822",
            "https://www.sbigroup.co.jp/news/2025/0822_15679.html",
            "www.sbigroup.co.jp",
            ("2025年8月22日", "Circle Internet Holdings, Inc.", "合弁会社を設立", "USDC"),
        ),
        (
            "sbi_startale_open_standard_jpysc_ousd_20261016",
            "sbi-startale-open-standard-jpysc-ousd-20261016",
            "https://www.sbigroup.co.jp/news/2026/1016_16665.html",
            "www.sbigroup.co.jp",
            ("2026年10月16日", "Open Standard", "JPYSC", "Open USD（OUSD）", "実証実験を検討"),
        ),
        (
            "sbi_vc_trade_ripple_rlusd_japan_launch_2026_06_24",
            "sbi-vc-trade-rlusd-japan-availability-2026-06-24",
            "https://www.sbigroup.co.jp/news/pr/2026/0624_16424.html",
            "www.sbigroup.co.jp",
            ("2026年6月24日", "RLUSD", "Ripple Labs Inc.", "イーサリアムチェーンのみの対応となります"),
        ),
    ],
)
def test_additional_first_party_event_specs_are_exact_and_present_in_registry(
    source_id, event_id, source_uri, host, markers
):
    spec = next(item for item in EVENT_SOURCE_CAPTURE_SPECS if item["source_id"] == source_id)
    assert spec["event_id"] == event_id
    assert spec["source_uri"] == source_uri
    assert set(markers).issubset(set(spec["required_markers"]))
    assert host in ALLOWED_HOSTS

    root = Path(__file__).resolve().parents[1]
    registry = json.loads(
        (root / "research" / "xrp_intelligence" / "event_registry_current.json").read_text(encoding="utf-8")
    )
    matches = [event for event in registry["events"] if event["event_id"] == event_id]
    assert len(matches) == 1
    assert matches[0]["source_id"] == source_id
    assert matches[0]["source_url"] == source_uri
    assert matches[0]["source_status"] == "verified"
