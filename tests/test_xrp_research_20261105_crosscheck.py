import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T020359Z-xrp-derivatives-liquidity-amendment-crosscheck.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_rendered_sources_are_unreceipted_and_model_ineligible():
    data = load()
    assert data["forecast_issued"] is False
    assert data["prediction_status"] == "NOT_ISSUED"
    assert data["model_eligible"] is False
    assert all(source["raw_content_sha256"] is None for source in data["source_registry"])
    assert all(source["model_eligible"] is False for source in data["source_registry"])


def test_tradradar_snapshot_keeps_mark_price_oi_and_account_ratio_scoped():
    data = load()["derivatives_reconciliation"]
    assert data["as_of_utc"] == "2026-11-04T21:20:00Z"
    assert data["mark_price_usd"] == 1.3045
    assert data["open_interest_usd"] == 2_040_000_000
    assert data["open_interest_change_24h_pct"] == 1.26
    assert data["oi_weighted_funding_pct_per_8h"] == 0.0086
    assert data["liquidations_24h_lower_bound_usd"] == 8_050_000
    assert data["long_short_account_ratio"] == 3.20
    assert data["long_accounts_pct"] == 76.2
    assert data["model_eligible"] is False
    assert "not a spot execution price" in " ".join(data["limitations"])
    assert "not notional exposure" in " ".join(data["limitations"])


def test_liquidity_sources_are_not_synchronized_or_comparable():
    data = load()["liquidity_reconciliation"]
    assert data["historical_cex_study"]["updated_at"] == "2026-09-30"
    assert data["historical_cex_study"]["exchanges"] == 8
    assert data["historical_cex_study"]["bid_depth_usd_approx"] == 18_000_000
    assert data["historical_cex_study"]["ask_depth_usd_approx"] == 14_000_000
    assert data["single_venue_perpetual_snapshot"]["as_of_utc"] == "2026-11-04T07:18:00Z"
    assert data["single_venue_perpetual_snapshot"]["instrument"] == "XRPUSDT perpetual"
    assert "Do not sum" in data["no_aggregation_rule"]


def test_fix_cleanup_activation_does_not_imply_lending_launch_or_collateral_use():
    data = load()["xrpl_amendment_state"]
    assert data["prior_fix_activation"]["ledger_index"] == 108112129
    assert data["prior_fix_activation"]["enabled_at_utc"] == "2026-11-04T14:52:00Z"
    assert data["pending_amendments"]["LendingProtocol"] == 19
    assert data["pending_amendments"]["SingleAssetVault"] == 21
    assert data["yes_votes_required"] == 29
    assert "not a lending launch" in data["interpretation"]
    assert "more than 80%" in data["governance_method"]["official_rule"]


def test_validator_denominator_scope_disagreement_is_preserved():
    data = load()["xrpl_amendment_state"]["governance_method"]
    assert "35 of 35 validators heard" in data["secondary_denominator_disagreement"]
    assert "36 trusted validators" in data["secondary_denominator_disagreement"]
    assert "29" in data["secondary_denominator_disagreement"]


def test_competing_hypotheses_retain_counterevidence_and_no_forecast():
    data = load()
    assert len(data["competing_hypotheses"]) == 3
    assert all(item["support"] for item in data["competing_hypotheses"])
    assert all(item["disconfirming_or_missing"] for item in data["competing_hypotheses"])
    assert data["predictions"]["issued"] is False
