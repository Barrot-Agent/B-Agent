import hashlib
import json
from pathlib import Path


def test_xrp_cross_provider_snapshot_preserves_disagreement_and_timestamp_limits():
    path = (
        Path(__file__).resolve().parents[1]
        / "research"
        / "xrp_intelligence"
        / "20261107T025842Z-xrp-spot-derivatives-cross-provider-snapshot.json"
    )
    artifact = json.loads(path.read_text(encoding="utf-8"))

    sources = {item["source_id"]: item for item in artifact["source_records"]}
    assert len(sources) == 4
    for source in sources.values():
        assert hashlib.sha256(
            source["normalized_excerpt"].encode("utf-8")
        ).hexdigest() == source["normalized_excerpt_sha256"]

    binance = artifact["spot_observations"]["binance_page"]
    coingecko = artifact["spot_observations"]["coingecko_page"]
    assert binance["price_usd"] == 1.1730575
    assert binance["change_24h_pct"] == -3.67
    assert coingecko["price_usd_rounded"] == 1.17
    assert coingecko["change_24h_pct"] == -4.2
    assert artifact["spot_provider_disagreement"]["change_24h_difference_percentage_points"] == 0.53
    assert artifact["spot_provider_disagreement"]["treatment"].startswith("Preserve provider values")

    derivatives = artifact["derivatives"]
    assert len(derivatives["venue_rows"]) == 10
    assert sum(row["open_interest_usd"] for row in derivatives["venue_rows"]) == 2_420_962_182
    assert derivatives["provider_timestamp"] is None
    assert derivatives["funding_interval"] == "NOT_SPECIFIED_IN_RENDERED_TABLE"
    assert derivatives["positive_funding_rows"] == 9
    assert derivatives["zero_or_rounded_zero_funding_rows"] == 1

    event = artifact["event_context"]
    assert event["reported_xrp_transfer"] == 233_460_000
    assert event["treatment"].startswith("Potential exchange-flow attribution contamination")
    assert artifact["model_admission"]["eligible"] is False
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["paper_trade_executed"] is False
    assert artifact["forecast"]["real_money_action"] is False
