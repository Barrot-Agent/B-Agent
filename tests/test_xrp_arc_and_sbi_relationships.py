from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "data/xrp_intelligence/snapshots/20261101T221819Z-arc-activity-and-sbi-cross-rail.json"

def load():
    return json.loads(SNAP.read_text(encoding="utf-8"))

def test_arc_chain_metrics_are_separate_from_global_agent_stack_metric():
    d = load()
    assert d["arc"]["defiLlama"]["stablecoin_market_cap_usd"] == 1_097_000_000
    assert d["arc"]["agentgdp_x402"]["coverage"] == "PARTIAL_AND_BACKFILLING"
    assert d["arc"]["reconciliation"]["status"] == "MULTIPLE_MARKET_SEGMENTS; NO_SINGLE_ADOPTION_METRIC"

def test_arc_bitquery_window_is_historical_and_filtered_counts_are_proxies():
    d = load()["arc"]["bitquery_first_month"]
    assert d["window_end"] == "2026-10-14"
    assert d["decline_from_launch_pct"] == 94
    assert d["morpho_cirbtc_market"]["utilization_pct"] == 97
    assert d["morpho_cirbtc_market"]["borrowed_usdc_bridged_out_by_five_borrowers_usd"] == 142_000_000

def test_sbi_has_separate_ripple_and_circle_capital_relationships():
    d = load()["sbi_group"]
    assert d["ripple_equity"]["reported_share_pct"] == 9
    assert d["ripple_equity"]["not_xrp_tokens"] is True
    assert d["circle_equity"]["total_usd"] == 50_000_000
    assert d["arc_token_presale"]["sbi_specific_amount_usd"] is None

def test_sbi_rlusd_relationship_is_only_an_mou():
    assert load()["sbi_group"]["rlusd_japan"]["status"] == "MOU_NOT_PROOF_OF_LIVE_DISTRIBUTION"

def test_sbi_and_sbi_group_are_not_conflated_with_sbic():
    d = load()["sbi_group"]["sbic_distinction"]
    assert d["same_as_SBI_Holdings"] is False
    assert d["direct_xrp_or_circle_relationship"] == "NOT_ESTABLISHED"
