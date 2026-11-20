import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T052215Z-binance-security-incident-xrp-flow-and-withdrawal-recovery.json"
)


def test_official_exchange_government_and_onchain_sources_are_separate():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    sources = {item["id"]: item for item in data["source_registry"]}
    groups = {
        sources["BINANCE_SECURITY_INCIDENT_INITIAL_20261030"]["independence_group"],
        sources["FBI_TRADERTRAITOR_ADVISORY_20261031"]["independence_group"],
        sources["WHALE_ALERT_INITIAL_XRP_TRANSFER_20261029"]["independence_group"],
    }
    assert len(groups) == 3


def test_secondary_wallet_attribution_is_not_independent_confirmation():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    sources = {item["id"]: item for item in data["source_registry"]}
    assert (
        sources["CRYPTO_BASIC_BINANCE_XRP_TRANSFER_REPORT_20261102"]["independence_group"]
        == "secondary_reporting_whale_alert_based"
    )
    assert (
        sources["UTODAY_BINANCE_XRP_WALLET_INTERPRETATION_20261105"]["independence_group"]
        == "secondary_reporting_whale_alert_and_explorer_labels"
    )
    assert data["xrp_flow_analysis"]["recipient_attribution_status"] == "UNRESOLVED"
