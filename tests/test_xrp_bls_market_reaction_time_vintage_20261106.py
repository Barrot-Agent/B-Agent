from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORRECTION = ROOT / "research" / "xrp_intelligence" / "20261106T140000Z-bls-market-reaction-time-vintage-correction.json"
CANONICAL = ROOT / "research" / "xrp_intelligence" / "20261106T134313Z-bls-october-employment-and-xrp-post-release-market-reconciliation.json"


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\\0".encode("ascii") + payload).hexdigest()


def test_market_reaction_vintages_are_preserved_not_averaged() -> None:
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    canonical = json.loads(CANONICAL.read_text(encoding="utf-8"))
    assert _git_blob_sha(CANONICAL) == correction["canonical_event_artifact"]["git_blob_sha1"]
    assert canonical["macro"]["actual"]["nonfarm_payroll_change"] == 165000
    assert canonical["macro"]["actual"]["unemployment_rate_pct"] == 4.1

    timeline = {item["source_id"]: item for item in correction["market_reaction_timeline"]}
    reuters = timeline["reuters_market_reaction_1349z"]
    marketwatch = timeline["marketwatch_factset_last_check"]
    ft = timeline["ft_initial_market_reaction"]
    assert reuters["published_at_utc"] == "2026-11-06T13:49:00Z"
    assert reuters["reported"]["two_year_treasury_yield_pct"] == 4.52
    assert reuters["reported"]["two_year_change_basis_points"] == 5
    assert reuters["reported"]["implied_december_fed_hike_probability_pct"] == 78
    assert reuters["reported"]["prior_implied_december_fed_hike_probability_pct"] == 70
    assert "before pulling back" in reuters["reported_path"]
    assert marketwatch["reported"]["two_year_treasury_yield_pct"] == 4.51
    assert marketwatch["measurement_timestamp_utc"] is None
    assert ft["reported"]["two_year_treasury_yield_pct"] == 4.53
    assert correction["time_vintage_reconciliation"]["no_averaging"] is True
    assert correction["time_vintage_reconciliation"]["observations_are_not_identical_ticks"] is True


def test_real_wage_context_and_positive_equity_futures_are_counterevidence() -> None:
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    reuters = next(x for x in correction["market_reaction_timeline"] if x["source_id"] == "reuters_market_reaction_1349z")
    guardian = next(x for x in correction["market_reaction_timeline"] if x["source_id"] == "guardian_real_wage_and_geopolitical_context")
    assert reuters["reported"]["nasdaq_futures_change_pct"] == 1.4
    assert reuters["reported"]["sp500_futures_change_pct"] == 0.3
    assert guardian["reported"]["nominal_hourly_earnings_yoy_pct"] == 3.1
    assert guardian["reported"]["september_cpi_yoy_pct"] == 3.7
    assert guardian["reported"]["real_wage_growth_gap_percentage_points"] == -0.6
    assert correction["cross_asset_interpretation"]["conclusion"].startswith("The macro impulse is mixed")


def test_no_xrp_event_join_or_directional_forecast_is_claimed() -> None:
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    canonical = json.loads(CANONICAL.read_text(encoding="utf-8"))
    assert correction["xrp_alignment"]["canonical_kraken_provider_event_timestamp_utc"] is None
    assert correction["xrp_alignment"]["provider_timestamped_xrp_response_after_reuters_publication_available"] is False
    assert correction["xrp_alignment"]["event_return_computable"] is False
    assert correction["model_admission"]["eligible_for_feature_store"] is False
    assert correction["forecast_status"] == "NOT_ISSUED"
    assert canonical["forecast_status"]["status"] == "NOT_ISSUED"
