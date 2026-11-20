import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from barrot_agent.ingestion.conflict_resolution_policy import (
    ConflictEvidence, ResolutionChoice, recommend_resolution,
)


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=check,
        env={**os.environ, "GIT_AUTHOR_NAME": "Barrot conflict test",
             "GIT_AUTHOR_EMAIL": "barrot-test@example.invalid",
             "GIT_COMMITTER_NAME": "Barrot conflict test",
             "GIT_COMMITTER_EMAIL": "barrot-test@example.invalid"},
    )


class GitConflictResolutionIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.name", "Barrot conflict test")
        git(self.repo, "config", "user.email", "barrot-test@example.invalid")

    def tearDown(self):
        self.temp.cleanup()

    def commit_file(self, path: str, content: str, message: str):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        git(self.repo, "add", path)
        git(self.repo, "commit", "-m", message)

    def test_real_git_content_conflict_fails_closed(self):
        self.commit_file("app/value.py", "VALUE = 'base'\n", "base")
        git(self.repo, "checkout", "-b", "incoming")
        self.commit_file("app/value.py", "VALUE = 'incoming'\n", "incoming")
        git(self.repo, "checkout", "main")
        self.commit_file("app/value.py", "VALUE = 'current'\n", "current")
        merge = git(self.repo, "merge", "incoming", "--no-edit", check=False)
        self.assertNotEqual(merge.returncode, 0)
        self.assertIn("<<<<<<<", (self.repo / "app/value.py").read_text(encoding="utf-8"))
        decision = recommend_resolution(ConflictEvidence(file_path="app/value.py"))
        self.assertEqual(decision.choice, ResolutionChoice.MANUAL)
        self.assertFalse(decision.auto_apply)

    def test_real_git_clean_merge_preserves_both_disjoint_changes(self):
        base = "def left():\n    return 1\n" + ("\n" * 8) + "def right():\n    return 2\n"
        incoming = "def left():\n    return 10\n" + ("\n" * 8) + "def right():\n    return 2\n"
        current = "def left():\n    return 1\n" + ("\n" * 8) + "def right():\n    return 20\n"
        self.commit_file("app/module.py", base, "base")
        git(self.repo, "checkout", "-b", "incoming")
        self.commit_file("app/module.py", incoming, "incoming")
        git(self.repo, "checkout", "main")
        self.commit_file("app/module.py", current, "current")
        merge = git(self.repo, "merge", "incoming", "--no-edit", check=False)
        self.assertEqual(merge.returncode, 0, merge.stderr)
        merged = (self.repo / "app/module.py").read_text(encoding="utf-8")
        self.assertIn("return 10", merged)
        self.assertIn("return 20", merged)
        decision = recommend_resolution(ConflictEvidence(
            both_changes_are_required=True, both_changes_are_compatible=True,
            composition_is_validated=True, tests_pass=True, protected_area_reviewed=True,
        ))
        self.assertEqual(decision.choice, ResolutionChoice.BOTH)
        self.assertFalse(decision.auto_apply)

    def test_duplicate_function_conflict_is_not_accept_both_by_default(self):
        self.commit_file("app/functions.py", "def calculate(value):\n    return value\n", "base")
        git(self.repo, "checkout", "-b", "incoming")
        self.commit_file("app/functions.py", "def calculate(value):\n    return value * 2\n", "incoming")
        git(self.repo, "checkout", "main")
        self.commit_file("app/functions.py", "def calculate(value):\n    return value + 2\n", "current")
        merge = git(self.repo, "merge", "incoming", "--no-edit", check=False)
        self.assertNotEqual(merge.returncode, 0)
        self.assertIn("<<<<<<<", (self.repo / "app/functions.py").read_text(encoding="utf-8"))
        self.assertEqual(recommend_resolution(ConflictEvidence()).choice, ResolutionChoice.MANUAL)

    def test_workflow_and_secret_paths_always_escalate(self):
        for path in (".github/workflows/ci.yml", "secrets/provider.json"):
            decision = recommend_resolution(ConflictEvidence(
                file_path=path, incoming_is_intended_pr_change=True,
                incoming_preserves_current_behavior=True, incoming_is_validated=True,
                tests_pass=True, protected_area_reviewed=True,
            ))
            self.assertEqual(decision.choice, ResolutionChoice.MANUAL)
            self.assertFalse(decision.auto_apply)

    def test_outdated_incoming_and_failed_tests_never_auto_apply(self):
        outdated = recommend_resolution(ConflictEvidence(
            current_is_authoritative=True, incoming_is_superseded_or_invalid=True,
        ))
        failing = recommend_resolution(ConflictEvidence(
            incoming_is_intended_pr_change=True, incoming_preserves_current_behavior=True,
            incoming_is_validated=True, tests_pass=False, protected_area_reviewed=True,
        ))
        self.assertEqual(outdated.choice, ResolutionChoice.CURRENT)
        self.assertEqual(failing.choice, ResolutionChoice.MANUAL)
        self.assertFalse(outdated.auto_apply)
        self.assertFalse(failing.auto_apply)


if __name__ == "__main__":
    unittest.main()
