from __future__ import annotations

import json
from pathlib import Path

from barrot_agent.evolution.xrp_public_ingestion import (
    DIGEST_ONLY_RAW_SOURCE_REASONS,
    ENDPOINTS,
    SCHEDULED_ENDPOINTS,
    WEEKLY_ENDPOINTS,
)


ROOT = Path(__file__).resolve().parents[1]


def test_feature_store_contract_endpoint_counts_match_registry() -> None:
    contract = (ROOT / "research" / "xrp_intelligence" / "feature-store-contract.md").read_text(
        encoding="utf-8"
    )
    assert len(ENDPOINTS) == 50
    assert len(SCHEDULED_ENDPOINTS) == 43
    assert len(WEEKLY_ENDPOINTS) == 3
    assert len(ENDPOINTS) == len(SCHEDULED_ENDPOINTS) + len(WEEKLY_ENDPOINTS) + 4
    assert "50 public endpoint records: 43 hourly scheduled sources, three weekly scheduled CFTC sources" in contract
    assert "Thus 46 sources are scheduled (43 hourly plus three weekly) and four endpoint definitions are excluded from scheduling: two Deribit raw-only endpoints and two XRPL public-node endpoints." in contract
    assert "40 endpoint records: 36 hourly scheduled sources" not in contract
    assert "two free non-commercial XRPL public-node endpoints excluded by default" in contract


def test_exchange_wallet_balance_source_is_scheduled_digest_only() -> None:
    all_sources = {source_id for source_id, _ in ENDPOINTS}
    scheduled_sources = {source_id for source_id, _ in SCHEDULED_ENDPOINTS}
    assert "xrp_exchange_balances_json" in all_sources
    assert "xrp_exchange_balances_json" in scheduled_sources
    assert "xrp_exchange_balances_json" in DIGEST_ONLY_RAW_SOURCE_REASONS
    assert "SHA-256 receipt only" in DIGEST_ONLY_RAW_SOURCE_REASONS["xrp_exchange_balances_json"]


def test_primary_mission_is_xrp_priority_one_on_barrot_v3() -> None:
    mission = json.loads(
        (ROOT / "barrot_agent" / "data" / "missions" / "primary_mission.json").read_text(
            encoding="utf-8"
        )
    )
    assert mission["mission_id"] == "xrp_intelligence_prediction_engine"
    assert mission["priority"] == 1
    assert mission["status"] == "active"
    assert mission["foundation"]["id"] == "barrot_v3"
    assert mission["foundation"]["preserve"] is True
    assert mission["foundation"]["responsibilities"] == [
        "execution",
        "orchestration",
        "safety",
        "verification",
    ]
