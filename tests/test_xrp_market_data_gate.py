import unittest
from datetime import datetime, timedelta, timezone

from scripts.xrp_market_data_gate import validate_snapshot


BASE = datetime(2026, 10, 26, 11, 3, 40, tzinfo=timezone.utc)


def stamp(delta_seconds=0):
    return (BASE + timedelta(seconds=delta_seconds)).isoformat()


def valid_snapshot():
    return {
        "cutoff_time": stamp(0),
        "spot": {
            "pair": "XRP/USD",
            "bid": 1.28836,
            "ask": 1.28853,
            "last": 1.28853,
            "event_time": stamp(-1),
            "received_time": stamp(-0.5),
        },
        "perpetual": {
            "pair": "XRP/USDT",
            "mark_price": 1.28818181,
            "index_price": 1.28854371,
            "event_time": stamp(-2),
            "received_time": stamp(-0.4),
        },
        "fx": {
            "pair": "USDT/USD",
            "bid": 0.99847,
            "ask": 0.99848,
            "last": 0.99847,
            "event_time": stamp(-3),
            "received_time": stamp(-0.3),
        },
    }


class TestXrpMarketDataGate(unittest.TestCase):
    def check(self, snapshot, **kwargs):
        return validate_snapshot(snapshot, now=BASE, **kwargs)

    def test_accepts_fresh_synchronized_three_leg_snapshot(self):
        result = self.check(valid_snapshot())
        self.assertTrue(result["accepted"])
        self.assertEqual(result["status"], "ACCEPTED")
        self.assertEqual(result["forecast_status"], "NOT_ISSUED")
        self.assertAlmostEqual(result["event_skew_seconds"], 2.0)

    def test_rejects_missing_event_timestamp(self):
        data = valid_snapshot()
        data["spot"]["event_time"] = None
        result = self.check(data)
        self.assertFalse(result["accepted"])
        self.assertTrue(any("spot.event_time" in item for item in result["errors"]))

    def test_rejects_timezone_naive_timestamp(self):
        data = valid_snapshot()
        data["spot"]["event_time"] = "2026-10-26T11:03:39"
        result = self.check(data)
        self.assertFalse(result["accepted"])
        self.assertTrue(any("must include a timezone" in item for item in result["errors"]))

    def test_rejects_stale_event(self):
        data = valid_snapshot()
        data["fx"]["event_time"] = stamp(-40)
        result = self.check(data)
        self.assertFalse(result["accepted"])
        self.assertTrue(any("fx: event timestamp is stale" in item for item in result["errors"]))

    def test_rejects_excessive_cross_leg_skew(self):
        data = valid_snapshot()
        data["fx"]["event_time"] = stamp(-10)
        result = self.check(data)
        self.assertFalse(result["accepted"])
        self.assertTrue(any("exceed allowed skew" in item for item in result["errors"]))

    def test_rejects_materially_future_event(self):
        data = valid_snapshot()
        data["spot"]["event_time"] = stamp(10)
        data["spot"]["received_time"] = stamp(0)
        result = self.check(data)
        self.assertFalse(result["accepted"])
        self.assertTrue(any("event timestamp is in the future" in item for item in result["errors"]))

    def test_rejects_future_cutoff(self):
        data = valid_snapshot()
        data["cutoff_time"] = stamp(20)
        result = self.check(data)
        self.assertFalse(result["accepted"])
        self.assertTrue(any("cutoff_time: timestamp is in the future" in item for item in result["errors"]))

    def test_rejects_wrong_quote_pair(self):
        data = valid_snapshot()
        data["perpetual"]["pair"] = "XRP/USD"
        result = self.check(data)
        self.assertFalse(result["accepted"])
        self.assertTrue(any("expected pair XRP/USDT" in item for item in result["errors"]))

    def test_rejects_crossed_spot_book(self):
        data = valid_snapshot()
        data["spot"]["bid"] = 1.30
        data["spot"]["ask"] = 1.29
        result = self.check(data)
        self.assertFalse(result["accepted"])
        self.assertTrue(any("crossed book" in item for item in result["errors"]))

    def test_rejects_nonfinite_price(self):
        data = valid_snapshot()
        data["spot"]["last"] = float("nan")
        result = self.check(data)
        self.assertFalse(result["accepted"])
        self.assertTrue(any("finite positive number" in item for item in result["errors"]))

    def test_last_trade_outside_book_is_warning_not_rejection(self):
        data = valid_snapshot()
        data["spot"]["last"] = 1.30
        result = self.check(data)
        self.assertTrue(result["accepted"])
        self.assertTrue(any("last trade is outside" in item for item in result["warnings"]))

    def test_large_cross_market_basis_is_warning_not_directional_signal(self):
        data = valid_snapshot()
        data["perpetual"]["mark_price"] = 1.40
        result = self.check(data)
        self.assertTrue(result["accepted"])
        self.assertTrue(any("basis exceeds warning threshold" in item for item in result["warnings"]))
        self.assertEqual(result["forecast_status"], "NOT_ISSUED")

    def test_rejects_stale_receive_timestamp(self):
        data = valid_snapshot()
        data["spot"]["received_time"] = stamp(-60)
        result = self.check(data)
        self.assertFalse(result["accepted"])
        self.assertTrue(any("received timestamp is stale" in item for item in result["errors"]))

    def test_rejects_event_timestamp_after_receive_time(self):
        data = valid_snapshot()
        data["spot"]["event_time"] = stamp(0)
        data["spot"]["received_time"] = stamp(-10)
        result = self.check(data)
        self.assertFalse(result["accepted"])
        self.assertTrue(any("event time is materially after receive time" in item for item in result["errors"]))

    def test_rejects_naive_now_argument(self):
        result = validate_snapshot(valid_snapshot(), now=datetime(2026, 10, 26, 11, 3, 40))
        self.assertFalse(result["accepted"])
        self.assertTrue(any("now: must be a timezone-aware datetime" in item for item in result["errors"]))


