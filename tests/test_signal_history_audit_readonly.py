import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "audit_signal_history_readonly",
    ROOT / "scripts" / "audit_signal_history_readonly.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReadOnlySignalHistoryAuditTests(unittest.TestCase):
    def test_never_emits_accuracy_percentage(self):
        result = MODULE.audit_history_text(
            json.dumps({"checked": True, "correct": True, "price_at_emission": 1.2})
        )
        self.assertIsNone(result["accuracy_pct"])
        self.assertEqual(result["skill_status"], "NOT_ESTIMABLE_MISSING_EVALUATION_TIMESTAMPS")

    def test_counts_missing_evaluation_timestamp(self):
        raw = "\n".join([
            json.dumps({"checked": True, "correct": True, "price_at_emission": 1.2}),
            json.dumps({"checked": False, "price_at_emission": 0}),
        ])
        result = MODULE.audit_history_text(raw)
        self.assertEqual(result["checked_count"], 1)
        self.assertEqual(result["unchecked_count"], 1)
        self.assertEqual(result["checked_missing_evaluation_timestamp"], 1)

    def test_invalid_prices_are_counted(self):
        raw = "\n".join([
            json.dumps({"checked": True, "price_at_emission": 0}),
            json.dumps({"checked": False, "price_at_emission": float("nan")}),
        ])
        result = MODULE.audit_history_text(raw)
        self.assertEqual(result["invalid_emission_price_count"], 2)

    def test_fixed_horizon_requires_timestamp_target_price_and_horizon(self):
        raw = json.dumps({
            "checked": True,
            "correct": True,
            "price_at_emission": 1.2,
            "checked_at": "2026-10-23T01:00:00Z",
        })
        self.assertEqual(MODULE.audit_history_text(raw)["fixed_horizon_candidate_count"], 0)

    def test_malformed_lines_counted_without_crashing(self):
        result = MODULE.audit_history_text("{broken\n")
        self.assertEqual(result["parse_errors"], 1)
        self.assertEqual(result["record_count"], 0)

    def test_input_is_not_modified(self):
        raw = json.dumps({"checked": True, "correct": True, "price_at_emission": 1.2})
        before = raw[:]
        MODULE.audit_history_text(raw)
        self.assertEqual(raw, before)


if __name__ == "__main__":
    unittest.main()
