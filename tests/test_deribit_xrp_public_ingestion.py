from datetime import datetime, timezone

import pytest

from barrot_agent.evolution.xrp_public_ingestion import (
    ENDPOINTS,
    LIVE_HTTP_CACHE_AGE_LIMITS,
    MAX_LIVE_AGE_SECONDS,
    MAX_ORDERBOOK_AGE_SECONDS,
    PARSERS,
    XRPIngestionError,
)

CAPTURED = datetime(2026, 11, 13, 16, 23, 41, tzinfo=timezone.utc)
TICKER_ID = "deribit_xrp_usdc_perpetual_ticker"
BOOK_ID = "deribit_xrp_usdc_perpetual_order_book"
TICKER_URL = "https://www.deribit.com/api/v2/public/ticker?instrument_name=XRP_USDC-PERPETUAL"
BOOK_URL = "https://www.deribit.com/api/v2/public/get_order_book?instrument_name=XRP_USDC-PERPETUAL&depth=50"


def _ms(value: datetime) -> int:
    return int(value.timestamp() * 1000)


def _ticker(*, timestamp: datetime, instrument: str = "XRP_USDC-PERPETUAL") -> dict:
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "instrument_name": instrument,
            "timestamp": _ms(timestamp),
            "best_bid_price": 1.012,
            "best_ask_price": 1.013,
            "last_price": 1.0125,
            "mark_price": 1.0124,
            "index_price": 1.0123,
            "current_funding": -0.0001,
            "funding_8h": 0.0002,
            "open_interest": 1000000,
            "volume": 250000,
            "volume_usd": 253000,
        },
    }


def _book(*, timestamp: datetime, instrument: str = "XRP_USDC-PERPETUAL") -> dict:
    return {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {
            "instrument_name": instrument,
            "timestamp": _ms(timestamp),
            "change_id": 12345,
            "prev_change_id": 12344,
            "bids": [[1.012, 1000], [1.011, 2000]],
            "asks": [[1.013, 1500], [1.014, 3000]],
        },
    }


def _call(source_id: str, payload: dict, captured: datetime = CAPTURED):
    url = TICKER_URL if source_id == TICKER_ID else BOOK_URL
    return PARSERS[source_id](
        payload,
        source_id=source_id,
        url=url,
        digest="a" * 64,
        captured=captured,
    )


def test_deribit_ticker_is_timestamped_but_remains_raw_only():
    records, source_time, eligible, reason = _call(
        TICKER_ID,
        _ticker(timestamp=datetime(2026, 11, 13, 16, 23, 0, tzinfo=timezone.utc)),
    )
    assert records == []
    assert source_time == "2026-11-13T16:23:00.000000Z"
    assert eligible is False
    assert "raw_only" in reason
    assert "open_interest_funding" in reason


def test_deribit_ticker_staleness_is_preserved_in_raw_only_reason():
    records, source_time, eligible, reason = _call(
        TICKER_ID,
        _ticker(timestamp=datetime(2026, 11, 13, 16, 10, 0, tzinfo=timezone.utc)),
    )
    assert records == []
    assert source_time == "2026-11-13T16:10:00.000000Z"
    assert eligible is False
    assert f"source_timestamp_older_than_{MAX_LIVE_AGE_SECONDS}_seconds" in reason


def test_deribit_ticker_rejects_wrong_instrument_and_future_timestamp():
    with pytest.raises(XRPIngestionError, match="instrument identity mismatch"):
        _call(
            TICKER_ID,
            _ticker(
                timestamp=datetime(2026, 11, 13, 16, 23, 0, tzinfo=timezone.utc),
                instrument="BTC_USDC-PERPETUAL",
            ),
        )
    with pytest.raises(XRPIngestionError, match="later than capture time"):
        _call(
            TICKER_ID,
            _ticker(timestamp=datetime(2026, 11, 13, 16, 24, 0, tzinfo=timezone.utc)),
        )


def test_deribit_order_book_is_timestamped_but_remains_raw_only():
    records, source_time, eligible, reason = _call(
        BOOK_ID,
        _book(timestamp=datetime(2026, 11, 13, 16, 23, 0, tzinfo=timezone.utc)),
    )
    assert records == []
    assert source_time == "2026-11-13T16:23:00.000000Z"
    assert eligible is False
    assert "raw_only" in reason
    assert "sequence_semantics" in reason


def test_deribit_order_book_rejects_crossed_books_and_invalid_sequence():
    crossed = _book(timestamp=datetime(2026, 11, 13, 16, 23, 0, tzinfo=timezone.utc))
    crossed["result"]["asks"][0][0] = 1.012
    with pytest.raises(XRPIngestionError, match="crossed or locked"):
        _call(BOOK_ID, crossed)

    invalid = _book(timestamp=datetime(2026, 11, 13, 16, 23, 0, tzinfo=timezone.utc))
    invalid["result"]["change_id"] = True
    with pytest.raises(XRPIngestionError, match="change_id is invalid"):
        _call(BOOK_ID, invalid)


def test_deribit_order_book_enforces_60_second_freshness():
    records, _source_time, eligible, reason = _call(
        BOOK_ID,
        _book(timestamp=datetime(2026, 11, 13, 16, 20, 0, tzinfo=timezone.utc)),
    )
    assert records == []
    assert eligible is False
    assert f"source_timestamp_older_than_{MAX_ORDERBOOK_AGE_SECONDS}_seconds" in reason


def test_deribit_endpoints_are_scheduled_with_explicit_freshness_limits():
    endpoint_map = dict(ENDPOINTS)
    assert endpoint_map[TICKER_ID] == TICKER_URL
    assert endpoint_map[BOOK_ID] == BOOK_URL
    assert LIVE_HTTP_CACHE_AGE_LIMITS[TICKER_ID] == MAX_LIVE_AGE_SECONDS
    assert LIVE_HTTP_CACHE_AGE_LIMITS[BOOK_ID] == MAX_ORDERBOOK_AGE_SECONDS
