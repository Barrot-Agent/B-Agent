from pathlib import Path

from barrot_agent.evolution.xrp_public_ingestion import ENDPOINTS, SCHEDULED_ENDPOINTS


def test_forecast_ledger_contract_endpoint_counts_match_collector():
    contract_path = (
        Path(__file__).resolve().parents[1]
        / "research"
        / "xrp_intelligence"
        / "forecast-ledger-contract.md"
    )
    contract = contract_path.read_text(encoding="utf-8")

    assert len(ENDPOINTS) == 32
    assert len(SCHEDULED_ENDPOINTS) == 30
    assert contract.count("32 public endpoint records") == 2
    assert "23 public endpoint records" not in contract
