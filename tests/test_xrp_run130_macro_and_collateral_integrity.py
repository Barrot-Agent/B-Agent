from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEL = ROOT / "research" / "xrp_intelligence"
CPI = INTEL / "20261110T133108Z-run130b-october-cpi-release-and-market-reaction.json"
REAL_EARNINGS = INTEL / "20261110T133404Z-run130c-real-earnings-release.json"
COLLATERAL = INTEL / "20261110T132100Z-run130e-cbxrp-morpho-market-and-oracle-reconciliation.json"
HASH_CORRECTION = INTEL / "20261110T134556Z-run130f-normalized-hash-corrections.json"
SBIC = INTEL / "20261110T134556Z-run130f-japan-sbic-primary-identity-chatgpt-seminar.json"
SBIC_HASH_CORRECTION = INTEL / "20261110T135238Z-run130g-sbic-normalized-hash-correction.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized_digest(data: dict, field: str = "normalized_evidence_sha256") -> str:
    normalized = dict(data)
    normalized.pop(field)
    canonical = json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_run130b_cpi_keeps_unavailable_year_over_year_values_null():
    data = _load(CPI)
    event = data["macro_event"]
    assert event["release_id"] == "USDL-26-1685"
    assert event["headline_cpi_mom_sa_pct"] == 0.4
    assert event["core_cpi_mom_sa_pct"] == 0.3
    assert event["year_over_year"]["headline_pct"] is None
    assert event["year_over_year"]["core_pct"] is None
    assert data["model_admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["market_observations"]["conclusion"].startswith(
        "No synchronized post-release multi-venue snapshot"
    )


def test_run130c_real_earnings_preserves_nulls_and_provenance():
    data = _load(REAL_EARNINGS)
    results = data["release"]["results"]
    assert data["release"]["release_id"] == "USDL-26-1686"
    assert results["all_employees"]["real_average_hourly_earnings_mom_sa_pct"] == 0
    assert results["all_employees"]["real_average_weekly_earnings_mom_sa_pct"] == 0
    assert results["production_nonsupervisory"]["real_average_hourly_earnings_mom_sa_pct"] == 0.1
    assert results["production_nonsupervisory"]["real_average_weekly_earnings_mom_sa_pct"] == -0.3
    assert results["year_over_year"]["all_employees_real_earnings_pct"] is None
    assert results["year_over_year"]["production_nonsupervisory_real_earnings_pct"] is None
    assert data["provenance"]["raw_http_wire_bytes_captured"] is False
    assert data["model_admission"]["status"] == "NOT_ADMITTED"
    assert data["forecast_status"] == "NOT_ISSUED"


def test_run130f_append_only_receipt_corrects_both_normalized_hashes():
    correction = _load(HASH_CORRECTION)
    assert correction["status"] == "CORRECTED_BY_APPEND_ONLY_RECEIPT"
    assert correction["preservation"]["original_artifacts_mutated"] is False
    assert correction["preservation"]["corrections_append_only"] is True
    assert len(correction["corrections"]) == 2
    for item in correction["corrections"]:
        source = _load(ROOT / item["artifact_path"])
        recorded = source["normalized_evidence_sha256"]
        recomputed = _normalized_digest(source)
        assert recorded == item["original_recorded_normalized_sha256"]
        assert recomputed == item["recomputed_normalized_sha256"]
        assert recomputed != recorded


def test_run130e_cbXRP_market_identity_and_liquidation_math():
    data = _load(COLLATERAL)
    market = data["market_identity"]
    assert market["network"] == "Base"
    assert market["market_id"] == (
        "0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109"
    )
    assert len(market["market_id"]) == 66
    assert market["collateral_contract"] == "0xcb585250f852c6c6bf90434ab21a00f02833a4af"
    assert market["lltv_pct"] == 62.5
    assert market["lltv_immutable"] is True
    lif = min(1.15, 1 / (0.3 * 0.625 + 0.7))
    assert math.isclose(lif, 1.1267605634, rel_tol=0, abs_tol=1e-9)
    assert math.isclose((lif - 1) * 100, 12.67605634, rel_tol=0, abs_tol=1e-7)
    assert data["model_admission"]["status"] == "NOT_ADMITTED"
    assert data["forecast_status"] == "NOT_ISSUED"


def test_run130e_oracle_timestamp_mismatch_stays_quarantined():
    data = _load(COLLATERAL)
    market = data["market_identity"]
    assert market["feed_heartbeat"] == "1 day"
    assert market["feed_deviation_pct"] == 0.5
    assert market["feed_latest_price_timestamp_utc"] is None
    assert market["oracle_comparison"].startswith("QUARANTINED")
    disagreements = data["cross_interface_disagreements"]
    assert any(item["metric"] == "oracle_price" for item in disagreements)
    assert any(item["metric"] == "liquidity" for item in disagreements)


def test_run130e_credit_and_liquidation_values_are_not_mislabeled_as_xrp_spot_flows():
    data = _load(COLLATERAL)
    non_equivalences = data["evidence_classification"]["non_equivalences"]
    assert "Outstanding USDC debt is not proof of XRP purchases or net capital entering XRP." in non_equivalences
    assert "Base cbXRP collateral is not native XRPL lending." in non_equivalences
    assert "Liquidation count/debt repaid are not XRP sold." in non_equivalences
    assert data["morphowatch_snapshot"]["borrowed_usdc_usd"] == 55_520_000
    assert data["morphowatch_snapshot"]["collateral_cbxrp"] == 120_450_000


def test_run130f_sbic_east_central_west_are_distinct_regional_companies():
    data = _load(SBIC)
    entities = data["entities"]
    assert entities["east"]["official_abbreviation"] == "SBIC East Japan"
    assert entities["central"]["official_abbreviation"] == "SBIC Central Japan"
    assert entities["west"]["official_abbreviation"] == "SBIC West Japan"
    assert entities["east"]["legal_name_en"] != entities["central"]["legal_name_en"]
    assert entities["central"]["legal_name_en"] != entities["west"]["legal_name_en"]
    assert "Small and Medium Business Investment & Consultation" in entities["east"]["legal_name_en"]
    assert data["identity_conclusion"]["not_sbi_holdings"].startswith("These are distinct legal entities")
    assert data["identity_conclusion"]["shareholder_limitation"].startswith("SBIC East's public profile lists shareholder categories")


def test_run130f_chatgpt_reference_is_an_educational_seminar_not_openai_partnership():
    data = _load(SBIC)
    event = data["chatgpt_event"]
    assert event["date"] == "2026-03-05"
    assert event["organizer"].endswith("(SBIC East Japan)")
    assert event["co_host"] == "Hamamatsu Iwata Shinkin"
    assert event["speaker_affiliation"] == "Microsoft Japan, executive officer and evangelist"
    assert event["commercial_openai_relationship_evidenced"] is False
    assert data["identity_conclusion"]["xrp_relationship"].startswith("No direct XRP")
    assert data["forecast_status"] == "NOT_APPLICABLE"


def test_run130g_sbic_hash_correction_matches_committed_json():
    data = _load(SBIC)
    correction = _load(SBIC_HASH_CORRECTION)
    item = correction["correction"]
    recorded = data["normalized_evidence_sha256"]
    recomputed = _normalized_digest(data)
    assert correction["status"] == "CORRECTED_BY_APPEND_ONLY_RECEIPT"
    assert correction["preservation"]["original_artifact_mutated"] is False
    assert item["original_recorded_normalized_sha256"] == recorded
    assert item["recomputed_normalized_sha256"] == recomputed
    assert recomputed != recorded
