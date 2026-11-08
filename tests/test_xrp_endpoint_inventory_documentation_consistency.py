from pathlib import Path

from barrot_agent.evolution.xrp_public_ingestion import (
    ENDPOINTS,
    NONCOMMERCIAL_XRPL_NODE_SOURCE_IDS,
    SCHEDULED_ENDPOINTS,
)


def test_forecast_contract_endpoint_counts_match_collector_inventory():
    root = Path(__file__).resolve().parents[1]
    contract = (root / "research/xrp_intelligence/forecast-ledger-contract.md").read_text(encoding="utf-8")

    assert len(ENDPOINTS) == 35
    assert len(NONCOMMERCIAL_XRPL_NODE_SOURCE_IDS) == 2
    assert len(SCHEDULED_ENDPOINTS) == 33
    assert len(SCHEDULED_ENDPOINTS) == len(ENDPOINTS) - len(NONCOMMERCIAL_XRPL_NODE_SOURCE_IDS)
    assert "35 public endpoint records (33 scheduled; two free non-commercial XRPL nodes excluded)" in contract
    assert "35 public endpoint records, 33 scheduled after excluding two non-commercial XRPL public-node endpoints" in contract
    assert "35 public endpoint records, 30 scheduled after excluding two non-commercial XRPL public-node endpoints" not in contract
