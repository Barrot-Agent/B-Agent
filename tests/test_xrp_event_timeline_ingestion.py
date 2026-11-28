from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from barrot_agent.evolution.xrp_public_ingestion import (
    XRPIngestionError,
    _capture_event_timeline_registry,
)

CUTOFF = "2026-11-12T05:00:00Z"


def _event(event_id: str, *, stance: str = "supports", captured_at: str = "2026-11-12T04:00:00Z"):
    return {
        "event_id": event_id,
        "event_type": "corporate",
        "event_name": f"Event {event_id}",
        "hypothesis_id": "evernorth-capital",
        "domain": "institutional-capital",
        "hypothesis": "Evernorth registered resale capacity may create equity supply.",
        "counter_hypothesis": "Registered shares are not completed sales or XRP sales.",
        "claim": f"Evidence {event_id}.",
        "source_id": f"source-{event_id}",
        "source_name": f"Publisher {event_id}",
        "source_url": f"https://publisher-{event_id}.example/research",
        "independence_group": f"publisher-{event_id}",
        "source_status": "verified",
        "stance": stance,
        "event_status": "occurred",
        "event_time_utc": "2026-11-11T20:00:00Z",
        "source_published_at_utc": "2026-11-11T20:01:00Z",
        "available_at_utc": captured_at,
        "captured_at_utc": captured_at,
        "raw_source_sha256": None,
        "assumptions": ["The publisher timestamp is accurate."],
        "falsification_conditions": ["A subsequent primary filing reverses the claim."],
        "related_entities": ["Evernorth"],
        "tags": ["XRP"],
    }


