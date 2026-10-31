from datetime import datetime, timezone

from scripts.entity_cooccurrence import build_cooccurrence
from scripts.entity_sentiment_profile import build_profile


GENERATED_AT = datetime(2026, 10, 31, 11, 0, tzinfo=timezone.utc)


def test_entity_profile_labels_article_sentiment_and_all_time_scope():
    xrp_entries = [{
        "title": "XRP and SEC headline",
        "distill": {"sentiment": "bullish", "entities": ["XRP", "SEC"]},
    }]
    btc_entries = [{
        "title": "Bitcoin and XRP headline",
        "distill": {"sentiment": "bearish", "entities": ["XRP", "SEC"]},
    }]

    result = build_profile(xrp_entries, btc_entries, generated_at=GENERATED_AT)
    xrp = next(row for row in result["entities"] if row["entity"] == "XRP")

    assert result["generated_at_utc"] == "2026-10-31T11:00:00+00:00"
    assert result["time_scope"] == "ALL_AVAILABLE_LOG_ENTRIES"
    assert result["input_timestamp_filter"] == "NONE"
    assert result["deduplication"] == "NONE"
    assert result["source_independence_adjusted"] is False
    assert result["feature_eligibility"] == "EXPLORATORY_ONLY_NOT_PREDICTIVE"
    assert "not" in result["score_semantics"].lower()
    assert xrp["total_mentions"] == 2
    assert xrp["net_sentiment_score"] == 0.0
    assert xrp["pipelines_seen_in"] == ["BTC", "XRP"]
    assert xrp["assets_seen_in"] == ["BTC", "XRP"]
    assert xrp["pipeline_breakdown"]["XRP"]["bullish"] == 1
    assert xrp["pipeline_breakdown"]["BTC"]["bearish"] == 1
    assert "article-level" in xrp["score_semantics"].lower()


def test_cooccurrence_examples_identify_pipeline_not_verified_asset():
    xrp_entries = [{
        "title": "Ripple and XRP",
        "distill": {"entities": ["Ripple", "XRP"]},
    }]
    btc_entries = [{
        "title": "Ripple and Bitcoin",
        "distill": {"entities": ["Bitcoin", "Ripple"]},
    }]

    result = build_cooccurrence(xrp_entries, btc_entries, generated_at=GENERATED_AT)
    ripple_xrp = next(
        row for row in result["pairs"]
        if row["entity_a"] == "Ripple" and row["entity_b"] == "XRP"
    )
    ripple_btc = next(
        row for row in result["pairs"]
        if row["entity_a"] == "Bitcoin" and row["entity_b"] == "Ripple"
    )

    assert result["time_scope"] == "ALL_AVAILABLE_LOG_ENTRIES"
    assert result["feature_eligibility"] == "EXPLORATORY_ONLY_NOT_PREDICTIVE"
    assert result["source_independence_adjusted"] is False
    assert result["deduplication"] == "NONE"
    assert ripple_xrp["pipeline_counts"] == {"XRP": 1}
    assert ripple_xrp["example_headlines"][0]["pipeline_asset"] == "XRP"
    assert ripple_xrp["example_headlines"][0]["asset"] == "XRP"
    assert ripple_btc["pipeline_counts"] == {"BTC": 1}
    assert ripple_btc["example_headlines"][0]["pipeline_asset"] == "BTC"
    assert "not verified exclusive asset exposure" in result["pipeline_label_semantics"]


def test_naive_generated_timestamp_is_rejected():
    naive = datetime(2026, 10, 31, 11, 0)
    try:
        build_profile([], [], generated_at=naive)
    except ValueError as exc:
        assert "timezone-aware" in str(exc)
    else:
        raise AssertionError("naive timestamp should be rejected")
