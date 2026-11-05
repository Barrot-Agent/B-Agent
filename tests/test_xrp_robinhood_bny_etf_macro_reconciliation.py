import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105T083300Z-xrp-robinhood-bny-etf-macro-reconciliation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def utc(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None
    return parsed.astimezone(timezone.utc)


def test_artifact_provenance_cutoff_and_model_quarantine():
    data = load()
    assert data["artifact_type"] == "xrp_institutional_rails_etf_issuer_vintage_and_macro_event_reconciliation"
    assert utc(data["captured_at_utc"]) == utc(data["data_cutoff_utc"])
    ids = [item["id"] for item in data["source_registry"]]
    assert len(ids) == len(set(ids))
    assert all(item["raw_content_sha256"] is None for item in data["source_registry"])
    assert all(item["model_eligible"] is False for item in data["source_registry"])
    assert data["data_quality"]["raw_source_bytes_captured"] is False
    assert data["data_quality"]["independent_timestamp_anchor"] is False
    known = set(ids)
    for observation in data["institutional_relationships"]["observations"]:
        assert set(observation["evidence"]) <= known
    for edge in data["institutional_relationships"]["relationship_graph"]:
        assert set(edge["evidence"]) <= known
    assert data["predictions"]["issued"] is False


def test_kraken_ticker_arithmetic_is_exact_and_depth_is_not_inferred():
    spot = load()["market_snapshot"]["spot"]
    mid = (spot["best_bid_usd"] + spot["best_ask_usd"]) / 2
    spread = (spot["best_ask_usd"] - spot["best_bid_usd"]) / mid * 10000
    assert math.isclose(spot["mid_usd"], mid, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(spot["displayed_spread_bps"], spread, rel_tol=0, abs_tol=1e-12)
    assert spot["low_24h_usd"] <= spot["last_usd"] <= spot["high_24h_usd"]
    assert load()["market_snapshot"]["order_book"]["full_depth_status"] == "NOT_CAPTURED"


def test_etf_trackers_preserve_same_date_disagreement_and_fund_universe():
    data = load()["market_snapshot"]["etf_flow_vintage"]
    assert data["alpha_finance"]["latest_complete_session"] == "2026-11-03"
    assert data["alpha_finance"]["november_3_net_flow_usd"] == 0
    assert data["xrp_insights"]["november_3_net_flow_xrp"] == -162050
    assert data["bykaranteli"]["net_flow_usd"] == 0
    assert data["crypto_news"]["november_2_net_flow_usd"] == -529510
    assert data["disagreement"]["no_averaging"] is True
    assert "different" in data["disagreement"]["explanation"]


def test_issuer_holdings_are_not_summed_across_stale_vintages():
    data = load()["market_snapshot"]["issuer_holdings_vintage"]
    assert data["bitwise"]["data_as_of_date"] == "2026-11-01"
    assert data["grayscale_gxrp"]["data_as_of_date"] == "2026-10-22"
    assert data["rex_xrpr"]["data_as_of_date"] == "2026-10-01"
    assert data["franklin_xrpz"]["data_as_of_date"] == "2026-09-04"
    assert data["synchronization_status"] == "NOT_SYNCHRONIZED"
    assert "Do not sum" in data["do_not_sum_rule"]
    assert data["rex_xrpr"]["coinshares_physical_xrp_units"] > 0


def test_custody_and_distribution_are_not_mislabeled_as_xrp_capital():
    data = load()
    observations = {item["id"]: item for item in data["institutional_relationships"]["observations"]}
    assert "no XRP-specific assets under custody" in " ".join(observations["BNY_RIPPLE_CUSTODY"]["limitation"].lower().split())
    assert "future" in observations["COINBASE_RLUSD"]["classification"]
    assert data["actual_capital_policy"]["current_unverified_items"]
    assert data["actual_capital_policy"]["rule"].startswith("Never convert")


def test_bls_employment_report_is_future_at_cutoff_and_direction_unknown():
    data = load()
    event = data["market_snapshot"]["macro_event"]
    assert event["status_at_cutoff"] == "FUTURE_SCHEDULED"
    assert utc(event["scheduled_at_utc"]) > utc(data["data_cutoff_utc"])
    assert event["directional_effect"] == "UNKNOWN_UNTIL_RELEASE_AND_MARKET_RESPONSE"
