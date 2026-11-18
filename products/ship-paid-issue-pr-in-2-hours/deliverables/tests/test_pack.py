import unittest
from datetime import datetime, timezone

from paid_issue_kit.pack import (
    build_evidence_pack,
    build_pr_body,
    validate_evidence_plan,
    validate_pr_body,
)

GENERATED = datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc)


def plan(**overrides):
    base = {
        "issue_url": "https://github.com/example/project/issues/42",
        "summary": "Adds a retry wrapper to the upload command.",
        "change_bullets": [
            "Added retry_upload() with three attempts.",
            "Reused the existing backoff helper.",
        ],
        "why": "The upload command fails on the first transient network error.",
        "test_command": "python3 -m pytest tests/test_upload.py -q",
        "test_result": "12 passed in 0.41s",
        "risk": "Retries extend the worst-case runtime by two seconds.",
        "rollback": "Revert commit abc123 and the previous behaviour returns.",
        "checklist": [
            "Tests pass locally",
            "No unrelated files changed",
        ],
        "issue_id": "issue-42",
        "claims": [
            {
                "text": "The retry path is exercised by a test.",
                "evidence": "tests/test_upload.py::test_retry_on_timeout",
                "limit": "Only the timeout path is covered.",
            }
        ],
        "command": "python3 -m pytest tests/test_upload.py -q",
        "exit_code": 0,
        "output": "12 passed in 0.41s",
    }
    base.update(overrides)
    return base


class TestPrBody(unittest.TestCase):
    def test_builds_and_validates(self):
        body = build_pr_body(plan())
        self.assertEqual(validate_pr_body(body), [])
        self.assertIn("## Proof", body)
        self.assertIn("Command: `python3 -m pytest", body)

    def test_missing_plan_key_raises(self):
        data = plan()
        data.pop("rollback")
        with self.assertRaises(ValueError):
            build_pr_body(data)

    def test_empty_bullets_raise(self):
        with self.assertRaises(ValueError):
            build_pr_body(plan(change_bullets=[]))

    def test_missing_section_is_caught(self):
        body = build_pr_body(plan()).replace("## Risk and rollback", "## Notes")
        self.assertIn("missing section: ## Risk and rollback", validate_pr_body(body))

    def test_section_name_inside_prose_does_not_count(self):
        body = build_pr_body(plan()).replace(
            "## Proof", "The template asks for ## Proof here", 1
        )
        self.assertIn("missing section: ## Proof", validate_pr_body(body))

    def test_placeholder_is_caught(self):
        body = build_pr_body(plan(why="TODO explain the failure"))
        self.assertTrue(any("placeholder text present" in p for p in validate_pr_body(body)))

    def test_leftover_bracket_placeholder_is_caught(self):
        body = build_pr_body(plan(why="[one paragraph on the failure]"))
        self.assertTrue(
            any("placeholder bracket present" in p for p in validate_pr_body(body))
        )

    def test_banned_claim_is_caught(self):
        body = build_pr_body(plan(test_result="Guaranteed to pass everywhere"))
        self.assertTrue(any("guarantee language" in p for p in validate_pr_body(body)))

    def test_missing_issue_link_is_caught(self):
        body = build_pr_body(plan(issue_url="issue 42"))
        self.assertIn("no issue-specific link found", validate_pr_body(body))

    def test_missing_test_command_is_caught(self):
        body = build_pr_body(plan(test_command="looks fine", test_result="looks fine"))
        self.assertIn("no runnable test command found", validate_pr_body(body))

    def test_missing_result_is_caught(self):
        body = build_pr_body(plan()).replace("Result:", "Outcome:")
        self.assertIn("no test result found", validate_pr_body(body))

    def test_missing_rollback_is_caught(self):
        body = build_pr_body(plan()).replace("Rollback:", "Undo:")
        self.assertIn("no rollback statement found", validate_pr_body(body))

    def test_checked_items_required(self):
        body = build_pr_body(plan()).replace("- [x]", "- [ ]")
        self.assertIn("fewer than two checked checklist items", validate_pr_body(body))

    def test_short_body_is_caught(self):
        self.assertIn("pr body shorter than 200 characters", validate_pr_body("## What changed\n"))

    def test_empty_body_is_caught(self):
        self.assertEqual(validate_pr_body(""), ["pr body is empty"])

    def test_optional_note_is_rendered_as_comment(self):
        body = build_pr_body(plan(note="Synthetic example"))
        self.assertTrue(body.startswith("<!-- Synthetic example -->"))
        self.assertEqual(validate_pr_body(body), [])


class TestEvidencePack(unittest.TestCase):
    def test_builds_and_validates(self):
        text = build_evidence_pack(plan(), generated_at=GENERATED)
        self.assertEqual(validate_evidence_plan(plan()), [])
        self.assertIn("Exit code: 0", text)
        self.assertIn("Evidence: tests/test_upload.py", text)
        self.assertIn("Limit: Only the timeout path is covered.", text)
        self.assertIn("Generated: 2026-11-18T12:00:00Z", text)

    def test_non_url_issue_is_rejected(self):
        problems = validate_evidence_plan(plan(issue_url="issue 42"))
        self.assertIn("issue_url is not an http(s) URL", problems)

    def test_failing_exit_code_is_rejected(self):
        problems = validate_evidence_plan(plan(exit_code=1))
        self.assertIn("exit_code is not 0; a failing run cannot be presented as proof", problems)

    def test_missing_claim_is_rejected(self):
        self.assertIn("at least one claim is required", validate_evidence_plan(plan(claims=[])))

    def test_claim_without_limit_is_rejected(self):
        claims = [{"text": "The retry path is tested.", "evidence": "test_upload.py"}]
        self.assertIn("claim 1 missing limit", validate_evidence_plan(plan(claims=claims)))

    def test_short_claim_is_rejected(self):
        claims = [{"text": "Works", "evidence": "test", "limit": "one path"}]
        problems = validate_evidence_plan(plan(claims=claims))
        self.assertIn("claim 1 is shorter than 10 characters", problems)

    def test_banned_claim_is_rejected(self):
        claims = [
            {
                "text": "This change is bulletproof.",
                "evidence": "test_upload.py",
                "limit": "timeout only",
            }
        ]
        problems = validate_evidence_plan(plan(claims=claims))
        self.assertIn("claim 1: unverifiable bulletproof claim", problems)

    def test_empty_output_is_rejected(self):
        self.assertIn("command output is empty", validate_evidence_plan(plan(output="")))

    def test_build_rejects_bad_claim_shape(self):
        with self.assertRaises(ValueError):
            build_evidence_pack(plan(claims=["not-an-object"]))

    def test_build_rejects_non_integer_exit_code(self):
        with self.assertRaises(ValueError):
            build_evidence_pack(plan(exit_code="0"))


if __name__ == "__main__":
    unittest.main()
