from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "barrot-autonomous-resolver.yml"


class ResolverWorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")
        start = cls.text.index("      - name: Open issues for failing workflows")
        end = cls.text.index("      # -----------------------------------------------------------------------\n      # 2.", start)
        cls.failure_step = cls.text[start:end]

    def test_failure_scanner_uses_strict_shell_mode(self):
        self.assertIn("set -euo pipefail", self.failure_step)
        self.assertNotIn("set +e", self.failure_step)

    def test_failure_scan_uses_paginated_cutoff_helper(self):
        self.assertIn("scripts/list_recent_failed_workflows.py", self.failure_step)
        self.assertIn("--hours 24", self.failure_step)
        self.assertNotIn("gh run list", self.failure_step)

    def test_api_errors_are_not_collapsed_into_no_failures(self):
        self.assertNotIn("|| true", self.failure_step)
        self.assertNotIn("2>/dev/null || echo", self.failure_step)

    def test_issue_context_comes_from_same_filtered_run(self):
        self.assertIn("RUN_URL", self.failure_step)
        self.assertNotIn("URL unavailable", self.failure_step)


if __name__ == "__main__":
    unittest.main(verbosity=2)
