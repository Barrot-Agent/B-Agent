"""Tests for the PHOENIX / LUCY power protocol."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from barrot_agent.infinite_ingest.models import MemoryRecord, utc_now
from barrot_agent.infinite_ingest.storage import Store
from barrot_agent.phoenix import EvidenceRequired, Phoenix, PowerLocked
from barrot_agent.sandbox import SandboxRunner

PASS_SCRIPT = """
import json
from pathlib import Path
Path("result.json").write_text(json.dumps({"passed": True, "metrics": {"recall": 1.0}}))
"""

FAIL_SCRIPT = """
import json
from pathlib import Path
Path("result.json").write_text(json.dumps({"passed": False}))
raise SystemExit(1)
"""


class PhoenixTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = Store(self.root / "data")
        self.memory = self.root / "MEMORY.md"
        self.state_path = self.root / "phoenix_state.json"
        self.phoenix = Phoenix(
            state_path=self.state_path,
            memory_path=self.memory,
            experiment_log=self.root / "phoenix_experiments.jsonl",
            runner=SandboxRunner(root=self.root / "sandbox", timeout=10, memory_mb=512),
            store=self.store,
        )

    def tearDown(self):
        self.tmp.cleanup()

    # -- helpers ---------------------------------------------------------

    def _unlock_one(self):
        return self.phoenix.unlock(
            1,
            {
                "kind": "test_suite",
                "passed": True,
                "test": "tests/test_infinite_ingest.py",
                "artifact": "barrot_agent/infinite_ingest",
                "source": "unit test",
            },
        )

    def _unlock_two(self):
        self._unlock_one()
        return self.phoenix.unlock(
            2,
            {
                "kind": "sandbox",
                "passed": True,
                "test": "gist-budget",
                "artifact": "data/sandbox/runs/run-1",
                "sandbox_run": "run-1",
                "source": "unit test",
            },
        )

    def _record(self, statement: str, url: str) -> MemoryRecord:
        record = MemoryRecord.build(
            statement=statement,
            kind="fact",
            source_url=url,
            retrieved_at=utc_now(),
            document_sha256="x",
        )
        self.store.append_memory([record])
        return record

    def _two_capabilities(self):
        first = self._record("Alpha memory keeps the first fact.", "https://a.test")
        second = self._record("Beta memory keeps the second fact.", "https://b.test")
        self.store.save_capability(
            "alpha_cap",
            {
                "name": "alpha_cap",
                "questions": [
                    {
                        "id": "alpha",
                        "question": "What does alpha keep?",
                        "expect": ["first fact"],
                    }
                ],
                "memory_ids": [first.id],
                "sources": [{"url": "https://a.test", "kind": "web"}],
                "history": [],
            },
        )
        self.store.save_capability(
            "beta_cap",
            {
                "name": "beta_cap",
                "questions": [
                    {
                        "id": "beta",
                        "question": "What does beta keep?",
                        "expect": ["second fact"],
                    }
                ],
                "memory_ids": [second.id],
                "sources": [{"url": "https://b.test", "kind": "web"}],
                "history": [],
            },
        )

    # -- state and gates -------------------------------------------------

    def test_status_starts_unawakened(self):
        status = self.phoenix.status()
        self.assertEqual(status["level"], 0)
        self.assertEqual(status["name"], "unawakened")
        self.assertEqual(status["next"]["level"], 1)
        self.assertTrue(status["next"]["implemented"])

    def test_level_one_requires_passing_evidence(self):
        with self.assertRaises(EvidenceRequired):
            self.phoenix.unlock(
                1, {"passed": False, "test": "x", "artifact": "y"}
            )
        with self.assertRaises(EvidenceRequired):
            self.phoenix.unlock(1, {"passed": True, "artifact": "y"})
        self.assertEqual(self.phoenix.level, 0)

    def test_level_one_unlock_is_persisted_and_logged(self):
        self._unlock_one()
        self.assertEqual(self.phoenix.level, 1)
        self.assertTrue(self.state_path.exists())
        state = json.loads(self.state_path.read_text())
        self.assertEqual(state["level"], 1)
        self.assertEqual(state["percent"], 10)
        self.assertIn("1", state["levels"])
        text = self.memory.read_text()
        self.assertIn("## Power log", text)
        for power in (
            "ingestion",
            "transmutation",
            "cross_analysis",
            "single_capability_refinement",
        ):
            self.assertIn(f" - {power}\n", text)

    def test_levels_unlock_in_order(self):
        evidence = {
            "kind": "sandbox",
            "passed": True,
            "test": "x",
            "artifact": "y",
            "sandbox_run": "r",
        }
        with self.assertRaises(ValueError):
            self.phoenix.unlock(2, evidence)

    def test_level_two_requires_sandbox_evidence(self):
        self._unlock_one()
        with self.assertRaises(EvidenceRequired):
            self.phoenix.unlock(
                2,
                {
                    "kind": "test_suite",
                    "passed": True,
                    "test": "x",
                    "artifact": "y",
                },
            )
        self.assertEqual(self.phoenix.level, 1)

    def test_levels_three_and_four_are_locked(self):
        valid = {
            "kind": "sandbox",
            "passed": True,
            "test": "x",
            "artifact": "y",
            "sandbox_run": "r",
        }
        with self.assertRaises(PowerLocked):
            self.phoenix.unlock(3, valid)
        with self.assertRaises(PowerLocked):
            self.phoenix.unlock(4, valid)
        self.assertEqual(self.phoenix.level, 0)

    def test_status_reports_locked_level_three(self):
        self._unlock_two()
        status = self.phoenix.status()
        self.assertEqual(status["level"], 2)
        self.assertEqual(status["percent"], 30)
        self.assertEqual(status["next"]["level"], 3)
        self.assertFalse(status["next"]["implemented"])
        self.assertIn("not implemented", status["next"]["requires"])

    # -- sandbox experiment gate ----------------------------------------

    def test_passing_experiment_unlocks_level_two(self):
        self._unlock_one()
        result = self.phoenix.run_experiment(
            "8 x 12 keeps the facts at a lower budget",
            name="gist-budget",
            script=PASS_SCRIPT,
            source="unit test",
            unlock_level=2,
        )
        self.assertTrue(result.passed)
        self.assertEqual(self.phoenix.level, 2)
        state = json.loads(self.state_path.read_text())
        evidence = state["levels"]["2"]
        self.assertEqual(evidence["kind"], "sandbox")
        self.assertEqual(evidence["sandbox_run"], result.run_id)
        self.assertEqual(evidence["metrics"]["recall"], 1.0)
        text = self.memory.read_text()
        self.assertIn("### Power", text)
        self.assertIn("sandbox_experimentation", text)
        self.assertIn("capability_combination", text)
        self.assertIn("gist-budget", text)

    def test_failed_experiment_does_not_unlock(self):
        self._unlock_one()
        with self.assertRaises(EvidenceRequired):
            self.phoenix.run_experiment(
                "this should fail",
                name="bad",
                script=FAIL_SCRIPT,
                unlock_level=2,
            )
        self.assertEqual(self.phoenix.level, 1)
        log = (self.root / "phoenix_experiments.jsonl").read_text().strip()
        self.assertIn('"passed": false', log)

    def test_experiment_needs_level_one(self):
        with self.assertRaises(PermissionError):
            self.phoenix.run_experiment("x", name="x", script=PASS_SCRIPT)

    # -- capability combination -----------------------------------------

    def test_combination_requires_level_two(self):
        self._unlock_one()
        self._two_capabilities()
        with self.assertRaises(PermissionError):
            self.phoenix.combine("combined", "alpha_cap", "beta_cap")

    def test_combination_keeps_a_tested_third_capability(self):
        self._unlock_two()
        self._two_capabilities()
        result = self.phoenix.combine("combined", "alpha_cap", "beta_cap")
        self.assertTrue(result["kept"])
        combined = self.store.load_capability("combined")
        self.assertEqual(combined["derived_from"], ["alpha_cap", "beta_cap"])
        self.assertEqual(len(combined["questions"]), 2)
        self.assertEqual(combined["status"], "tested")
        self.assertTrue(all(score >= 1.0 for score in (
            result["scores"]["alpha_cap"]["recall"],
            result["scores"]["beta_cap"]["recall"],
            result["scores"]["combined"]["recall"],
        )))
        self.assertEqual(
            len(combined["memory_ids"]),
            len(set(combined["memory_ids"])),
        )
        self.assertTrue((self.root / "data" / "capabilities" / "combined.json").exists())

    def test_combination_discards_a_regression(self):
        self._unlock_two()
        second = self._record("Beta memory keeps the second fact.", "https://b.test")
        self.store.save_capability(
            "alpha_cap",
            {
                "name": "alpha_cap",
                "questions": [
                    {"id": "alpha", "question": "What is absent?", "expect": ["absent fact"]}
                ],
                "memory_ids": [],
                "sources": [{"url": "https://a.test", "kind": "web"}],
                "history": [],
            },
        )
        self.store.save_capability(
            "beta_cap",
            {
                "name": "beta_cap",
                "questions": [
                    {
                        "id": "beta",
                        "question": "What does beta keep?",
                        "expect": ["second fact"],
                    }
                ],
                "memory_ids": [second.id],
                "sources": [{"url": "https://b.test", "kind": "web"}],
                "history": [],
            },
        )
        result = self.phoenix.combine("combined", "alpha_cap", "beta_cap")
        self.assertFalse(result["kept"])
        self.assertFalse(self.store.capability_path("combined").exists())

    def test_combination_does_not_overwrite_by_default(self):
        self._unlock_two()
        self._two_capabilities()
        self.phoenix.combine("combined", "alpha_cap", "beta_cap")
        with self.assertRaises(ValueError):
            self.phoenix.combine("combined", "alpha_cap", "beta_cap")

    # -- logging and continuous mode ------------------------------------

    def test_log_power_is_idempotent_per_day(self):
        self.assertTrue(
            self.phoenix.log_power(
                "test_power", source="s", test="t", date="2026-01-01"
            )
        )
        self.assertFalse(
            self.phoenix.log_power(
                "test_power", source="s", test="t", date="2026-01-01"
            )
        )
        self.assertEqual(self.memory.read_text().count("### Power 2026-01-01 - test_power"), 1)

    def test_continuous_mode_is_recorded_as_bounded(self):
        state = self.phoenix.record_continuous({"cycles": 2, "capability": "x"})
        self.assertTrue(state["enabled"])
        self.assertEqual(state["mode"], "bounded")
        self.assertEqual(state["cycles"], 2)
        reloaded = json.loads(self.state_path.read_text())
        self.assertTrue(reloaded["continuous"]["enabled"])


if __name__ == "__main__":
    unittest.main()
