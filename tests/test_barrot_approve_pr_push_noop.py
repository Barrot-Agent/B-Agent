from pathlib import Path
import unittest

WORKFLOW = Path(".github/workflows/barrot-approve-pr.yml").read_text(encoding="utf-8")


class TestBarrotApprovalWorkflowPushNoop(unittest.TestCase):
    def test_event_key_is_quoted_and_push_is_explicit(self):
        self.assertIn('"on":', WORKFLOW)
        self.assertIn("  push:", WORKFLOW)
        self.assertIn('      - "**"', WORKFLOW)

    def test_push_job_has_no_permissions_or_approval_secrets(self):
        block = WORKFLOW.split("  push-noop:", 1)[1].split("\n  approve:", 1)[0]
        self.assertIn("if: github.event_name == 'push'", block)
        self.assertIn("permissions: {}", block)
        self.assertNotIn("secrets.", block)
        self.assertNotIn("gh api", block)
        self.assertNotIn("gh pr", block)

    def test_approval_job_is_manual_only_and_least_privilege(self):
        block = WORKFLOW.split("  approve:", 1)[1]
        self.assertIn("if: github.event_name == 'workflow_dispatch'", block)
        self.assertIn("pull-requests: write", block)
        self.assertIn("EXPECTED_HEAD_SHA", block)
        self.assertIn("APPROVAL_REASON", block)
        self.assertNotIn("contents: write", WORKFLOW)
        self.assertNotIn("gh pr merge", WORKFLOW)

    def test_manual_approval_still_requires_head_sha_and_reason(self):
        self.assertIn("expected_head_sha:", WORKFLOW)
        self.assertIn("reason:", WORKFLOW)
        self.assertIn('"$head_sha" != "$EXPECTED_HEAD_SHA"', WORKFLOW)
        self.assertIn('if [[ -z "$APPROVAL_REASON" ]]', WORKFLOW)


if __name__ == "__main__":
    unittest.main()
