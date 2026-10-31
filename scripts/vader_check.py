#!/usr/bin/env python3
"""
BARROT-Ω VADER CROSS-CHECK — free, zero-API-cost secondary sentiment
signal to compare against the Groq LLM classification. Pure lexicon-based,
no compiled dependencies, safe on Termux.

Honest limitation found and fixed during build: plain VADER's general-
purpose lexicon has near-zero coverage of crypto/finance vocabulary
(bullish, surge, crash, bankruptcy all scored neutral 0.0 untested).
A small domain lexicon is added on top of VADER's base lexicon to fix
this. This does NOT replace the Groq classification - it's a free
secondary signal to flag disagreement, not a primary source.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_CRYPTO_LEXICON = {
    "bullish": 2.5, "bearish": -2.5, "surge": 2.0, "surges": 2.0,
    "rally": 2.0, "rallies": 2.0, "plunge": -2.5, "plunges": -2.5,
    "crash": -2.8, "crashes": -2.8, "dump": -2.0, "dumps": -2.0,
    "moon": 2.5, "mooning": 2.5, "dip": -1.0, "dips": -1.0,
    "breakout": 1.8, "correction": -1.2, "bankruptcy": -3.0,
    "hack": -2.5, "hacked": -2.5, "exploit": -2.0, "exploited": -2.0,
    "adoption": 1.5, "approval": 2.0, "approved": 2.0,
    "reject": -2.0, "rejected": -2.0, "lawsuit": -1.5,
    "settlement": 1.0, "partnership": 1.5, "listing": 1.2,
    "delisting": -2.0,
}

_analyzer = SentimentIntensityAnalyzer()
_analyzer.lexicon.update(_CRYPTO_LEXICON)


def vader_check(text: str) -> dict:
    """Returns VADER's read on the given text plus a bullish/bearish/
    neutral label using the same thresholds convention as the Groq
    classification, so the two can be directly compared."""
    scores = _analyzer.polarity_scores(text or "")
    compound = scores["compound"]
    if compound >= 0.2:
        label = "bullish"
    elif compound <= -0.2:
        label = "bearish"
    else:
        label = "neutral"
    return {"vader_compound": compound, "vader_sentiment": label}


def agrees_with(groq_sentiment: str, vader_result: dict) -> bool:
    """True if VADER's label matches the Groq label exactly."""
    return vader_result.get("vader_sentiment") == groq_sentiment
