import unittest

from barrot_agent.ingestion.conflict_resolution_policy import ConflictEvidence
from barrot_agent.ingestion.merge_conflict_micro_ingestion import MergeConflictMicroIngestion


class LegacyConflictAnalyzerGateTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = MergeConflictMicroIngestion()
        self.analyzer.initialize_knowledge_base()

    def test_legacy_analyzer_defaults_to_manual_review(self):
        conflict = "<<<<<<< HEAD\nvalue = 'current'\n=======\nvalue = 'incoming'\n>>>>>>> feature"
        result = self.analyzer.analyze_conflict(conflict, "app/module.py")
        self.assertEqual(result["recommended_choice"], "manual")
        self.assertIsNone(result["recommended_technique"])
        self.assertFalse(result["auto_resolvable"])
        self.assertTrue(result["requires_human_review"])
        self.assertFalse(result["resolution_decision"]["auto_apply"])

    def test_legacy_strategy_lookup_without_evidence_returns_none(self):
        self.assertIsNone(self.analyzer.get_recommended_strategy("content", "app/module.py"))

    def test_legacy_patterns_never_claim_automatic_resolution(self):
        self.assertTrue(self.analyzer.conflict_patterns)
        self.assertFalse(any(pattern.auto_resolvable for pattern in self.analyzer.conflict_patterns))

    def test_validated_both_choice_remains_advisory_only(self):
        conflict = "<<<<<<< HEAD\nvalue = 'current'\n=======\nvalue = 'incoming'\n>>>>>>> feature"
        evidence = ConflictEvidence(
            both_changes_are_required=True,
            both_changes_are_compatible=True,
            composition_is_validated=True,
            tests_pass=True,
            protected_area_reviewed=True,
        )
        result = self.analyzer.analyze_conflict(conflict, "app/module.py", evidence)
        self.assertEqual(result["recommended_choice"], "both")
        self.assertFalse(result["auto_resolvable"])
        self.assertTrue(result["requires_human_review"])
        self.assertIsNone(result["recommended_technique"]["success_rate"])
        self.assertEqual(result["recommended_technique"]["success_rate_status"], "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
