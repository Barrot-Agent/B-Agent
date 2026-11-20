from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from barrot_agent.reverse_engineering.curriculum import (
    ANALYSIS_POLICY,
    CURRICULUM_ID,
    SOURCES,
    seed_reverse_engineering_curriculum,
)
from barrot_agent.sources.source_acquisition import SourceAcquisitionPlanner


class ReverseEngineeringCurriculumTests(unittest.TestCase):
    def test_seed_registers_all_curriculum_targets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            planner = SourceAcquisitionPlanner(Path(directory) / "targets.json")
            result = seed_reverse_engineering_curriculum(planner)

            self.assertEqual(result["targets_registered"], len(SOURCES))
            self.assertEqual(result["new_targets_added"], len(SOURCES))
            self.assertEqual(len(planner.list_targets()), len(SOURCES))
            self.assertGreaterEqual(len(planner.list_needs()), 10)

    def test_seed_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            planner = SourceAcquisitionPlanner(Path(directory) / "targets.json")
            first = seed_reverse_engineering_curriculum(planner)
            second = seed_reverse_engineering_curriculum(planner)

            self.assertEqual(first["new_targets_added"], len(SOURCES))
            self.assertEqual(second["new_targets_added"], 0)
            self.assertEqual(len(planner.list_targets()), len(SOURCES))

    def test_targets_require_provenance_and_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            planner = SourceAcquisitionPlanner(Path(directory) / "targets.json")
            seed_reverse_engineering_curriculum(planner)

            for target in planner.list_targets():
                self.assertTrue(target.mmi_required)
                self.assertTrue(target.independent_corroboration_required)
                self.assertTrue(target.provenance_requirements)
                self.assertTrue(target.verification_requirements)
                self.assertTrue(target.discovery_uri)
                self.assertTrue(target.publisher)

    def test_analysis_policy_defaults_to_safe_handling(self) -> None:
        self.assertTrue(ANALYSIS_POLICY["authorized_scope_only"])
        self.assertEqual(ANALYSIS_POLICY["default_sample_handling"], "static_analysis_only")
        self.assertTrue(ANALYSIS_POLICY["dynamic_analysis_requires_isolated_sandbox"])
        self.assertEqual(CURRICULUM_ID, "barrot-reverse-engineering")


if __name__ == "__main__":
    unittest.main()
