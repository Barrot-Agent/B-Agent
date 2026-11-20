"""Real Git integration tests for Barrot's fail-closed conflict boundary."""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from barrot_agent.ingestion.merge_conflict_micro_ingestion import MergeConflictMicroIngestion


@unittest.skipUnless(shutil.which("git"), "Git is required for merge integration tests")
class GitConflictIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Barrot Conflict Test")
        self.git("config", "user.email", "barrot-conflict-test@example.invalid")
        (self.repo / "app.py").write_text('VALUE = "base"\n', encoding="utf-8")
        self.git("add", "app.py")
        self.git("commit", "-q", "-m", "base")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()

    def tearDown(self):
        self.temp_dir.cleanup()

    def git(self, *args):
        return subprocess.run(
            ["git", *args],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )

    def commit_file(self, path, content, message):
        (self.repo / path).write_text(content, encoding="utf-8")
        self.git("add", path)
        result = self.git("commit", "-q", "-m", message)
        self.assertEqual(result.returncode, 0, result.stderr)

    def make_conflicting_branches(self):
        self.git("checkout", "-q", "-b", "incoming")
        self.commit_file("app.py", 'VALUE = "incoming"\n', "incoming change")
        incoming = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("checkout", "-q", "main")
        self.commit_file("app.py", 'VALUE = "current"\n', "current change")
        current = self.git("rev-parse", "HEAD").stdout.strip()
        return current, incoming

    def test_independent_changes_merge_cleanly(self):
        self.commit_file("current.py", 'CURRENT = True\n', "current side")
        current = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("checkout", "-q", "-b", "incoming", self.base)
        self.commit_file("incoming.py", 'INCOMING = True\n', "incoming side")
        incoming = self.git("rev-parse", "HEAD").stdout.strip()
        result = self.git("merge-tree", "--write-tree", current, incoming)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_incompatible_same_line_edits_are_reported_as_conflict(self):
        current, incoming = self.make_conflicting_branches()
        result = self.git("merge-tree", "--write-tree", current, incoming)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CONFLICT", result.stdout + result.stderr)

    def test_actual_git_merge_preserves_conflict_markers_for_review(self):
        self.make_conflicting_branches()
        self.git("checkout", "-q", "incoming")
        result = self.git("merge", "--no-edit", "main")
        self.assertNotEqual(result.returncode, 0)
        conflicted = (self.repo / "app.py").read_text(encoding="utf-8")
        self.assertIn("<<<<<<<", conflicted)
        self.assertIn("=======", conflicted)
        self.assertIn(">>>>>>>", conflicted)
        self.assertTrue(self.git("ls-files", "-u").stdout.strip())

    def test_merge_tree_check_does_not_move_checked_out_head(self):
        current, incoming = self.make_conflicting_branches()
        before = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("merge-tree", "--write-tree", current, incoming)
        after = self.git("rev-parse", "HEAD").stdout.strip()
        self.assertEqual(before, after)

    def test_legacy_analyzer_never_turns_markers_into_auto_resolution(self):
        analyzer = MergeConflictMicroIngestion()
        analyzer.initialize_knowledge_base()
        analysis = analyzer.analyze_conflict(
            '<<<<<<< HEAD\nVALUE = "current"\n=======\nVALUE = "incoming"\n>>>>>>> topic\n',
            "src/app.py",
        )
        self.assertFalse(analysis["auto_resolvable"])
        self.assertTrue(analysis["manual_review_required"])
        self.assertIsNone(analysis["recommended_technique"])
        self.assertEqual(analysis["policy_decision"]["choice"], "manual")
        self.assertFalse(analysis["policy_decision"]["auto_apply"])


if __name__ == "__main__":
    unittest.main()
