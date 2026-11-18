import contextlib
import io
import json
import os
import tempfile
import unittest

from paid_issue_kit.cli import main


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)
    return path


def candidate():
    return {
        "issue_id": "issue-7",
        "url": "https://github.com/example/project/issues/7",
        "repo": "example/project",
        "title": "Handle empty config file",
        "amount_usd": 300,
        "acceptance_criteria": "An empty config file produces a clear error, not a traceback.",
        "repo_stars": 88,
        "repo_pushed_at": "2026-11-05T00:00:00Z",
        "labels": ["bounty"],
        "effort_hours": 2,
    }


def plan():
    return {
        "issue_id": "issue-7",
        "issue_url": "https://github.com/example/project/issues/7",
        "summary": "Raises a clear error for an empty config file.",
        "change_bullets": ["Added an empty-file guard.", "Added a regression test."],
        "why": "An empty config currently raises an unhandled traceback.",
        "test_command": "python3 -m pytest tests/test_config.py -q",
        "test_result": "8 passed in 0.31s",
        "risk": "A valid but empty config now errors instead of continuing.",
        "rollback": "Revert the commit and the previous parse path returns.",
        "checklist": ["Tests pass locally", "No unrelated files changed"],
        "claims": [
            {
                "text": "The empty-file path is covered by a test.",
                "evidence": "tests/test_config.py::test_empty_file",
                "limit": "Only the empty-file case is covered.",
            }
        ],
        "command": "python3 -m pytest tests/test_config.py -q",
        "exit_code": 0,
        "output": "8 passed in 0.31s",
    }


class TestCli(unittest.TestCase):
    def test_score_writes_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = write_json(os.path.join(tmp, "in.json"), [candidate()])
            out = os.path.join(tmp, "ledger.csv")
            with contextlib.redirect_stdout(io.StringIO()):
                code = main(
                    ["score", "--input", source, "--out", out,
                     "--now", "2026-11-18T12:00:00+00:00"]
                )
            self.assertEqual(code, 0)
            with open(out, encoding="utf-8") as handle:
                text = handle.read()
            self.assertIn("decision", text.splitlines()[0])
            self.assertIn("GO", text)

    def test_score_prints_csv_without_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = write_json(os.path.join(tmp, "in.json"), {"candidates": [candidate()]})
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                code = main(["score", "--input", source, "--now", "2026-11-18T12:00:00+00:00"])
            self.assertEqual(code, 0)
            self.assertIn("issue-7", buffer.getvalue())

    def test_score_bad_input_returns_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = write_json(os.path.join(tmp, "in.json"), {"nope": True})
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(["score", "--input", source]), 2)

    def test_pr_writes_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = write_json(os.path.join(tmp, "plan.json"), plan())
            out_dir = os.path.join(tmp, "out")
            with contextlib.redirect_stdout(io.StringIO()):
                code = main(["pr", "--plan", source, "--out-dir", out_dir])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(os.path.join(out_dir, "PR_BODY.md")))
            self.assertTrue(os.path.exists(os.path.join(out_dir, "EVIDENCE_PACK.md")))

    def test_pr_blocks_bad_plan(self):
        bad = plan()
        bad["test_result"] = "Guaranteed to work"
        with tempfile.TemporaryDirectory() as tmp:
            source = write_json(os.path.join(tmp, "plan.json"), bad)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = main(["pr", "--plan", source])
            self.assertEqual(code, 1)
            self.assertIn("BLOCKED", stderr.getvalue())

    def test_pr_missing_file_returns_two(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["pr", "--plan", "/nonexistent/plan.json"]), 2)

    def test_timebox_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = os.path.join(tmp, "run.json")
            with contextlib.redirect_stdout(io.StringIO()):
                start = main(["timebox", "start", "--state", state, "--mission", "demo"])
                self.assertEqual(start, 0)
                self.assertEqual(
                    main(["timebox", "checkpoint", "--state", state, "--phase", "triage"]), 0
                )
                self.assertEqual(main(["timebox", "status", "--state", state]), 0)
            with open(state, encoding="utf-8") as handle:
                data = json.load(handle)
            self.assertEqual(data["mission"], "demo")
            self.assertEqual([c["phase"] for c in data["checkpoints"]], ["triage"])

    def test_timebox_bad_order_returns_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = os.path.join(tmp, "run.json")
            with contextlib.redirect_stdout(io.StringIO()):
                main(["timebox", "start", "--state", state, "--mission", "demo"])
            with contextlib.redirect_stderr(io.StringIO()):
                code = main(["timebox", "checkpoint", "--state", state, "--phase", "submit"])
            self.assertEqual(code, 1)

    def test_timebox_start_requires_mission(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = os.path.join(tmp, "run.json")
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    main(["timebox", "start", "--state", state])
            self.assertEqual(raised.exception.code, 2)

    def test_phases_command(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = main(["phases"])
        self.assertEqual(code, 0)
        self.assertIn("120", buffer.getvalue())
        self.assertIn("triage", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
