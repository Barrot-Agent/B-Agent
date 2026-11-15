import hashlib
import json
from pathlib import Path


def test_soter_series_b_network_preserves_close_timing_and_source_disagreement():
    path = (
        Path(__file__).resolve().parents[1]
        / "research"
        / "xrp_intelligence"
        / "20261107T030853Z-soter-series-b-sbi-coinbase-institutional-network.json"
    )
    artifact = json.loads(path.read_text(encoding="utf-8"))

    for source_name in ("primary_source", "secondary_source"):
        source = artifact[source_name]
        assert hashlib.sha256(
            source["normalized_excerpt"].encode("utf-8")
        ).hexdigest() == source["normalized_excerpt_sha256"]

    primary = artifact["primary_source"]["primary_disclosures"]
    assert primary["second_close_investors"] == ["SC Ventures", "SBI Group"]
    assert primary["second_close_follow_on_investor"] == "Token Bay Capital"
    assert primary["first_close_investors"] == [
        "Coinbase Ventures",
        "Franklin Templeton",
        "Brevan Howard Digital",
    ]
    assert primary["individual_investment_amounts_disclosed"] is False
    assert primary["total_round_size_disclosed"] is False

    secondary = artifact["secondary_source"]["secondary_claims"]
    assert secondary["headline_cash_amount_usd"] == 23_500_000
    assert secondary["body_cash_amount_usd"] == 23_000_000
    assert secondary["investor_level_allocation_disclosed"] is False

    interpretation = artifact["relationship_interpretation"]
    assert "different Series B closes" in interpretation["sbi_coinbase"]
    assert "not a direct SBI-Coinbase" in interpretation["sbi_coinbase"]
    assert "No XRP-specific" in interpretation["xrp"]
    assert artifact["model_admission"]["eligible"] is False
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["paper_trade_executed"] is False
    assert artifact["forecast"]["real_money_action"] is False
