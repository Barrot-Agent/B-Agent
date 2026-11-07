import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T221027Z-xrp-market-etf-institutional-identity-reconciliation.json"
)
CORRECTION = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T221843Z-alpha-five-funds-excerpt-hash-correction.json"
)


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_raw_exchange_response_hashes_recompute_and_timestamp_gates_fail_closed():
    data = load()
    sources = {item["source_id"]: item for item in data["sources"]}
    for source_id in ("KRAKEN_XRPUSD_TICKER", "OKX_XRPUSDT_TICKER"):
        source = sources[source_id]
        assert hashlib.sha256(source["raw_response_body"].encode("utf-8")).hexdigest() == source["raw_response_sha256"]
        assert source["model_eligible"] is False
    assert sources["KRAKEN_XRPUSD_TICKER"]["provider_timestamp_utc"] is None
    assert sources["OKX_XRPUSDT_TICKER"]["provider_age_seconds_at_reference"] > 300


def test_visible_excerpt_hashes_are_exact_and_the_single_typo_is_append_only_corrected():
    data = load()
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    supersedes = correction["supersedes"]
    correction_used = 0
    for source in data["sources"]:
        excerpts = []
        if source.get("excerpt") is not None:
            excerpts.append((source["excerpt"], source["excerpt_sha256"]))
        excerpts.extend((item["text"], item["sha256"]) for item in source.get("excerpts", []))
        for text, expected in excerpts:
            actual = hashlib.sha256(text.encode("utf-8")).hexdigest()
            assert len(text.split()) <= data["source_capture_contract"]["maximum_direct_quote_words_per_source"]
            if actual == expected:
                continue
            assert source["source_id"] == supersedes["source_id"]
            assert text == supersedes["excerpt"]
            assert expected == supersedes["original_sha256"]
            assert actual == supersedes["corrected_sha256"]
            correction_used += 1
    assert correction_used == 1
    assert correction["append_only"] is True
    assert correction["raw_source_body_retrieved_again"] is False
    assert correction["model_eligible"] is False


def test_cross_venue_price_gap_is_not_promoted_to_arbitrage_or_model_feature():
    market = load()["market_snapshot"]
    assert market["kraken_xrp_usd"]["provider_timestamp_utc"] is None
    assert market["okx_xrp_usdt"]["provider_age_seconds"] > market["okx_xrp_usdt"]["freshness_threshold_seconds"]
    assert "NOT_COMPARABLE" in market["cross_venue_comparability"]
    assert market["direct_depth_status"].startswith("Kraken depth")
    assert market["kraken_xrp_usd"]["model_eligible"] is False
    assert market["okx_xrp_usdt"]["model_eligible"] is False


def test_swiftedge_microstructure_is_secondary_and_venue_coverage_unknown():
    data = load()
    swiftedge = next(x for x in data["sources"] if x["source_id"] == "SWIFTEDGE_MARKET_BRIEF")
    market = data["market_snapshot"]["swiftedge_secondary_snapshot"]
    assert swiftedge["source_venue_coverage"] == "UNDISCLOSED"
    assert market["net_taker_flow_pct"] == -18.8
    assert market["open_interest_change_24h_pct"] == -1.7
    assert market["large_order_net_usd"] == -9700000
    assert market["model_eligible"] is False


def test_etf_provider_disagreement_is_reconciled_by_universe_method_and_window_not_averaged():
    etf = load()["etf_flow_reconciliation"]
    alpha = etf["alpha_finance"]
    insights = etf["xrp_insights"]
    assert alpha["fund_count"] == 5
    assert "XRPR" in alpha["excludes"] and "BITW" in alpha["excludes"]
    assert alpha["flow_2026_11_06_usd"] == 0
    assert alpha["seven_session_flow_usd"] == 8400000
    assert insights["fund_universe"] == "six US spot funds plus BITW"
    assert insights["gxrp_flow_treatment"].startswith("excluded")
    assert insights["week_nov_2_to_6_flow_xrp"] == -812500
    assert "NOT_DIRECTLY_COMPARABLE" in etf["comparability"]
    assert "cannot be averaged" in etf["comparability"]


def test_issuer_holdings_and_onchain_claims_remain_secondary_not_primary_receipts():
    sources = {item["source_id"]: item for item in load()["sources"]}
    insights = sources["XRP_INSIGHTS_ETF_TRACKER"]
    assert insights["source_type"] == "secondary_issuer_holdings_aggregator"
    assert insights["model_eligible"] is False
    assert any("independent XRPL node/query receipts" in x for x in insights["limitations"])


def test_institutional_relationships_do_not_imply_barrot_auth_or_xrp_purchases():
    relationships = {item["id"]: item for item in load()["ecosystem_relationships"]}
    assert relationships["SBI_HOLDINGS_ANTHROPIC"]["barrot_authentication"] == "NOT_VERIFIED"
    assert relationships["SBI_STARTALE_OPEN_STANDARD"]["direct_sbi_coinbase_xrp_partnership"] == "NOT_ESTABLISHED"
    assert relationships["RIPPLE_BNY"]["disclosed_xrp_customer_balances"] is False
    assert relationships["RIPPLE_COINBASE_RLUSD"]["evidence_of_xrp_purchase"] is False


def test_kamilah_video_candidate_is_not_attributed_to_unverified_personal_channel():
    identity = load()["identity_update"]
    candidate = identity["new_candidate"]
    assert identity["person_identity_status"] == "CONFIRMED"
    assert identity["channel_identity_status"] == "PROBABLE_MATCH_NOT_FIRST_PARTY_VERIFIED"
    assert identity["verified_personal_channel_uploads"] == 0
    assert candidate["video_id"] == "bZ3aaY1RKCc"
    assert candidate["attribution_status"] == "CANDIDATE_ONLY_CANONICAL_CHANNEL_UNVERIFIED"
    assert candidate["profile_promoted"] is False
    assert candidate["full_content_reviewed"] is False


def test_exact_phrase_status_and_forecast_remain_fail_closed():
    data = load()
    assert "No new verified XRP relationship" in data["exact_phrase_research"]["ask_coin"]
    assert "No new issuer-primary" in data["exact_phrase_research"]["actual_capital"]
    assert "No OpenAI partnership" in data["exact_phrase_research"]["sbic_chatgpt_sbic"]
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["model_admission"]["eligible_sources"] == []
