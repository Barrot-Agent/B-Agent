"""
Converts emit_signal.py's continuous 0-100 score into the -1..+1 range
hrm_resolve() expects for a single signal channel. Only the sentiment
channel has real data right now — orderbook/onchain are explicitly
unavailable and must be passed as 0.0 (neutral), never guessed.
"""


def score_to_unit(score: float) -> float:
    """Map 0-100 -> -1.0..+1.0. 50 = neutral, 100 = max bullish, 0 = max bearish."""
    score = max(0.0, min(100.0, float(score)))
    return (score - 50.0) / 50.0
