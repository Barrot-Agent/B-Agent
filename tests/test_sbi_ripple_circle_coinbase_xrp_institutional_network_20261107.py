import hashlib
import json
from pathlib import Path


def test_sbi_ripple_circle_coinbase_network_preserves_asset_and_relationship_boundaries():
    path = (
        Path(__file__).resolve().parents[1]
        / "research"
        / "xrp_intelligence"
        / "20261107T031930Z-sbi-ripple-circle-coinbase-xrp-institutional-network.json"
    )
    artifact = json.loads(path.read_text(encoding="utf-8"))

    assert len(artifact["source_records"]) >= 20
    for source in artifact["source_records"]:
        assert hashlib.sha256(
            source["normalized_excerpt"].encode("utf-8")
        ).hexdigest() == source["normalized_excerpt_sha256"]

    edges = artifact["network_edges"]
    assert any(
        edge["from"] == "SBI Remit"
        and edge["to"] == "XRP"
        and edge["type"] == "production_bridge_currency_use"
        for edge in edges
    )
    assert any(
        edge["from"] == "SBI Ripple Asia"
        and edge["to"] == "XRPL"
        and edge["type"] == "tokenized_deposit_proof_of_concept"
        for edge in edges
    )
    assert any(
        edge["from"] == "Circle"
        and edge["to"] == "XRPL"
        and edge["type"] == "native_stablecoin_ledger_integration"
        for edge in edges
    )
    assert any(
        edge["from"] == "Circle"
        and edge["to"] == "Coinbase"
        and edge["type"] == "USDC_distribution_and_revenue_sharing"
        for edge in edges
    )

    distinctions = artifact["asset_and_ledger_distinctions"]
    assert "without using XRP as the bridge asset" in distinctions["XRPL"]
    assert "no bridge required" in distinctions["USDC"]
    assert "SBI Remit uses it as a bridge currency" in distinctions["XRP"]

    metrics = artifact["balance_sheet_and_distribution_metrics"]
    assert metrics["circle_q3_2026_coinbase_related_distribution_costs_usd"] == 331_300_000
    assert metrics["circle_2026_nine_month_coinbase_related_distribution_costs_usd"] == 986_600_000
    assert "not total customer USDC balances" in metrics["metric_caveats"][1]

    interpretation = artifact["relationship_interpretation"]
    assert "not a direct partnership" in interpretation["coinbase_ripple"]
    assert "not a direct Circle-Ripple corporate partnership" in interpretation["circle_ripple"]
    assert "multi-rail and multi-chain" in interpretation["sbi_strategy"]

    assert artifact["model_admission"]["eligible_as_event_timeline"] is True
    assert artifact["model_admission"]["eligible_as_numeric_price_feature"] is False
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["paper_trade_executed"] is False
    assert artifact["forecast"]["real_money_action"] is False
