from __future__ import annotations

import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORRECTION = ROOT / "research" / "xrp_intelligence" / "20261108T034500Z-xrp-archive-integrity-and-pillars-correction.json"
ARCHIVE_REVIEW = ROOT / "research" / "xrp_intelligence" / "20261104T144241Z-archive-review-corrections-and-point-in-time-quarantine.json"
EVERNORTH = ROOT / "research" / "xrp_intelligence" / "20261104T134706Z-evernorth-close-actual-capital-sbi-ownership-reconciliation.json"
ADVANCE = ROOT / "research" / "xrp_intelligence" / "20261106T080100Z-evernorth-advance-funding-purchase-cost-correction.json"
DELAYED = ROOT / "research" / "xrp_intelligence" / "20261106T130046Z-evernorth-delayed-funding-capital-category-correction.json"
DELAYED_TARGET = ROOT / "research" / "xrp_intelligence" / "20261106-evernorth-delayed-funding-and-sbi-group-capital-reconciliation.json"
PILLARS_OBSERVATION = ROOT / "research" / "xrp_intelligence" / "20261104T141402Z-nine-platform-capability-authentication-observation.json"
PILLARS_SCRIPT = ROOT / "scripts" / "pillars_check.py"
PREIMAGE = ROOT / "research" / "xrp_intelligence" / "source_preimages" / "6d1a72976e13441525401ed8d1bb90e0b401f3aa.json"
ELOC_CURRENT = ROOT / "research" / "xrp_intelligence" / "20261106T043450Z-evernorth-eloc-dollar-cap-correction.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\\0" + raw).hexdigest()


def test_c09_supersedes_only_the_incorrect_C07_average_cost():
    correction = load(CORRECTION)
    c09 = next(item for item in correction["corrections"] if item["correction_id"] == "C09_EVERNORTH_PURCHASE_COST_SUPERSESSION")
    archive = load(ARCHIVE_REVIEW)
    c07 = next(item for item in archive["correction_overlay"]["entries"] if item["correction_id"] == "C07_EVERNORTH_CAPITAL_LEDGER")
    old_avg = next(item for item in c07["field_corrections"] if item["path"] == "$.xrp_asset_reconciliation.cash_funded_market_purchase.implied_average_cost_usd_per_xrp")
    assert old_avg["canonical_value"] == 214050000 / 84365876
    assert c09["supersedes_correction_id"] == "C07_EVERNORTH_CAPITAL_LEDGER"
    assert c09["superseded_value"] == old_avg["canonical_value"]
    assert c09["canonical_values"]["cash_received_exact_usd"] == 214049995
    assert c09["canonical_values"]["cash_received_summary_rounded_usd"] == 214050000
    assert c09["canonical_values"]["cash_used_for_xrp_purchase_usd"] == 214000000
    assert c09["canonical_values"]["restricted_cash_at_2025_12_31_usd"] == 49995
    assert c09["canonical_values"]["xrp_quantity_exact"] == 84365876.3625
    assert c09["canonical_values"]["issuer_reported_average_price_usd_per_xrp"] == 2.53657058
    assert c09["non_superseded_C07_corrections"]["additional_debt_capital_lender"] == "Ripple Labs Inc."
    assert c09["non_superseded_C07_corrections"]["duplicate_relationship_edges_removed_from_derived_view"] == 2


def test_purchase_cost_corrections_and_source_preimage_are_bound():
    correction = load(CORRECTION)
    sources = {item["path"]: item for item in correction["source_artifacts"]}
    assert git_blob_sha1(EVERNORTH) == sources[str(EVERNORTH.relative_to(ROOT))]["git_blob_sha"]
    assert git_blob_sha1(ADVANCE) == sources[str(ADVANCE.relative_to(ROOT))]["git_blob_sha"]
    assert git_blob_sha1(DELAYED) == sources[str(DELAYED.relative_to(ROOT))]["git_blob_sha"]
    assert git_blob_sha1(DELAYED_TARGET) == sources[str(DELAYED_TARGET.relative_to(ROOT))]["git_blob_sha"]
    assert git_blob_sha1(PREIMAGE) == "6d1a72976e13441525401ed8d1bb90e0b401f3aa"
    assert git_blob_sha1(ELOC_CURRENT) != git_blob_sha1(PREIMAGE)
    advance = load(ADVANCE)
    evidence = advance["primary_source_evidence"]
    assert evidence["cash_used_to_purchase_digital_assets_usd"] == 214000000
    assert evidence["advance_funding_cash_received_exact_usd"] == 214049995
    assert evidence["restricted_cash_at_2025_12_31_usd"] == 49995
    delayed = load(DELAYED)
    field = next(item for item in delayed["field_corrections"] if item["json_pointer"] == "/separate_capital_categories/2/amount_usd")
    assert field["corrected_value"] == 214000000
    assert field["original_value"] == 214100000


def test_delayed_funding_correction_prevents_double_counting():
    correction = load(DELAYED)
    target = load(DELAYED_TARGET)
    row = target["separate_capital_categories"][2]
    assert row["amount_usd"] == 214100000
    derived = dict(row)
    field = next(item for item in correction["field_corrections"] if item["json_pointer"] == "/separate_capital_categories/2/amount_usd")
    derived["amount_usd"] = field["corrected_value"]
    assert derived["amount_usd"] == 214000000
    amount_xrp_exact = next(item for item in correction["field_additions"] if item["field"] == "amount_xrp_exact")
    no_double_count = next(item for item in correction["field_additions"] if item["field"] == "do_not_add_delayed_subscriber_cash_separately")
    assert amount_xrp_exact["value"] == 84365876.3625
    assert derived["amount_usd"] != 214050000
    assert no_double_count["value"] is True


def test_c10_quarantines_historical_pillars_clean_result_without_http_status():
    correction = load(CORRECTION)
    c10 = next(item for item in correction["corrections"] if item["correction_id"] == "C10_PILLARS_FICTION_SCAN_HTTP_STATUS_INCONCLUSIVE")
    observation = load(PILLARS_OBSERVATION)
    item = next(x for x in observation["workflow"] if x["id"] == c10["target_observation_id"])
    assert item["status"] == c10["original_status"] == "PASS_SOURCE_ONLY"
    assert c10["canonical_status"] == "INCONCLUSIVE_HTTP_STATUS_NOT_CAPTURED"
    assert "without validating or recording HTTP status" in c10["canonical_detail"]
    assert c10["model_eligible"] is False
    assert "status_code != 200" in PILLARS_SCRIPT.read_text(encoding="utf-8")


def test_source_artifact_git_blob_bindings_match_exact_files():
    correction = load(CORRECTION)
    for source in correction["source_artifacts"]:
        path = ROOT / source["path"]
        if "corrected_git_blob_sha" in source:
            assert git_blob_sha1(path) == source["corrected_git_blob_sha"]
            continue
        assert git_blob_sha1(path) == source["git_blob_sha"]
