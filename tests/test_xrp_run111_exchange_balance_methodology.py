from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261110T022818Z-run111-xrp-market-flows-upbit-cpi-provenance.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_run111_exchange_balance_snapshot_preserves_coverage_and_same_wallet_methodology():
    artifact = load_artifact()
    balances = artifact["exchange_balance_methodology"]
    assert balances["snapshot_as_of_utc"] == "2026-11-09T08:01:00Z"
    assert balances["tracked_exchanges"] == 24
    assert balances["tracked_wallets"] == 701
    assert balances["attributed_balance_xrp"] == 22_350_000_000
    assert balances["same_wallet_change_7d_xrp"] == -25_800_000
    assert balances["same_wallet_change_30d_xrp"] == -138_100_000
    assert balances["same_wallet_change_1d_xrp"] == 9_700_000
    assert balances["naive_total_change_xrp"] == 373_900_000
    assert balances["newly_tracked_wallet_balance_xrp"] == 512_000_000
    assert balances["unclassified_pct"] == 40
    assert balances["wrapped_insurance_other_reserves_xrp"] == 483_000_000
    assert balances["model_admission"] is False


def test_run111_gross_binance_flows_are_not_netted_or_treated_as_independent():
    artifact = load_artifact()
    flows = artifact["exchange_flow_observations"]
    assert flows[0]["amount_xrp"] == 691_000_000
    assert flows[0]["direction"] == "gross_inflow"
    assert flows[1]["amount_xrp"] == 418_500_000
    assert flows[1]["direction"] == "gross_outflow"
    assert artifact["source_independence"]["cryptoquant_691m_and_418m"]["same_provider"] is True
    assert artifact["source_independence"]["cryptoquant_691m_and_418m"]["do_not_net"] is True


def test_run111_market_response_hashes_cover_surfaced_text_not_wire_bytes():
    artifact = load_artifact()
    market = artifact["market"]
    assert market["raw_http_bytes_preserved"] is False
    assert market["model_admission"] is False
    for name, body in market["raw_response_bodies"].items():
        assert hashlib.sha256(body.encode("utf-8")).hexdigest() == market["response_text_sha256"][name]
    assert market["comparison"]["asynchronous"] is True
    assert market["comparison"]["no_arbitrage_inference"] is True
    assert market["depth"]["l2_snapshot_captured"] is False


def test_run111_upbit_turnover_etf_scope_and_future_cpi_are_not_misclassified():
    artifact = load_artifact()
    assert artifact["upbit_turnover"]["volume_is_net_capital"] is False
    assert artifact["upbit_turnover"]["share_of_upbit_volume_pct"] == 17.0
    assert artifact["etf_flow_observation"]["reported_net_flow_nov3_to_nov6_usd"] == 0
    assert "secondary tracker report" in artifact["etf_flow_observation"]["source"]
    assert artifact["macro_event"]["released_at_capture"] is False
    assert artifact["macro_event"]["scheduled_at_utc"] == "2026-11-10T13:30:00Z"
    assert artifact["forecast_status"] == "NOT_ISSUED"
