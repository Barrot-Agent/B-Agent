import hashlib
import json
from pathlib import Path


def test_kraken_direct_ticker_preserves_daily_open_and_rolling_24h_fields():
    path = (
        Path(__file__).resolve().parents[1]
        / "research"
        / "xrp_intelligence"
        / "20261107T030448Z-xrp-kraken-direct-spot-ticker.json"
    )
    artifact = json.loads(path.read_text(encoding="utf-8"))
    source = artifact["source"]
    assert hashlib.sha256(
        source["exact_response_representation"].encode("utf-8")
    ).hexdigest() == source["exact_response_representation_sha256"]

    observed = artifact["observation"]
    assert artifact["instrument"] == "XXRPZUSD"
    assert observed["last_usd"] == 1.16702
    assert observed["best_bid_usd"] == 1.16701
    assert observed["best_ask_usd"] == 1.16702
    assert observed["volume_24h_xrp"] == 28_038_383.03545056
    assert observed["vwap_24h_usd"] == 1.18564059
    assert observed["utc_daily_open_usd"] == 1.17749
    assert artifact["field_semantics"]["ticker_field_o"].startswith("UTC daily open")
    assert "not a rolling 24-hour open" in artifact["field_semantics"]["ticker_field_o"]
    assert artifact["model_admission"]["eligible"] is False
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["paper_trade_executed"] is False
    assert artifact["forecast"]["real_money_action"] is False
