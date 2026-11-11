"""Tests for scripts/transmute.py — the transmutation loop.

Runnable under pytest or plain unittest (stdlib only in the script itself).
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "transmute.py"

GOOD_BASELINE = "def add(a, b):\n    return a + b\n"
GOOD_FASTER = "def add(a, b):\n    return a + b  # fast path\n"
BROKEN = "def add(a, b)\n    return a + b\n"  # syntax error

MINI_TEST = (
    "from target_mod import add\n\n"
    "def test_add():\n"
    "    assert add(1, 2) == 3\n"
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _mk(tmp: Path):
    _write(tmp / "target_mod.py", GOOD_BASELINE)
    _write(tmp / "variant_fast.py", GOOD_FASTER)
    _write(tmp / "variant_broken.py", BROKEN)
    _write(tmp / "test_target_mod.py", MINI_TEST)


class TestTransmute(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="transmute_test_"))
        _mk(self.tmp)

    def test_compile_gate(self):
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import transmute

        ok, _, _ = transmute.run_py_compile(self.tmp / "target_mod.py", self.tmp)
        bad, _, _ = transmute.run_py_compile(self.tmp / "variant_broken.py", self.tmp)
        self.assertTrue(ok)
        self.assertFalse(bad)

    def test_score_prefers_tests_then_speed(self):
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import transmute

        winner_tests = transmute.score(rate=1.0, wall_ms=9999, lines=10)
        loser_tests = transmute.score(rate=0.0, wall_ms=1, lines=1)
        self.assertGreater(winner_tests, loser_tests)
        fast = transmute.score(rate=1.0, wall_ms=10, lines=5)
        slow = transmute.score(rate=1.0, wall_ms=20, lines=5)
        self.assertGreater(fast, slow)

    def test_variant_wins_and_log_written(self):
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import transmute

        log = self.tmp / "log.json"
        report = transmute.transmute(
            target=self.tmp / "target_mod.py",
            variants=[self.tmp / "variant_fast.py", self.tmp / "variant_broken.py"],
            tests=[self.tmp / "test_target_mod.py"],
            runner="unittest",
            log_path=log,
            keep_losers=True,
            interactive=False,
            repeats=3,
        )
        # Winner applied to the target file.
        self.assertEqual(
            (self.tmp / "target_mod.py").read_text(), GOOD_FASTER
        )
        self.assertEqual(report["winner"], "variant_fast.py")
        self.assertTrue(log.exists())
        runs = json.loads(log.read_text())
        self.assertEqual(runs[-1]["winner"], "variant_fast.py")
        self.assertIn("baseline", [c["name"] for c in runs[-1]["candidates"]])

    def test_broken_variant_never_replaces_target(self):
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import transmute

        report = transmute.transmute(
            target=self.tmp / "target_mod.py",
            variants=[self.tmp / "variant_broken.py"],
            tests=[self.tmp / "test_target_mod.py"],
            runner="unittest",
            log_path=self.tmp / "log.json",
            keep_losers=True,
            interactive=False,
        )
        self.assertEqual((self.tmp / "target_mod.py").read_text(), GOOD_BASELINE)
        self.assertEqual(report["winner"], "baseline")

    def test_cli_end_to_end(self):
        _mk(self.tmp)
        log = self.tmp / "log.json"
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(self.tmp / "target_mod.py"),
                "--variant",
                str(self.tmp / "variant_fast.py"),
                "--variant",
                str(self.tmp / "variant_broken.py"),
                "--tests",
                str(self.tmp / "test_target_mod.py"),
                "--runner",
                "unittest",
                "--repeats",
                "3",
                "--log",
                str(log),
                "--cwd",
                str(self.tmp),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual((self.tmp / "target_mod.py").read_text(), GOOD_FASTER)
        runs = json.loads(log.read_text())
        self.assertEqual(runs[-1]["winner"], "variant_fast.py")

    def test_cli_fails_without_variants_when_not_tty(self):
        _mk(self.tmp)
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(self.tmp / "target_mod.py"),
                "--tests",
                str(self.tmp / "test_target_mod.py"),
                "--runner",
                "unittest",
                "--log",
                str(self.tmp / "log.json"),
                "--cwd",
                str(self.tmp),
            ],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=120,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("variant", (proc.stdout + proc.stderr).lower())


if __name__ == "__main__":
    unittest.main()
