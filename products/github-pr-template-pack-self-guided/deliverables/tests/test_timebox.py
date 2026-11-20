import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from paid_issue_kit.timebox import PHASES, TOTAL_MINUTES, Timebox


class Clock:
    def __init__(self):
        self.now = datetime(2026, 11, 18, 9, 0, tzinfo=timezone.utc)

    def __call__(self):
        return self.now

    def advance(self, minutes):
        self.now += timedelta(minutes=minutes)


def run_all(box, clock, minutes_per_phase=20):
    for name, _, _ in PHASES:
        clock.advance(minutes_per_phase)
        box.checkpoint(name)


class TestPhaseTable(unittest.TestCase):
    def test_total_is_120(self):
        self.assertEqual(TOTAL_MINUTES, 120)
        self.assertEqual(sum(minutes for _, minutes, _ in PHASES), 120)

    def test_six_phases(self):
        self.assertEqual(len(PHASES), 6)


class TestTimebox(unittest.TestCase):
    def test_not_started(self):
        box = Timebox("demo", clock=Clock())
        self.assertEqual(box.status()["verdict"], "NOT STARTED")

    def test_start_sets_in_progress(self):
        box = Timebox("demo", clock=Clock())
        box.start()
        self.assertEqual(box.status()["verdict"], "IN PROGRESS")

    def test_out_of_order_checkpoint_rejected(self):
        box = Timebox("demo", clock=Clock())
        box.start()
        with self.assertRaisesRegex(ValueError, "expected 'triage'"):
            box.checkpoint("patch")

    def test_checkpoint_before_start_rejected(self):
        box = Timebox("demo", clock=Clock())
        with self.assertRaises(ValueError):
            box.checkpoint("triage")

    def test_completed_phases_and_next(self):
        clock = Clock()
        box = Timebox("demo", clock=clock)
        box.start()
        clock.advance(10)
        box.checkpoint("triage")
        self.assertEqual(box.completed, ["triage"])
        self.assertEqual(box.next_phase(), "reproduce")

    def test_claim_holds_inside_budget(self):
        clock = Clock()
        box = Timebox("demo", clock=clock)
        box.start()
        run_all(box, clock, minutes_per_phase=19)
        state = box.status()
        self.assertEqual(state["verdict"], "CLAIM HOLDS")
        self.assertLessEqual(state["elapsed_minutes"], 120)
        self.assertIn("merge and payment are excluded", state["claim_scope"])

    def test_claim_broken_over_budget(self):
        clock = Clock()
        box = Timebox("demo", clock=clock)
        box.start()
        run_all(box, clock, minutes_per_phase=25)
        self.assertEqual(box.status()["verdict"], "CLAIM BROKEN")

    def test_phase_over_budget_flag(self):
        clock = Clock()
        box = Timebox("demo", clock=clock)
        box.start()
        clock.advance(30)
        state = box.status()
        self.assertTrue(state["next_phase_over_budget"])
        self.assertGreater(state["minutes_into_next_phase"], state["next_phase_budget_minutes"])

    def test_extra_checkpoint_rejected(self):
        clock = Clock()
        box = Timebox("demo", clock=clock)
        box.start()
        run_all(box, clock, minutes_per_phase=1)
        with self.assertRaises(ValueError):
            box.checkpoint("triage")

    def test_save_and_load_roundtrip(self):
        clock = Clock()
        box = Timebox("demo", clock=clock)
        box.start()
        clock.advance(12)
        box.checkpoint("triage", note="scope confirmed")
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "run.json")
            box.save(path)
            loaded = Timebox.load(path, clock=clock)
        self.assertEqual(loaded.mission, "demo")
        self.assertEqual(loaded.completed, ["triage"])
        self.assertEqual(loaded.checkpoints[0]["note"], "scope confirmed")
        self.assertEqual(loaded.status()["verdict"], "IN PROGRESS")

    def test_report_mentions_verdict(self):
        box = Timebox("demo", clock=Clock())
        box.start()
        self.assertIn("Verdict: IN PROGRESS", box.report())

    def test_empty_mission_rejected(self):
        with self.assertRaises(ValueError):
            Timebox("")

    def test_double_start_rejected(self):
        box = Timebox("demo", clock=Clock())
        box.start()
        with self.assertRaises(ValueError):
            box.start()

    def test_to_dict_shape(self):
        data = Timebox("demo", clock=Clock()).to_dict()
        self.assertEqual(data["mission"], "demo")
        self.assertEqual(len(data["phases"]), 6)
        json.dumps(data)


if __name__ == "__main__":
    unittest.main()
