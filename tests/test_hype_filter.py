"""Tests for the media hype filter.

Runs with the stdlib runner (``python -m unittest``) and under pytest.
No network, no model.  Two fixtures are real transcript excerpts; the rest are
minimal synthetic cases that isolate one check at a time.
"""

from __future__ import annotations

import json
import unittest

from barrot_agent.hype_filter import (
    HYPE_THRESHOLD,
    enforce_gate,
    is_media_kind,
    run_hype_filter,
)

# Real excerpt, Julia McCoy, us_pnC6ETNA (2026-11-15).
AGI_VIDEO = (
    "Using OpenAI's own setup, the one that lets the model keep its train of thought "
    "between steps, Astra scored 99.9%. On ARC's plain neutral setup where every model "
    "gets the exact same barebones environment, it scored 62.7%. ARC Prize says this "
    "isn't proof of AGI. So, I'm drawing the line right here. AGI is here. That's why I "
    "call it a psyop. It was built to make you afraid at the exact moment these groups "
    "wanted new laws. All three have gotten money through the same grant fund. The money "
    "behind it comes from an investor. So go check the scoreboard yourself, and grab my "
    "free guide while you're at it."
)

# Real excerpt, Better Stack, lNpDxKfBlf8 (2026-11-15).
MEMORY_VIDEO = (
    "I rented an H100 and put it to the test. The README example reproduced almost word "
    "for word, and the speed claim held up. With 512 documents the answering time stayed "
    "flat at 0.12 seconds, and counting the embedding step it answered in 3.2 seconds "
    "instead of 19.3. Then I built my own test on my own custom data, and it failed "
    "miserably. Memorilla hallucinated a shellfish allergy and got the birthday wrong. "
    "It answered 1 out of 8 plot questions. My tests were small and this is just a "
    "research project."
)


class CalibrationTests(unittest.TestCase):
    """The filter must sort the two real sources correctly."""

    def test_agi_video_is_hype(self):
        verdict = run_hype_filter(
            AGI_VIDEO, title="It's Official: We've Entered AGI", source="us_pnC6ETNA"
        )
        self.assertTrue(verdict.is_hype)
        self.assertEqual(verdict.tag, "HYPE")
        self.assertGreaterEqual(verdict.failures, HYPE_THRESHOLD)
        self.assertIn("benchmark_caveat", verdict.failed_names)
        self.assertIn("funding_vs_intent", verdict.failed_names)
        self.assertTrue(verdict.refinement_blocked)

    def test_memory_video_is_not_hype(self):
        verdict = run_hype_filter(
            MEMORY_VIDEO,
            title="Did Stanford Just Solve AI Memory? (Memorilla)",
            source="lNpDxKfBlf8",
        )
        self.assertFalse(verdict.is_hype)
        self.assertEqual(verdict.tag, "OK")
        self.assertEqual(verdict.failures, 0)
        self.assertFalse(verdict.refinement_blocked)


class BenchmarkCaveatTests(unittest.TestCase):
    def test_caveat_alone_passes(self):
        verdict = run_hype_filter(
            "The benchmark is narrow and this result is not proof of general intelligence."
        )
        check = verdict.get("benchmark_caveat")
        self.assertTrue(check.passed)

    def test_overclaim_alone_fails(self):
        verdict = run_hype_filter("AGI is here. The benchmark is complete.")
        check = verdict.get("benchmark_caveat")
        self.assertFalse(check.passed)
        self.assertIn("no benchmark caveat", check.reason)

    def test_caveat_quoted_then_overridden_fails(self):
        verdict = run_hype_filter(
            "ARC Prize says this isn't proof of AGI. I'm drawing the line here: AGI is here."
        )
        check = verdict.get("benchmark_caveat")
        self.assertFalse(check.passed)
        self.assertIn("overrides", check.reason)

    def test_scores_without_limitation_fail(self):
        verdict = run_hype_filter("The model scored 99.9% on the leaderboard.")
        check = verdict.get("benchmark_caveat")
        self.assertFalse(check.passed)
        self.assertIn("without any stated limitation", check.reason)

    def test_no_benchmark_is_not_applicable(self):
        verdict = run_hype_filter("I walked the dog and bought bread.")
        check = verdict.get("benchmark_caveat")
        self.assertFalse(check.applicable)
        self.assertIsNone(check.passed)
        self.assertFalse(check.failed)


class HarnessTests(unittest.TestCase):
    def test_score_without_harness_fails(self):
        verdict = run_hype_filter("Model X scored 99.9% on the benchmark.")
        check = verdict.get("harness_disclosure")
        self.assertFalse(check.passed)
        self.assertIn("without naming", check.reason)

    def test_named_harness_passes(self):
        verdict = run_hype_filter(
            "Model X scored 99.9% under the standard harness and 62.7% under the "
            "provider adapter."
        )
        check = verdict.get("harness_disclosure")
        self.assertTrue(check.passed)

    def test_own_test_setup_counts_as_disclosure(self):
        verdict = run_hype_filter(
            "I built my own test on custom data after the benchmark. "
            "The 512-document run took 3.2 seconds."
        )
        check = verdict.get("harness_disclosure")
        self.assertTrue(check.passed)

    def test_no_score_is_not_applicable(self):
        verdict = run_hype_filter("The demo looked fine.")
        self.assertFalse(verdict.get("harness_disclosure").applicable)


