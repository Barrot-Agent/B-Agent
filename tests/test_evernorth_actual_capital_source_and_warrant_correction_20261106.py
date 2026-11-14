from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "research" / "xrp_intelligence"
ORIGINAL = ROOT / "20261106T154537Z-evernorth-actual-capital-eloc-warrant-reconciliation.json"
CORRECTION = ROOT / "20261106T154537Z-evernorth-actual-capital-source-and-warrant-correction.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_correction_is_bound_to_exact_original_artifact():
    correction = load(CORRECTION)
    assert correction["superseded_artifact_blob_sha"] == "5cafe9338521909969fac9a63b785df1aa944e2d"
    assert correction["supersedes_artifact_id"] == "evernorth_actual_capital_eloc_warrant_reconciliation_20261106T154537Z"


def test_evidence_urls_and_registration_effect_date_are_corrected():
    correction = load(CORRECTION)
    overrides = correction["source_overrides"]
    assert overrides["eloc_8k"]["url"].endswith("/evernorth-elocx8xk.htm")
    assert overrides["warrant_prospectus"]["url"].endswith("/d824062d424b3.htm")
    assert overrides["registration_disambiguation"]["display_time_utc"] == "2026-08-27"
    reg = correction["registration_statement_disambiguation"]
    assert reg["eloc_file_number"] == "333-299620"
    assert reg["public_warrant_file_number"] == "333-294417"
    assert reg["public_warrant_effective_date"] == "2026-08-27"
    assert reg["eloc_effect_notice_date_independently_located"] is False


def test_public_warrants_were_not_exercisable_on_november_6():
    row = load(CORRECTION)["public_warrants_correction"]
    assert row["warrant_count"] == 11_499_992
    assert row["exercise_price_usd"] == 11.5
    assert row["business_combination_closing_date"] == "2026-10-09"
    assert row["earliest_exercise_date_approx"] == "2027-10-09"
    assert row["exercisable_as_of_2026_11_06"] is False
    assert row["actual_exercises_verified"] is False


def test_in_kind_xrp_components_reconcile_to_reported_total():
    row = load(CORRECTION)["in_kind_contribution_reconciliation"]
    components = row["components_xrp"]
    assert sum(components.values()) == 388_910_554.061435
    assert row["total_xrp_reported_rounded"] == 388_910_554
    assert row["pubco_xrp_subtotal"] == 261_919_096
    assert components["ripple_contribution"] == 126_791_458
    assert components["delayed_funding_subscribers"] == 200_000


def test_corrected_normalized_excerpt_hashes_match():
    correction = load(CORRECTION)
    for key in ("warrant_prospectus", "registration_disambiguation", "in_kind_breakdown"):
        source = correction["source_overrides"][key]
        digest = hashlib.sha256(source["normalized_excerpt"].encode("utf-8")).hexdigest()
        assert digest == source["normalized_excerpt_sha256"]


def test_correction_does_not_enable_forecasting_or_real_money_actions():
    correction = load(CORRECTION)
    assert correction["model_eligibility"]["eligible"] is False
    assert correction["forecast_status"]["status"] == "NOT_ISSUED"
    assert correction["safety"]["no_paper_trade"] is True
    assert correction["safety"]["no_real_money_action"] is True
