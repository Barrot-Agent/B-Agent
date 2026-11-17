"""Tests for the PHOENIX sandbox runner.

Every test uses a temporary sandbox root.  No real repository data is touched.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from barrot_agent.sandbox import SandboxRunner

PASS_SCRIPT = """
import json
from pathlib import Path
Path("result.json").write_text(json.dumps({"passed": True, "metrics": {"value": 42}}))
print("experiment complete")
"""

FAIL_SCRIPT = """
import json
from pathlib import Path
Path("result.json").write_text(json.dumps({"passed": False, "metrics": {"value": 0}}))
raise SystemExit(1)
"""


class SandboxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name) / "sandbox"
        self.runner = SandboxRunner(root=self.root, timeout=10, memory_mb=512)

    def tearDown(self):
        self.tmp.cleanup()

    def _log_lines(self) -> list[dict]:
        path = self.root / "runs.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text().splitlines() if line]

    def test_passing_run_is_kept(self):
        result = self.runner.run(
            name="pass", script=PASS_SCRIPT, run_id="pass-1"
        )
        self.assertTrue(result.passed)
        self.assertTrue(result.kept)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.metrics["value"], 42)
        run_dir = self.root / result.run_dir
        self.assertTrue((run_dir / "work" / "experiment.py").exists())
        self.assertTrue((run_dir / "work" / "result.json").exists())
        self.assertIn("experiment complete", result.stdout)
        lines = self._log_lines()
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0]["passed"])
        self.assertTrue(lines[0]["kept"])

    def test_failing_run_is_discarded_but_logged(self):
        result = self.runner.run(name="fail", script=FAIL_SCRIPT, run_id="fail-1")
        self.assertFalse(result.passed)
        self.assertFalse(result.kept)
        self.assertEqual(result.exit_code, 1)
        self.assertFalse((self.root / "runs" / "fail-1").exists())
        lines = self._log_lines()
        self.assertEqual(len(lines), 1)
        self.assertFalse(lines[0]["passed"])
        self.assertFalse(lines[0]["kept"])

    def test_timeout_kills_the_run(self):
        runner = SandboxRunner(root=self.root, timeout=0.3, memory_mb=512)
        result = runner.run(
            name="timeout",
            script="import time\ntime.sleep(5)\n",
            run_id="timeout-1",
        )
        self.assertTrue(result.timed_out)
        self.assertFalse(result.passed)
        self.assertFalse((self.root / "runs" / "timeout-1").exists())

    def test_inputs_are_copied_not_reused(self):
        source = Path(self.tmp.name) / "input.txt"
        source.write_text("original", encoding="utf-8")
        script = """
import json
from pathlib import Path
path = Path("input.txt")
content = path.read_text()
path.write_text("changed")
Path("result.json").write_text(json.dumps({"passed": content == "original"}))
"""
        result = self.runner.run(
            name="copy",
            script=script,
            inputs={"input.txt": source},
            run_id="copy-1",
        )
        self.assertTrue(result.passed)
        self.assertEqual(source.read_text(encoding="utf-8"), "original")
        self.assertEqual(
            (self.root / result.run_dir / "work" / "input.txt").read_text(),
            "changed",
        )

    def test_copied_module_can_be_imported(self):
        module = Path(self.tmp.name) / "helper.py"
        module.write_text("VALUE = 7\n", encoding="utf-8")
        script = """
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import helper
Path("result.json").write_text(json.dumps({"passed": helper.VALUE == 7}))
"""
        result = self.runner.run(
            name="module",
            script=script,
            modules={"helper.py": module},
            run_id="module-1",
        )
        self.assertTrue(result.passed)

    def test_requires_exactly_one_script_source(self):
        with self.assertRaises(ValueError):
            self.runner.run(name="none")

    def test_missing_input_is_rejected_before_running(self):
        with self.assertRaises(FileNotFoundError):
            self.runner.run(
                name="missing",
                script=PASS_SCRIPT,
                inputs={"input.txt": Path(self.tmp.name) / "nope.txt"},
            )


if __name__ == "__main__":
    unittest.main()
