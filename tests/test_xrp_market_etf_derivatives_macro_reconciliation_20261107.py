import hashlib
import json
from pathlib import Path


def test_xrp_market_etf_derivatives_macro_reconciliation_preserves_provenance_and_uncertainty():
    artifact_path = (
        Path(__file__).resolve().parents[1]
        / "research"
        / "xrp_intelligence"
        / "20261107T023600Z-xrp-market-etf-derivatives-macro-reconciliation.json"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["artifact_type"] == "xrp_market_etf_derivatives_macro_reconciliation"
    assert artifact["captured_at_utc"] == artifact["data_cutoff_utc"]
    assert artifact["model_admission"]["eligible"] is False
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["paper_trade_executed"] is False
    assert artifact["forecast"]["real_money_action"] is False

    kraken = artifact["market_observations"]["kraken_xrp_usd"]
    assert kraken["provider_timestamp_utc"] is None
    assert kraken["utc_day_open_usd"] == 1.17749
    assert "open_24h_usd" not in kraken
    assert abs(kraken["level1_spread_bps"] - 0.0849758456) < 1e-9

    derivatives = artifact["market_observations"]["derivatives"]
    assert derivatives["reconciliation"]["open_interest_difference_usd"] == 870_000_000
    assert derivatives["reconciliation"]["do_not_average"] is True
    assert derivatives["tradradar"]["open_interest_usd"] == 1_910_000_000
    assert derivatives["alpha_finance"]["open_interest_usd"] == 2_780_000_000
    assert derivatives["reconciliation"]["status"] == "UNRECONCILED_PROVIDER_UNIVERSES"

    etf = artifact["market_observations"]["etf_flows"]
    assert etf["xrp_insights"]["nov5_2026_flow_xrp"] == 110_214
    assert etf["cryptokeyhole"]["nov5_2026_flow_xrp"] == -3_339
    assert etf["cross_provider"]["nov5_flow_difference_xrp"] == 113_553
    assert etf["cross_provider"]["nov2_to_nov5_flow_difference_xrp"] == -136_131
    assert etf["cryptokeyhole"]["header_vs_table_rounding_difference_xrp"] == 1
    assert etf["cross_provider"]["do_not_average"] is True

    sources = artifact["provenance"]["sources"]
    assert len({item["source_id"] for item in sources}) == len(sources)
    for source in sources:
        if "raw_response_text" in source:
            assert hashlib.sha256(source["raw_response_text"].encode("utf-8")).hexdigest() == source["raw_response_text_sha256"]
        if "excerpt_text" in source:
            assert hashlib.sha256(source["excerpt_text"].encode("utf-8")).hexdigest() == source["excerpt_sha256"]
            assert source["raw_page_body_retained"] is False

    independence = " ".join(artifact["provenance"]["source_independence"]).lower()
    assert "not independent underlying economic data" in independence
    assert any("no full depth ladder" in item.lower() for item in artifact["limitations"])
