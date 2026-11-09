from pathlib import Path

from barrot_agent.evolution.xrp_public_ingestion import (
    ENDPOINTS,
    NONCOMMERCIAL_XRPL_NODE_SOURCE_IDS,
    SCHEDULED_ENDPOINTS,
    WEEKLY_ENDPOINTS,
)


def test_forecast_contract_endpoint_counts_match_collector_inventory():
    root = Path(__file__).resolve().parents[1]
    contract = (root / "research/xrp_intelligence/forecast-ledger-contract.md").read_text(encoding="utf-8")

    assert len(ENDPOINTS) == 39
    assert len(NONCOMMERCIAL_XRPL_NODE_SOURCE_IDS) == 2
    assert len(SCHEDULED_ENDPOINTS) == 36
    assert len(WEEKLY_ENDPOINTS) == 1
    assert len(SCHEDULED_ENDPOINTS) + len(WEEKLY_ENDPOINTS) == len(ENDPOINTS) - len(NONCOMMERCIAL_XRPL_NODE_SOURCE_IDS)
    assert "39 public endpoint records (36 hourly, one weekly CFTC TFF raw-only; two free non-commercial XRPL nodes excluded)" in contract
    assert "39 public endpoint records, 36 hourly plus 1 weekly after excluding two non-commercial XRPL public-node endpoints" in contract
    assert "38 public endpoint records" not in contract