class CostBudgetTests(unittest.TestCase):
    def test_accuracy_only_fails(self):
        verdict = run_hype_filter("It is 40% more accurate than the previous model.")
        check = verdict.get("cost_and_budget")
        self.assertFalse(check.passed)
        self.assertIn("without cost", check.reason)

    def test_dollar_cost_passes(self):
        verdict = run_hype_filter("It is 40% more accurate and costs $26K per run.")
        self.assertTrue(verdict.get("cost_and_budget").passed)

    def test_token_budget_passes(self):
        verdict = run_hype_filter("Same score with 108x fewer tokens.")
        self.assertTrue(verdict.get("cost_and_budget").passed)

    def test_latency_passes(self):
        verdict = run_hype_filter(
            "It answered 6x faster, in 3.2 seconds instead of 19.3 seconds."
        )
        self.assertTrue(verdict.get("cost_and_budget").passed)


class FundingIntentTests(unittest.TestCase):
    def test_funding_fact_alone_passes(self):
        verdict = run_hype_filter("The group is funded by a grant from a known investor.")
        check = verdict.get("funding_vs_intent")
        self.assertTrue(check.passed)
        self.assertIn("no motive inferred", check.reason)

    def test_funding_plus_asserted_motive_fails(self):
        verdict = run_hype_filter(
            "The group is funded by a grant. It was built to make you afraid."
        )
        check = verdict.get("funding_vs_intent")
        self.assertFalse(check.passed)
        self.assertIn("asserted as fact", check.reason)

    def test_hedged_motive_passes(self):
        verdict = run_hype_filter(
            "The group is funded by a grant. The timing might be a psyop, but I can't prove it."
        )
        check = verdict.get("funding_vs_intent")
        self.assertTrue(check.passed)
        self.assertIn("hedged", check.reason)

    def test_no_funding_is_not_applicable(self):
        verdict = run_hype_filter("A benchmark showed a 3% gain.")
        self.assertFalse(verdict.get("funding_vs_intent").applicable)


class BeneficiaryTests(unittest.TestCase):
    def test_emotional_without_stake_fails(self):
        verdict = run_hype_filter("This terrifying nightmare will destroy everything.")
        check = verdict.get("beneficiary")
        self.assertFalse(check.passed)
        self.assertIn("no beneficiary", check.reason)

    def test_emotional_with_disclosed_stake_passes(self):
        verdict = run_hype_filter(
            "This terrifying nightmare will destroy everything. Get my free guide."
        )
        self.assertTrue(verdict.get("beneficiary").passed)

    def test_neutral_text_is_not_applicable(self):
        verdict = run_hype_filter("The run took 3.2 seconds on one H100.")
        self.assertFalse(verdict.get("beneficiary").applicable)


class ThresholdAndGateTests(unittest.TestCase):
    def test_one_failure_is_not_hype(self):
        # Only the beneficiary check applies, and it fails.
        verdict = run_hype_filter("This terrifying nightmare will destroy everything.")
        self.assertEqual(verdict.failures, 1)
        self.assertFalse(verdict.is_hype)
        self.assertIn("beneficiary", verdict.failed_names)

    def test_two_failures_are_hype(self):
        verdict = run_hype_filter(
            "This terrifying nightmare will destroy everything. AGI is here."
        )
        self.assertEqual(verdict.failures, 2)
        self.assertTrue(verdict.is_hype)

    def test_bare_score_fails_three_checks(self):
        # A score with no caveat, no harness and no cost is the classic hype shape.
        verdict = run_hype_filter("Model X scored 99.9% on the benchmark.")
        self.assertEqual(verdict.failures, 3)
        self.assertTrue(verdict.is_hype)

    def test_media_kinds(self):
        for kind in ("video", "youtube", "podcast", "ted", "ted_talk", "audiobook"):
            self.assertTrue(is_media_kind(kind), msg=kind)
        for kind in ("paper", "code", "repo", "news", ""):
            self.assertFalse(is_media_kind(kind), msg=kind)

    def test_gate_skips_non_media(self):
        self.assertIsNone(
            enforce_gate(kind="paper", text=AGI_VIDEO, title="", source="")
        )

    def test_gate_blocks_media_hype(self):
        verdict = enforce_gate(kind="podcast", text=AGI_VIDEO, source="us_pnC6ETNA")
        self.assertIsNotNone(verdict)
        self.assertTrue(verdict.refinement_blocked)

    def test_empty_media_transcript_is_rejected(self):
        with self.assertRaises(ValueError):
            run_hype_filter("   ", kind="video")

    def test_empty_non_media_text_is_allowed(self):
        verdict = run_hype_filter("", kind="paper")
        self.assertFalse(verdict.is_hype)


class SerialisationTests(unittest.TestCase):
    def test_json_roundtrip(self):
        verdict = run_hype_filter(AGI_VIDEO, title="AGI", source="us_pnC6ETNA")
        payload = json.dumps(verdict.to_dict())
        loaded = json.loads(payload)
        self.assertEqual(loaded["tag"], "HYPE")
        self.assertEqual(loaded["failures"], verdict.failures)
        self.assertEqual(len(loaded["checks"]), 5)
        self.assertTrue(loaded["refinement_blocked"])

    def test_summary_names_failed_checks(self):
        verdict = run_hype_filter(AGI_VIDEO, source="us_pnC6ETNA")
        summary = verdict.summary()
        self.assertIn("HYPE", summary)
        self.assertIn("benchmark_caveat", summary)

    def test_deterministic(self):
        first = run_hype_filter(AGI_VIDEO, source="x").to_dict()
        second = run_hype_filter(AGI_VIDEO, source="x").to_dict()
        self.assertEqual(first, second)

    def test_evidence_is_returned(self):
        verdict = run_hype_filter(AGI_VIDEO, source="us_pnC6ETNA")
        check = verdict.get("funding_vs_intent")
        self.assertTrue(check.evidence)
        self.assertTrue(any("psyop" in span for span in check.evidence))


if __name__ == "__main__":
    unittest.main()
