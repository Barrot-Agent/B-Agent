"""Regression tests for the follow-up append-only XRP review corrections."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLLOWUP = ROOT / "research" / "xrp_intelligence" / "20261104T180409Z-xrp-research-followup-corrections.json"
BASE_OVERLAY = ROOT / "research" / "xrp_intelligence" / "20261104T144241Z-archive-review-corrections-and-point-in-time-quarantine.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_second_kraken_observation_is_labeled_as_utc_daily_open():
    correction = load_json(FOLLOWUP)
    target = load_json(
        ROOT / "research" / "xrp_intelligence" / "20261104T131226Z-circle-q3-coinbase-ripple-bny-sbic-market-addendum.json"
    )
    entry = next(
        item for item in correction["correction_overlay"]["entries"]
        if item["correction_id"] == "C18_KRAKEN_DAILY_OPEN_SECOND_ADDENDUM"
    )
    observation = target["market_observations"][0]
    assert observation["venue"] == "Kraken"
    assert observation["open_24h_usd"] == entry["original_value"] == 1.27513
    assert entry["canonical_field_name"] == "daily_open_usd"
    assert entry["canonical_path"] == "$.market_observations[0].daily_open_usd"
    assert entry["interpretation"] == "UTC-day open; not a rolling 24-hour open"
    assert entry["derived_rolling_24h_return"] == "not_available"
    assert entry["evidence_source_ids"] == ["kraken_ticker_api_docs"]
    assert entry["model_eligible"] is False
    assert correction["preservation"]["original_artifacts_modified"] is False


def test_occ_cas_crosswalk_is_entity_scoped_and_supersedes_unscoped_replacement():
    correction = load_json(FOLLOWUP)
    base = load_json(BASE_OVERLAY)
    target = load_json(
        ROOT / "research" / "xrp_intelligence" / "20261103T223100Z-circle-ripple-coinbase-bank-charter-stablecoin-network.json"
    )
    old_c01 = next(
        item for item in base["correction_overlay"]["entries"]
        if item["correction_id"] == "C01_SOURCE_CITATION_CROSSWALK"
    )
    unscoped = [
        item for item in old_c01["replacements"]
        if item.get("old_url") == "https://www.occ.gov/topics/charters-and-licensing/interpretations-and-actions/2026/"
        and item.get("canonical_url", "").endswith("FilingID=RjzoD2gxmYOv&FilingSubtypeID=1093&FilingTypeID=2")
    ]
    assert len(unscoped) == 1
    assert not unscoped[0].get("target_field")

    entry = next(
        item for item in correction["correction_overlay"]["entries"]
        if item["correction_id"] == "C19_OCC_CROSSWALK_ENTITY_SCOPE"
    )
    assert entry["supersedes_correction_id"] == "C01_SOURCE_CITATION_CROSSWALK"
    replacements = entry["canonical_replacements"]
    assert len(replacements) == 3
    assert all(item.get("target_field") for item in replacements)
    assert len({item["target_field"] for item in replacements}) == 3

    expected = {
        "$.bank_charter_status.circle.sources[1]": (
            "https://www.occ.gov/topics/charters-and-licensing/interpretations-and-actions/2026/",
            "https://apps.occ.gov/CAS/home/details?FilingID=D79Z71vmerN8&FilingSubtypeID=1093&FilingTypeID=2",
            "circle",
        ),
        "$.bank_charter_status.ripple.sources[0]": (
            "https://apps.occ.gov/CAAS_CATS/CAAS_Details.aspx?FilingTypeID=5&FilingID=363617",
            "https://apps.occ.gov/CAS/home/details?FilingID=RjzoD2gxmYOv&FilingSubtypeID=1093&FilingTypeID=2",
            "ripple",
        ),
        "$.bank_charter_status.coinbase.sources[1]": (
            "https://apps.occ.gov/CAAS_CATS/CAAS_Details.aspx?FilingTypeID=5&FilingID=363617",
            "https://apps.occ.gov/CAS/home/details?FilingID=3RAoRRek6o4j&FilingSubtypeID=1093&FilingTypeID=2",
            "coinbase",
        ),
    }
    for item in replacements:
        old_url, canonical_url, entity = expected[item["target_field"]]
        assert item["entity"] == entity
        assert item["old_url"] == old_url
        assert item["canonical_url"] == canonical_url
        assert item["source_id"].startswith(entity if entity != "circle" else "circle")

    assert correction["correction_overlay"]["consumer_application_status"] == "NOT_EXECUTED_RESEARCH_ONLY_OVERLAY"
    assert correction["forecast_issued"] is False
    assert correction["model_eligible"] is False
