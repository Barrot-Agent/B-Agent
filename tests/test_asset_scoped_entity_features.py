from scripts.entity_cooccurrence import build_cooccurrence
from scripts.entity_sentiment_profile import build_entity_sentiment_profile


def entry(title, sentiment, entities, **relevance):
    distill = {"sentiment": sentiment, "entities": entities}
    distill.update(relevance)
    return {"title": title, "distilled": True, "distill": distill}


def pair_set(rows):
    return {tuple(sorted((row["entity_a"], row["entity_b"]))) for row in rows}


def test_entity_features_keep_target_asset_scope_and_relevance_weights():
    xrp_entries = [
        entry("Ripple XRP custody update", "bullish", ["Ripple", "XRP"], xrp_relevance=1.0),
        entry("Bitcoin ETF headline", "bearish", ["Bitcoin", "XRP"], xrp_relevance=0.2),
        entry("Unweighted BTC headline", "bullish", ["Bitcoin", "BTC"], xrp_relevance=0.0),
    ]
    btc_entries = [
        entry("Bitcoin network update", "bullish", ["Bitcoin", "BTC"], btc_relevance=1.0),
    ]

    cooccurrence = build_cooccurrence(xrp_entries, btc_entries)
    assert ("BTC", "Bitcoin") in pair_set(cooccurrence["pairs"])
    assert ("Bitcoin", "XRP") in pair_set(cooccurrence["pairs_by_asset"]["XRP"])
    assert ("BTC", "Bitcoin") not in pair_set(cooccurrence["pairs_by_asset"]["XRP"])
    assert ("BTC", "Bitcoin") in pair_set(cooccurrence["pairs_by_asset"]["BTC"])
    xrp_pair = next(row for row in cooccurrence["pairs_by_asset"]["XRP"] if (row["entity_a"], row["entity_b"]) == ("Bitcoin", "XRP"))
    assert xrp_pair["relevance_weight_sum"] == 0.2
    assert xrp_pair["example_headlines"][0]["pipeline_asset"] == "XRP"

    profiles = build_entity_sentiment_profile(xrp_entries, btc_entries)
    # Legacy global profile remains available for descriptive cross-market analysis.
    assert any(row["entity"] == "Bitcoin" and row["total_mentions"] == 3 for row in profiles["entities"])
    xrp_bitcoin = next(row for row in profiles["asset_specific_profiles"]["XRP"] if row["entity"] == "Bitcoin")
    btc_bitcoin = next(row for row in profiles["asset_specific_profiles"]["BTC"] if row["entity"] == "Bitcoin")
    assert xrp_bitcoin["eligible_mentions"] == 1
    assert xrp_bitcoin["relevance_weight_sum"] == 0.2
    assert xrp_bitcoin["relevance_weighted_score_0_100"] == 0.0
    assert btc_bitcoin["eligible_mentions"] == 1
    assert btc_bitcoin["relevance_weighted_score_0_100"] == 100.0


def test_unweighted_or_invalid_relevance_is_not_admitted_to_asset_specific_profile():
    xrp_entries = [
        entry("No relevance", "bullish", ["Ripple", "XRP"], xrp_relevance=0),
        entry("Invalid relevance", "bearish", ["Ripple", "XRP"], xrp_relevance="not-a-number"),
    ]
    result = build_entity_sentiment_profile(xrp_entries, [])
    assert result["asset_specific_profiles"]["XRP"] == []
    cooccurrence = build_cooccurrence(xrp_entries, [])
    assert cooccurrence["pairs_by_asset"]["XRP"] == []
    assert cooccurrence["unique_pairs_found"] == 1  # Legacy descriptive aggregate is preserved.