def _write_registry(path: Path, events):
    path.write_text(
        json.dumps(
            {
                "artifact_type": "barrot.xrp.event_registry",
                "schema_version": "1.0.0",
                "registry_version": "test",
                "captured_at_utc": "2026-11-12T04:00:00Z",
                "events": events,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def test_registry_builds_cutoff_safe_scenarios_and_preserves_minority_objection(tmp_path):
    path = tmp_path / "events.json"
    _write_registry(path, [_event("support"), _event("contrary", stance="contradicts")])
    result = _capture_event_timeline_registry(path, CUTOFF)
    scenario = result["timeline"]["scenario_set"]["scenarios"][0]
    assert result["registry_status"] == "LOADED"
    assert result["registry_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert result["event_count"] == 2
    assert result["scenario_count"] == 1
    assert scenario["disagreement_present"] is True
    assert scenario["minority_objection_count"] == 1
    assert result["receipt_complete"] is False
    assert result["model_eligible"] is False
    assert result["forecast_status"] == "NOT_ISSUED"
    assert result["directional_forecast"] is False
    assert result["timeline"]["event_timeline"][0]["receipt_status"] == "MISSING_RAW_RECEIPT_HASH"


def test_registry_excludes_evidence_captured_after_cutoff(tmp_path):
    path = tmp_path / "events.json"
    _write_registry(path, [_event("late", captured_at="2026-11-12T05:00:01Z")])
    result = _capture_event_timeline_registry(path, CUTOFF)
    assert result["event_count"] == 0
    assert result["timeline"]["excluded_events"][0]["reason"] == "not_captured_by_data_cutoff"
    assert result["model_eligible"] is False


def test_missing_registry_emits_explicit_empty_not_forecast(tmp_path):
    result = _capture_event_timeline_registry(tmp_path / "missing.json", CUTOFF)
    assert result["registry_status"] == "MISSING"
    assert result["event_count"] == 0
    assert result["scenario_count"] == 0
    assert result["forecast_status"] == "NOT_ISSUED"
    assert result["model_eligible"] is False


def test_invalid_registry_schema_fails_closed(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"artifact_type": "wrong", "schema_version": "1.0.0", "events": []}), encoding="utf-8")
    with pytest.raises(XRPIngestionError, match="artifact_type is invalid"):
        _capture_event_timeline_registry(path, CUTOFF)




def _canonical_sec_document_receipt(source_url: str, captured_at: str, raw_hash: str = "a" * 64):
    receipt = {
        "source_id": "sec_edgar_document_evernorth_0001628280-26-072223",
        "source_uri": source_url,
        "captured_at_utc": captured_at,
        "source_data_as_of_utc": None,
        "source_http_date": None,
        "raw_content_sha256": raw_hash,
        "payload_size_bytes": 123,
        "raw_payload_path": None,
        "raw_bytes_retained": False,
        "raw_retention_reason": "SEC source bytes are digest-only in this fixture",
        "model_eligible_source": False,
        "raw_only_reason": "sec_edgar_primary_regulatory_data_research_only_not_market_feature",
        "source_http_headers": {},
    }
    canonical = json.dumps(
        receipt,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    receipt["receipt_id"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return receipt


def test_immutable_sec_accession_receipt_relinks_event_at_new_known_at_time(tmp_path):
    path = tmp_path / "events.json"
    source_url = "https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm"
    event = _event("sec-resale-event")
    event["source_id"] = "sec_evernorth_424b3"
    event["source_name"] = "SEC Evernorth 424B3"
    event["source_url"] = source_url
    _write_registry(path, [event])
    receipt = _canonical_sec_document_receipt(source_url, "2026-11-12T04:30:00Z")

    result = _capture_event_timeline_registry(
        path,
        "2026-11-12T05:00:00Z",
        raw_receipts=[receipt],
    )
    linked = result["timeline"]["event_timeline"][0]
    assert result["receipt_complete"] is True
    assert result["receipt_relinkage"]["status"] == "LINKED"
    assert result["receipt_relinkage"]["linked_event_count"] == 1
    assert linked["captured_at_utc"] == "2026-11-12T04:30:00Z"
    assert linked["available_at_utc"] == "2026-11-12T04:30:00Z"
    assert linked["raw_source_sha256"] == receipt["raw_content_sha256"]
    assert linked["receipt_status"] == "VERIFIED_CANONICAL_RECEIPT"
    assert linked["canonical_receipt_id"] == receipt["receipt_id"]
    assert linked["receipt_source_id_match"] is False
    assert result["receipt_linkage"]["source_id_mismatch_count"] == 1
    assert linked["receipt_linkage_method"] == "immutable_sec_accession_document_recapture"
    assert linked["source_capture_history"][0]["captured_at_utc"] == "2026-11-12T04:00:00Z"
    assert linked["source_capture_history"][-1]["receipt_id"] == receipt["receipt_id"]
    assert result["model_eligible"] is False
    assert result["forecast_status"] == "NOT_ISSUED"


def test_sec_event_receipt_with_tampered_canonical_id_fails_closed(tmp_path):
    path = tmp_path / "events.json"
    source_url = "https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm"
    event = _event("sec-tampered-receipt")
    event["source_id"] = "sec_evernorth_424b3"
    event["source_url"] = source_url
    _write_registry(path, [event])
    receipt = _canonical_sec_document_receipt(source_url, "2026-11-12T04:30:00Z")
    receipt["receipt_id"] = "f" * 64

    with pytest.raises(XRPIngestionError, match="receipt ID does not match canonical"):
        _capture_event_timeline_registry(
            path,
            "2026-11-12T05:00:00Z",
            raw_receipts=[receipt],
        )


def test_immutable_sec_accession_receipt_after_cutoff_is_not_used(tmp_path):
    path = tmp_path / "events.json"
    source_url = "https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm"
    event = _event("sec-future-receipt")
    event["source_id"] = "sec_evernorth_424b3"
    event["source_url"] = source_url
    _write_registry(path, [event])
    receipt = _canonical_sec_document_receipt(source_url, "2026-11-12T05:00:01Z")

    result = _capture_event_timeline_registry(
        path,
        "2026-11-12T05:00:00Z",
        raw_receipts=[receipt],
    )
    unlinked = result["timeline"]["event_timeline"][0]
    assert result["receipt_complete"] is False
    assert result["receipt_relinkage"]["future_receipt_count"] == 1
    assert unlinked["captured_at_utc"] == "2026-11-12T04:00:00Z"
    assert unlinked["raw_source_sha256"] is None
    assert unlinked["receipt_status"] == "MISSING_RAW_RECEIPT_HASH"
    assert unlinked["source_capture_history"] == []
    assert result["model_eligible"] is False


def test_mutable_or_non_sec_event_source_is_not_relinked(tmp_path):
    path = tmp_path / "events.json"
    event = _event("mutable-source")
    _write_registry(path, [event])
    receipt = _canonical_sec_document_receipt(
        "https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm",
        "2026-11-12T04:30:00Z",
    )

    result = _capture_event_timeline_registry(
        path,
        "2026-11-12T05:00:00Z",
        raw_receipts=[receipt],
    )
    unlinked = result["timeline"]["event_timeline"][0]
    assert result["receipt_complete"] is False
    assert result["receipt_relinkage"]["linked_event_count"] == 0
    assert unlinked["raw_source_sha256"] is None
    assert unlinked["receipt_status"] == "MISSING_RAW_RECEIPT_HASH"




def test_ambiguous_latest_sec_receipts_fail_closed(tmp_path):
    path = tmp_path / "events.json"
    source_url = "https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm"
    event = _event("sec-ambiguous-event")
    event["source_id"] = "sec_evernorth_424b3"
    event["source_url"] = source_url
    _write_registry(path, [event])
    receipts = [
        _canonical_sec_document_receipt(source_url, "2026-11-12T04:30:00Z", "a" * 64),
        _canonical_sec_document_receipt(source_url, "2026-11-12T04:30:00Z", "b" * 64),
    ]

    result = _capture_event_timeline_registry(
        path,
        "2026-11-12T05:00:00Z",
        raw_receipts=receipts,
    )
    unlinked = result["timeline"]["event_timeline"][0]
    assert result["receipt_complete"] is False
    assert result["receipt_relinkage"]["ambiguous_event_count"] == 1
    assert result["receipt_relinkage"]["linked_event_count"] == 0
    assert unlinked["raw_source_sha256"] is None
    assert unlinked["receipt_status"] == "MISSING_RAW_RECEIPT_HASH"
    assert result["model_eligible"] is False


def test_xrp_ingestion_workflow_publishes_the_event_timeline_artifact():
    workflow = Path(".github/workflows/xrp-public-ingestion.yml").read_text(encoding="utf-8")
    assert r"xrp-public-events-${{ github.run_id }}" in workflow
    assert "artifacts/xrp_ingestion/event_timeline.json" in workflow


def test_current_registry_retains_market_and_sbi_resale_counterevidence_without_raw_receipts():
    path = Path("research/xrp_intelligence/event_registry_current.json")
    registry = json.loads(path.read_text(encoding="utf-8"))
    assert registry["registry_version"].startswith("run")
    assert registry["captured_at_utc"].endswith("Z")
    assert registry["model_eligible"] is False
    assert registry["forecast_status"] == "NOT_ISSUED"
    validated = _capture_event_timeline_registry(path, registry["captured_at_utc"])
    assert validated["registry_status"] == "LOADED"
    assert validated["event_count"] > 0
    expected = {
        "sbi-remit-xrp-odl-corridors-2023-09-06",
        "sbi-remit-nium-fiat-alternative-rail-2025-06-30",
        "sbi-remit-cambodia-dlt-rail-2025-10-28",
        "sbi-remit-cumulative-turnover-all-rails-2026-05-27",
        "sbi-ripple-asia-dsrv-feasibility-2026-02-24",
        "sbi-ripple-asia-tokenized-deposit-poc-2026-02-26",
        "sbi-ripple-asia-xrpl-token-issuance-platform-2026-03-26",
        "sbi-start-bond-jpy-debt-xrp-reward-2026-03-24",
        "sbi-visa-crypto-card-xrp-rewards-2026-05-01",
        "sbi-holdings-ripple-stake-and-xrp-supply-2026-04-27",
        "doppler-sbi-digital-finance-institutional-xrp-partnership-2026-07-13",
        "ripple-national-trust-bank-occ-effective-2026-10-26",
        "ripple-coinbase-rlusd-partnership-2026-10-28",
        "xrp-okx-spot-2026-11-12T0447Z",
        "xrp-kraken-spot-2026-11-12T0502Z",
        "xrp-fuelmaps-depth-2026-11-12T0400Z",
        "xrp-liqwall-derivatives-2026-11-12T0502Z",
        "xrp-etf-flows-2026-11-10",
        "evernorth-sbi-lockup-ambiguity-2026-11-12",
        "pnc-coinbase-usdc-incoming-pilot-2026-11-09",
        "circle-usdc-xrpl-native-2025-06-12",
        "evernorth-2026-11-09-capital-cash-vs-in-kind",
        "flare-fxrp-one-year-2026-09-24",
        "evernorth-actual-capital-warrant-note-eloc-2026-11-13",
        "sbic-east-chatgpt-seminar-microsoft-speaker-2025-02-26",
        "sbic-west-chatgpt-generative-ai-seminar-2024-10-23",
        "xrp-okx-spot-basis-gate-2026-11-16T0058Z",
        "xrp-bybit-spot-stale-cross-venue-observation-2026-11-16T0001Z",
        "evernorth-coinbase-principal-market-xrp-valuation-2026-09-30",
        "standard-chartered-rlusd-xrpl-custody-lmax-collateral-plan-2026-10-12",
        "xrpl-amendment-rollcall-2026-11-16T0400Z",
        "xrpl-amendment-rollcall-2026-11-16T0452Z",
    }
    by_id = {event["event_id"]: event for event in registry["events"]}
    assert expected <= set(by_id)
    assert all(by_id[event_id]["raw_source_sha256"] is None for event_id in expected)
    assert "SBI is not named" in by_id["evernorth-sbi-lockup-ambiguity-2026-11-12"]["counter_hypothesis"]
    assert "on Ethereum" in by_id["pnc-coinbase-usdc-incoming-pilot-2026-11-09"]["claim"]
    circle_usdc = by_id["circle-usdc-xrpl-native-2025-06-12"]
    assert "natively on XRPL mainnet" in circle_usdc["claim"]
    assert "without XRP as the bridge asset" in circle_usdc["counter_hypothesis"]
    assert circle_usdc["raw_source_sha256"] is None
    evernorth = by_id["evernorth-2026-11-09-capital-cash-vs-in-kind"]
    assert "$272.6 million" in evernorth["claim"]
    assert "388,910,554 XRP" in evernorth["claim"]
    assert "yield strategies commenced following the Closing" in evernorth["claim"]
    assert "SBI Holdings, Inc." in evernorth["claim"]
    sbi_remit = by_id["sbi-remit-xrp-odl-corridors-2023-09-06"]
    assert "SBI VC Trade sends XRP in real time" in sbi_remit["claim"]
    assert "undisclosed" in sbi_remit["counter_hypothesis"]
    sbi_rails = by_id["sbi-remit-nium-fiat-alternative-rail-2025-06-30"]
    assert "more than 190 countries" in sbi_rails["claim"]
    assert "does not identify XRP" in sbi_rails["claim"]
    issuance = by_id["sbi-ripple-asia-xrpl-token-issuance-platform-2026-03-26"]
    assert "third-party prepaid-payment-instrument issuer" in issuance["claim"]
    assert "does not necessarily mean XRP is the bridge asset" in issuance["counter_hypothesis"]
    start_bond = by_id["sbi-start-bond-jpy-debt-xrp-reward-2026-03-24"]
    assert "2.15% fixed annual JPY coupon" in start_bond["claim"]
    assert "XRP reward" in start_bond["claim"]
    assert "not coupon or principal" in start_bond["claim"]
    assert start_bond["raw_source_sha256"] is None
    visa_card = by_id["sbi-visa-crypto-card-xrp-rewards-2026-05-01"]
    assert "XRP" in visa_card["claim"]
    assert "source of reward XRP is not disclosed" in visa_card["claim"]
    sbi_stake = by_id["sbi-holdings-ripple-stake-and-xrp-supply-2026-04-27"]
    assert "approximately 9% Ripple equity stake" in sbi_stake["claim"]
    assert "33.20B in Ripple escrow" in sbi_stake["claim"]
    doppler = by_id["doppler-sbi-digital-finance-institutional-xrp-partnership-2026-07-13"]
    assert doppler["source_status"] == "provisional"
    assert "No corresponding SBI announcement" in doppler["claim"]
    occ = by_id["ripple-national-trust-bank-occ-effective-2026-10-26"]
    assert "trust powers requested" in occ["claim"]
    rlusd = by_id["sbi-vc-trade-rlusd-japan-availability-2026-06-24"]
    assert "Ethereum only" in rlusd["claim"]
    assert "XRPL deposits/withdrawals are not supported" in rlusd["claim"]
    circle = by_id["circle-q3-2026-usdc-and-cpn-results-2026-11-04"]
    assert "$610M net" in circle["claim"]
    assert "-$1.387B net" in circle["claim"]
    assert "no significant operating results" in circle["claim"]
    assert "39.9%" in evernorth["claim"]
    assert evernorth["event_status"] == "occurred"
    assert "does not disclose a 400 million XRP allocation" in evernorth["counter_hypothesis"]
    flare = by_id["flare-fxrp-one-year-2026-09-24"]
    assert "145.2 million FXRP" in flare["claim"]
    assert "remains on XRPL" in flare["counter_hypothesis"]
    actual_capital = by_id["evernorth-actual-capital-warrant-note-eloc-2026-11-13"]
    assert "3,073,366" in actual_capital["claim"]
    assert "$35.3 million gross" in actual_capital["claim"]
    assert "$30.0 million principal/proceeds before transaction expenses" in actual_capital["claim"]
    assert "$29.0 million remains after the advisory fee alone" in actual_capital["claim"]
    assert "8,666,279" in actual_capital["claim"]
    assert "5,218,935" in actual_capital["claim"]
    assert "not proof of XRP purchases" in actual_capital["counter_hypothesis"]
    assert actual_capital["raw_source_sha256"] is None
    sbic = by_id["sbic-east-chatgpt-seminar-microsoft-speaker-2025-02-26"]
    assert "Microsoft Japan" in sbic["claim"]
    assert "no OpenAI contract" in sbic["claim"]
    assert sbic["source_status"] == "verified"
    assert sbic["raw_source_sha256"] is None
    sbic_west = by_id["sbic-west-chatgpt-generative-ai-seminar-2024-10-23"]
    assert "ChatGPT" in sbic_west["claim"]
    assert "Taichi Kakinuma" in sbic_west["claim"]
    assert "does not identify OpenAI as a contracting party" in sbic_west["claim"]
    assert sbic_west["event_status"] == "unknown"
    assert sbic_west["raw_source_sha256"] is None
    amendment_0452 = by_id["xrpl-amendment-rollcall-2026-11-16T0452Z"]
    assert "29 yes votes are required" in amendment_0452["claim"]
    assert "SingleAssetVault had 23 yes votes" in amendment_0452["claim"]
    assert amendment_0452["source_status"] == "provisional"
    assert amendment_0452["event_time_utc"] == "2026-11-16T04:52:00Z"
    assert amendment_0452["raw_source_sha256"] is None
    okx = by_id["xrp-okx-spot-basis-gate-2026-11-16T0058Z"]
    assert "63.905 seconds" in okx["claim"]
    assert "USD normalization is rejected" in okx["claim"]
    assert okx["raw_source_sha256"] is None
    bybit = by_id["xrp-bybit-spot-stale-cross-venue-observation-2026-11-16T0001Z"]
    assert "3,607.157 seconds" in bybit["claim"]
    assert "300-second freshness gate" in bybit["claim"]
    assert bybit["raw_source_sha256"] is None
    assert bybit["hypothesis_id"] == "xrp-bybit-stale-quote-freshness-2026-11-16"
    assert bybit["hypothesis_id"] != okx["hypothesis_id"]
    coinbase = by_id["evernorth-coinbase-principal-market-xrp-valuation-2026-09-30"]
    assert "evernorth-coinbase-principal-market-xrp-valuation-2026-09-30" in registry["run180_update"]["added_event_ids"]
    assert "selected Coinbase as the principal market" in coinbase["claim"]
    assert "not proof" in coinbase["counter_hypothesis"]
    assert "BitGo Trust" in coinbase["claim"]
    assert coinbase["raw_source_sha256"] is None
    standard_chartered = by_id["standard-chartered-rlusd-xrpl-custody-lmax-collateral-plan-2026-10-12"]
    assert "custody support for RLUSD issued on XRPL is live" in standard_chartered["claim"]
    assert "subject to final documentation" in standard_chartered["counter_hypothesis"]
    assert "does not imply native XRP purchases" in standard_chartered["counter_hypothesis"]
    assert standard_chartered["raw_source_sha256"] is None
    xrpl_votes = by_id["xrpl-amendment-rollcall-2026-11-16T0400Z"]
    assert "23 yes votes" in xrpl_votes["claim"]
    assert "29 yes votes are required" in xrpl_votes["claim"]
    assert "zero amendments in the 14-day activation countdown" in xrpl_votes["claim"]
    assert xrpl_votes["source_status"] == "provisional"
    assert xrpl_votes["raw_source_sha256"] is None
    cbxrp_reserves = by_id["coinbase-cbxrp-proof-of-reserves-2026-11-16"]
    assert "153,008,338.56 XRP" in cbxrp_reserves["claim"]
    assert "153,006,092.03 cbXRP" in cbxrp_reserves["claim"]
    assert "rather than a third-party audit" in cbxrp_reserves["counter_hypothesis"]
    assert cbxrp_reserves["raw_source_sha256"] is None
    morpho_liquidations = by_id["morpho-cbxrp-liquidation-window-2026-11-07-to-13"]
    assert "4,016,076.342260 USDC" in morpho_liquidations["claim"]
    assert "4,181,584.301387 cbXRP" in morpho_liquidations["claim"]
    assert "No native XRP redemption or sale was traced" in morpho_liquidations["claim"]
    assert morpho_liquidations["raw_source_sha256"] is None
    morpho_market = by_id["morpho-base-usdc-cbxrp-market-snapshot-2026-11-16T0244Z"]
    assert "90.59%" in morpho_market["claim"]
    assert "0.960902" in morpho_market["claim"]
    assert "191.62M" in morpho_market["claim"]
    assert morpho_market["raw_source_sha256"] is None
    coinglass = by_id["coinglass-xrp-futures-live-snapshot-2026-11-16T0244Z"]
    assert "4.50M" in coinglass["claim"]
    assert "33.42M" in coinglass["claim"]
    assert "not averaged" in coinglass["claim"]
    assert coinglass["raw_source_sha256"] is None
    evernorth = by_id["evernorth-q3-2026-preclose-liquidity-and-postclose-xrp-restriction-release"]
    assert "346,284,972 XRP" in evernorth["claim"]
    assert "126,791,458 XRP" in evernorth["claim"]
    assert "$9.7M" in evernorth["claim"]
    assert "five business days" in evernorth["claim"]
    assert "$214.05M" in evernorth["claim"]
    assert "84,365,876 XRP" in evernorth["claim"]
    assert "Coinbase" in evernorth["claim"] and "BitGo Trust" in evernorth["claim"]
    assert "No XRP sale, exchange deposit or redemption is disclosed" in evernorth["counter_hypothesis"]
    assert evernorth["raw_source_sha256"] is None
    missing_receipts = sum(1 for event in registry["events"] if not event.get("raw_source_sha256"))
    assert registry["source_receipt_status"].startswith(
        f"{missing_receipts} of {len(registry['events'])} curated events"
    )
    assert missing_receipts == len(registry["events"])
    assert registry["model_eligible"] is False
    missing_publisher_timestamps = sum(1 for event in registry["events"] if not event.get("source_published_at_utc"))
    # The registry-level coverage object is canonical. Run metadata has used
    # both legacy and explicit field names, so validate the newest available
    # block without silently selecting an older run that uses only the legacy key.
    coverage = registry["publisher_timestamp_coverage"]
    assert coverage["missing_exact_publisher_timestamps"] == missing_publisher_timestamps
    assert (
        coverage["exact_publisher_timestamps"] + missing_publisher_timestamps
        == len(registry["events"])
    )
    run_metadata = [
        (int(key[3:].split("_", 1)[0]), value)
        for key, value in registry.items()
        if key.startswith("run")
        and key[3:].split("_", 1)[0].isdigit()
        and isinstance(value, dict)
        and (
            "missing_publisher_timestamps" in value
            or "missing_exact_publisher_timestamp_count" in value
        )
    ]
    assert run_metadata
    latest_run_metadata = max(run_metadata, key=lambda item: item[0])[1]
    latest_missing_count = latest_run_metadata.get(
        "missing_publisher_timestamps",
        latest_run_metadata.get("missing_exact_publisher_timestamp_count"),
    )
    assert latest_missing_count == missing_publisher_timestamps
    timeline = _capture_event_timeline_registry(path, registry["captured_at_utc"])
    assert timeline["registry_status"] == "LOADED"
    assert timeline["event_count"] == len(registry["events"])
    assert timeline["receipt_complete"] is False
    assert timeline["model_eligible"] is False
    assert timeline["forecast_status"] == "NOT_ISSUED"
    assert timeline["directional_forecast"] is False
    assert timeline["scenario_count"] > 0


def test_registry_verifies_exact_canonical_receipt_metadata(tmp_path):
    path = tmp_path / "events.json"
    item = _event("verified")
    item["raw_source_sha256"] = "a" * 64
    _write_registry(path, [item])
    receipt = {
        "receipt_id": "receipt-verified",
        "source_id": item["source_id"],
        "source_uri": item["source_url"],
        "captured_at_utc": item["captured_at_utc"],
        "raw_content_sha256": item["raw_source_sha256"],
        "raw_bytes_retained": True,
    }

    result = _capture_event_timeline_registry(path, CUTOFF, raw_receipts=[receipt])

    assert result["receipt_complete"] is True
    assert result["receipt_linkage"]["verified_receipt_count"] == 1
    assert result["timeline"]["event_timeline"][0]["canonical_receipt_id"] == "receipt-verified"


def test_registry_does_not_link_url_only_match_from_another_capture_time(tmp_path):
    path = tmp_path / "events.json"
    item = _event("url-only")
    _write_registry(path, [item])
    receipt = {
        "receipt_id": "receipt-later",
        "source_id": item["source_id"],
        "source_uri": item["source_url"],
        "captured_at_utc": "2026-11-12T04:00:01Z",
        "raw_content_sha256": "a" * 64,
        "raw_bytes_retained": True,
    }

    result = _capture_event_timeline_registry(path, CUTOFF, raw_receipts=[receipt])

    assert result["receipt_complete"] is False
    assert result["receipt_linkage"]["url_match_count"] == 1
    assert result["receipt_linkage"]["url_capture_time_match_count"] == 0
    assert result["receipt_linkage"]["verified_receipt_count"] == 0
    assert result["timeline"]["event_timeline"][0]["receipt_status"] == "MISSING_RAW_RECEIPT_HASH"


def test_sbi_jpysc_reserve_allocation_is_research_only_and_not_xrp_collateral():
    import json
    from pathlib import Path

    registry_path = (
        Path(__file__).resolve().parents[1]
        / "research"
        / "xrp_intelligence"
        / "event_registry_current.json"
    )
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    event = next(
        item for item in registry["events"]
        if item["event_id"] == "sbi-jpysc-short-term-jgb-reserve-2026-09-07"
    )

    assert event["source_status"] == "verified"
    assert event["source_url"] == "https://www.sbigroup.co.jp/news/2026/0907_16567.html"
    assert event["source_published_at_utc"] is None
    assert event["event_time_precision"] == "date-only"
    assert event["raw_source_sha256"] is None
    assert event["model_eligible"] is False
    assert "JPY 1.0 billion" in event["claim"]
    assert "JPY 20.1 billion" in event["claim"]
    assert "JPY 6.9 billion" in event["claim"]
    assert "does not establish XRP collateral" in event["counter_hypothesis"]
    assert event["independence_group"] == "sbi-vc-trade-official-jpysc"
