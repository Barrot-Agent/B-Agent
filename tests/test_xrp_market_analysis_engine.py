from __future__ import annotations

import json

import pytest

from scripts.market_analysis_engine import validate_analysis_response


def valid_response() -> dict:
    return {
        "summary": "The historical sample is incomplete and no directional forecast is issued.",
        "observations": ["Observed signal-history values vary across the sampled dates."],
        "data_quality": ["The source table is not a point-in-time feature store."],
        "competing_hypotheses": ["Different market regimes may explain the historical variation."],
        "validation_gaps": ["Chronological walk-forward testing has not been completed."],
        "forecast_status": "NOT_ISSUED",
        "trade_recommendations": [],
    }


def test_descriptive_analysis_accepts_non_actionable_historical_text():
    payload = valid_response()

    result = validate_analysis_response(json.dumps(payload))

    assert result["forecast_status"] == "NOT_ISSUED"
    assert result["trade_recommendations"] == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("summary", "Buy XRP now at $1.20; price target $2.00."),
        ("observations", ["XRP will rise to $2.00."]),
        ("data_quality", ["The model gives a buy signal for XRP."]),
        ("competing_hypotheses", ["XRP is expected to rally next week."]),
        ("validation_gaps", ["Use an entry price of $1.20 and a stop-loss at $1.10."]),
    ],
)
def test_descriptive_analysis_rejects_actionable_or_directional_text(field, value):
    payload = valid_response()
    payload[field] = value if isinstance(value, list) else value

    with pytest.raises(ValueError, match="prohibited forecast or trading language"):
        validate_analysis_response(json.dumps(payload))
