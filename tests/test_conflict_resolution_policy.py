import unittest

from barrot_agent.ingestion.conflict_resolution_policy import (
    ConflictEvidence, ResolutionChoice, decision_as_dict, recommend_resolution,
)


class ConflictResolutionPolicyTests(unittest.TestCase):
    def test_missing_evidence_fails_closed(self):
        decision = recommend_resolution(ConflictEvidence())
        self.assertEqual(decision.choice, ResolutionChoice.MANUAL)
        self.assertFalse(decision.auto_apply)

    def test_validated_incoming_is_recommended_but_never_auto_applied(self):
        decision = recommend_resolution(ConflictEvidence(
            incoming_is_intended_pr_change=True,
            incoming_preserves_current_behavior=True,
            incoming_is_validated=True,
            tests_pass=True,
            protected_area_reviewed=True,
        ))
        self.assertEqual(decision.choice, ResolutionChoice.INCOMING)
        self.assertFalse(decision.auto_apply)

    def test_both_requires_compatibility_and_validation(self):
        decision = recommend_resolution(ConflictEvidence(
            both_changes_are_required=True,
            both_changes_are_compatible=True,
            composition_is_validated=True,
            tests_pass=True,
            protected_area_reviewed=True,
        ))
        self.assertEqual(decision.choice, ResolutionChoice.BOTH)
        self.assertFalse(decision.auto_apply)

    def test_high_risk_types_always_escalate(self):
        for kind in ("security", "delete_modify", "delete/modify", "workflow", "binary"):
            with self.subTest(kind=kind):
                decision = recommend_resolution(ConflictEvidence(
                    conflict_type=kind,
                    incoming_is_intended_pr_change=True,
                    incoming_preserves_current_behavior=True,
                    incoming_is_validated=True,
                    tests_pass=True,
                    protected_area_reviewed=True,
                ))
                self.assertEqual(decision.choice, ResolutionChoice.MANUAL)
                self.assertFalse(decision.auto_apply)

    def test_high_risk_paths_always_escalate(self):
        for path in (".github/workflows/ci.yml", ".github/CODEOWNERS",
                     "secrets/provider.json", "migrations/001.sql",
                     "package-lock.json", ".env.production", "src/auth.py",
                     "config/permissions.json"):
            with self.subTest(path=path):
                decision = recommend_resolution(ConflictEvidence(
                    file_path=path,
                    incoming_is_intended_pr_change=True,
                    incoming_preserves_current_behavior=True,
                    incoming_is_validated=True,
                    tests_pass=True,
                    protected_area_reviewed=True,
                ))
                self.assertEqual(decision.choice, ResolutionChoice.MANUAL)
                self.assertFalse(decision.auto_apply)

    def test_current_only_when_authoritative_and_incoming_invalid(self):
        decision = recommend_resolution(ConflictEvidence(
            current_is_authoritative=True,
            incoming_is_superseded_or_invalid=True,
        ))
        self.assertEqual(decision.choice, ResolutionChoice.CURRENT)
        self.assertFalse(decision.auto_apply)

    def test_failed_tests_block_incoming_and_both(self):
        incoming = recommend_resolution(ConflictEvidence(
            incoming_is_intended_pr_change=True,
            incoming_preserves_current_behavior=True,
            incoming_is_validated=True,
            tests_pass=False,
            protected_area_reviewed=True,
        ))
        both = recommend_resolution(ConflictEvidence(
            both_changes_are_required=True,
            both_changes_are_compatible=True,
            composition_is_validated=True,
            tests_pass=False,
            protected_area_reviewed=True,
        ))
        self.assertEqual(incoming.choice, ResolutionChoice.MANUAL)
        self.assertEqual(both.choice, ResolutionChoice.MANUAL)

    def test_both_sides_required_but_unvalidated_stops(self):
        decision = recommend_resolution(ConflictEvidence(
            both_changes_are_required=True,
            both_changes_are_compatible=True,
            tests_pass=True,
            protected_area_reviewed=True,
        ))
        self.assertEqual(decision.choice, ResolutionChoice.MANUAL)

    def test_decision_payload_is_auditable_and_never_authorizes_application(self):
        payload = decision_as_dict(ConflictEvidence())
        self.assertEqual(payload["choice"], "manual")
        self.assertFalse(payload["auto_apply"])
        self.assertIn("evidence", payload)
        self.assertIn("required_checks", payload)


