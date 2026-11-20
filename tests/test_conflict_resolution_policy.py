import unittest

from barrot_agent.ingestion.conflict_resolution_policy import (
    ConflictEvidence,
    ResolutionChoice,
    decision_as_dict,
    recommend_resolution,
)


class ConflictResolutionPolicyTests(unittest.TestCase):
    def test_incoming_is_not_automatic_without_evidence(self):
        decision = recommend_resolution(ConflictEvidence())
        self.assertEqual(decision.choice, ResolutionChoice.MANUAL)
        self.assertFalse(decision.auto_apply)
        self.assertEqual(decision.confidence, 0.0)

    def test_validated_intended_incoming_change_is_recommended(self):
        evidence = ConflictEvidence(
            incoming_is_intended_pr_change=True,
            incoming_preserves_current_behavior=True,
            incoming_is_validated=True,
            tests_pass=True,
            protected_area_reviewed=True,
        )
        decision = recommend_resolution(evidence)
        self.assertEqual(decision.choice, ResolutionChoice.INCOMING)
        self.assertFalse(decision.auto_apply)

    def test_both_requires_compatibility_and_validation(self):
        evidence = ConflictEvidence(
            both_changes_are_required=True,
            both_changes_are_compatible=True,
            composition_is_validated=True,
            tests_pass=True,
            protected_area_reviewed=True,
        )
        decision = recommend_resolution(evidence)
        self.assertEqual(decision.choice, ResolutionChoice.BOTH)
        self.assertFalse(decision.auto_apply)

    def test_security_and_delete_modify_always_escalate(self):
        for kind in ("security", "delete_modify", "workflow", "binary"):
            with self.subTest(kind=kind):
                evidence = ConflictEvidence(
                    conflict_type=kind,
                    incoming_is_intended_pr_change=True,
                    incoming_preserves_current_behavior=True,
                    incoming_is_validated=True,
                    tests_pass=True,
                    protected_area_reviewed=True,
                )
                decision = recommend_resolution(evidence)
                self.assertEqual(decision.choice, ResolutionChoice.MANUAL)
                self.assertFalse(decision.auto_apply)

    def test_current_only_when_authoritative_and_incoming_invalid(self):
        evidence = ConflictEvidence(
            current_is_authoritative=True,
            incoming_is_superseded_or_invalid=True,
        )
        self.assertEqual(recommend_resolution(evidence).choice, ResolutionChoice.CURRENT)

    def test_both_sides_required_but_unvalidated_stops(self):
        evidence = ConflictEvidence(
            both_changes_are_required=True,
            both_changes_are_compatible=True,
            tests_pass=True,
            protected_area_reviewed=True,
        )
        self.assertEqual(recommend_resolution(evidence).choice, ResolutionChoice.MANUAL)

    def test_decision_payload_is_auditable(self):
        payload = decision_as_dict(ConflictEvidence())
        self.assertEqual(payload["choice"], "manual")
        self.assertIn("evidence", payload)
        self.assertIn("required_checks", payload)
        self.assertFalse(payload["auto_apply"])
        self.assertEqual(payload["confidence"], 0.0)


if __name__ == "__main__":
    unittest.main()
