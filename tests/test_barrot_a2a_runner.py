from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from scripts.barrot_a2a_runner import (
    WorkerClient,
    build_prompt,
    execute_task,
    fit_result_payload,
    redact,
    run_once,
)


class RunnerRedactionTests(unittest.TestCase):
    def test_redacts_common_secret_assignments(self) -> None:
        value = redact("api_key=supersecret Authorization: Bearer abc123")
        self.assertNotIn("supersecret", value)
        self.assertNotIn("abc123", value)
        self.assertIn("[REDACTED]", value)

    def test_prompt_includes_task_identity_and_execution_boundaries(self) -> None:
        prompt = build_prompt({
            "task_id": "task-12345678",
            "title": "Inspect worker",
            "instructions": "Review the A2A worker and tests.",
            "context": {"branch": "feature/test"},
        })
        self.assertIn("task-12345678", prompt)
        self.assertIn("Review the A2A worker", prompt)
        self.assertIn("Do not commit, push, merge, deploy", prompt)


class RunnerExecutionTests(unittest.TestCase):
    @patch("scripts.barrot_a2a_runner.subprocess.run")
    def test_uses_existing_opencode_shared_runtime(self, run_mock: Mock) -> None:
        run_mock.return_value = subprocess.CompletedProcess(
            args=["opencode"], returncode=0, stdout='{"type":"text"}', stderr=""
        )
        result, success, error = execute_task(
            {"task_id": "task-12345678", "title": "Test", "instructions": "Do work."},
            Path("/tmp"),
        )
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(result["runtime"], "existing-opencode-shared-service")
        args, kwargs = run_mock.call_args
        self.assertEqual(args[0][:5], ["opencode", "run", "--agent", "barrot", "--format"])
        self.assertEqual(args[0][5], "json")
        self.assertEqual(kwargs["cwd"], "/tmp")
        self.assertEqual(kwargs["timeout"], 1800)

    @patch("scripts.barrot_a2a_runner.subprocess.run")
    def test_nonzero_exit_is_failed(self, run_mock: Mock) -> None:
        run_mock.return_value = subprocess.CompletedProcess(
            args=["opencode"], returncode=7, stdout="", stderr="test failure"
        )
        result, success, error = execute_task(
            {"task_id": "task-12345678", "instructions": "Do work."}, Path("/tmp")
        )
        self.assertFalse(success)
        self.assertEqual(error, "opencode_exit_7")
        self.assertEqual(result["exit_code"], 7)

    @patch("scripts.barrot_a2a_runner.subprocess.run")
    def test_timeout_is_reported_without_claiming_success(self, run_mock: Mock) -> None:
        run_mock.side_effect = subprocess.TimeoutExpired("opencode", 10, output="partial")
        result, success, error = execute_task(
            {"task_id": "task-12345678", "instructions": "Do work."},
            Path("/tmp"),
            timeout_seconds=10,
        )
        self.assertFalse(success)
        self.assertEqual(error, "opencode_execution_timeout")
        self.assertTrue(result["timed_out"])

    @patch("scripts.barrot_a2a_runner.subprocess.run", side_effect=FileNotFoundError)
    def test_missing_cli_fails_closed(self, _run_mock: Mock) -> None:
        result, success, error = execute_task(
            {"task_id": "task-12345678", "instructions": "Do work."}, Path("/tmp")
        )
        self.assertFalse(success)
        self.assertEqual(error, "opencode_cli_not_found")
        self.assertEqual(result["error"], "opencode_cli_not_found")


class RunnerQueueTests(unittest.TestCase):
    def test_claim_executes_and_records_completion(self) -> None:
        client = Mock(spec=WorkerClient)
        client.claim.return_value = {
            "task_id": "task-12345678",
            "title": "Task",
            "instructions": "Do work.",
            "attempts": 1,
        }
        with patch(
            "scripts.barrot_a2a_runner.execute_task",
            return_value=({"exit_code": 0}, True, None),
        ):
            did_work = run_once(client, Path("/tmp"), "barrot", 60, "opencode")
        self.assertTrue(did_work)
        client.complete.assert_called_once()
        args = client.complete.call_args.args
        self.assertEqual(args[0], "task-12345678")
        self.assertTrue(args[3])

    def test_empty_queue_does_not_invoke_completion(self) -> None:
        client = Mock(spec=WorkerClient)
        client.claim.return_value = None
        self.assertFalse(run_once(client, Path("/tmp"), "barrot", 60, "opencode"))
        client.complete.assert_not_called()


    def test_singleton_lock_prevents_duplicate_runners(self) -> None:
        import os
        import tempfile
        from scripts.barrot_a2a_runner import acquire_runner_lock, runner_is_active

        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "runner.lock"
            with patch.dict(os.environ, {"BARROT_A2A_LOCK_FILE": str(lock_path)}):
                lock = acquire_runner_lock()
                self.assertIsNotNone(lock)
                try:
                    self.assertTrue(runner_is_active())
                finally:
                    lock.close()
                self.assertFalse(runner_is_active())


    def test_completion_result_stays_under_encoded_payload_limit(self) -> None:
        import json
        result = {
            "stdout": ('"\\n😀' * 30_000),
            "stderr": ('\\t\\\\' * 10_000),
            "exit_code": 0,
        }
        bounded = fit_result_payload(result)
        envelope = {
            "worker_id": "worker",
            "success": True,
            "error": None,
            "result": bounded,
        }
        self.assertLess(len(json.dumps(envelope, ensure_ascii=False).encode("utf-8")), 96_000)
        self.assertIn("[truncated]", bounded["stdout"] + bounded["stderr"])


if __name__ == "__main__":
    unittest.main()
