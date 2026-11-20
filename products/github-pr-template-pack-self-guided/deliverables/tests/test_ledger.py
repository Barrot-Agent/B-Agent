import unittest
from datetime import datetime, timezone

from paid_issue_kit.ledger import Candidate, Policy, audit, evaluate, summarize, to_csv

NOW = datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc)


def candidate(**overrides):
    base = {
        "issue_id": "issue-1",
        "url": "https://github.com/example/project/issues/42",
        "repo": "example/project",
        "title": "Add retry to the upload command",
        "amount_usd": 500,
        "acceptance_criteria": "Upload retries three times and prints the final error.",
        "repo_stars": 120,
        "repo_pushed_at": "2026-11-10T00:00:00Z",
        "labels": ["bounty"],
        "effort_hours": 2,
    }
    base.update(overrides)
    return Candidate.from_dict(base)


class TestEvaluate(unittest.TestCase):
    def test_valid_candidate_is_go(self):
        verdict = evaluate(candidate(), now=NOW)
        self.assertEqual(verdict.decision, "GO")
        self.assertEqual(verdict.reasons, [])
        self.assertAlmostEqual(verdict.effective_hourly_usd, 250.0)

    def test_missing_amount_is_no_go(self):
        verdict = evaluate(candidate(amount_usd=None), now=NOW)
        self.assertEqual(verdict.decision, "NO-GO")
        self.assertIn("no stated amount", verdict.reasons)

    def test_amount_below_floor(self):
        verdict = evaluate(candidate(amount_usd=20), now=NOW)
        self.assertIn("amount below 50 USD", verdict.reasons)

    def test_amount_above_cap(self):
        verdict = evaluate(candidate(amount_usd=90_000), now=NOW)
        self.assertIn("amount above 50000 USD cap", verdict.reasons)

    def test_short_acceptance_criteria(self):
        verdict = evaluate(candidate(acceptance_criteria="make it work"), now=NOW)
        self.assertIn("acceptance criteria missing or too short", verdict.reasons)

    def test_archived_repository(self):
        verdict = evaluate(candidate(archived=True), now=NOW)
        self.assertIn("repository archived", verdict.reasons)

    def test_low_stars(self):
        verdict = evaluate(candidate(repo_stars=3), now=NOW)
        self.assertIn("repository has fewer than 20 stars", verdict.reasons)

    def test_stale_repository(self):
        verdict = evaluate(candidate(repo_pushed_at="2026-01-01T00:00:00Z"), now=NOW)
        self.assertTrue(any("idle for more than 120 days" in r for r in verdict.reasons))

    def test_invalid_repo_date(self):
        verdict = evaluate(candidate(repo_pushed_at="not-a-date"), now=NOW)
        self.assertIn("repo_pushed_at is not a valid ISO date", verdict.reasons)

    def test_spam_title(self):
        verdict = evaluate(candidate(title="[BOUNTY] answer this survey"), now=NOW)
        self.assertIn("spam marker in title", verdict.reasons)

    def test_zero_effort(self):
        verdict = evaluate(candidate(effort_hours=0), now=NOW)
        self.assertIn("effort_hours must be greater than zero", verdict.reasons)

    def test_effort_above_cap(self):
        verdict = evaluate(candidate(effort_hours=40), now=NOW)
        self.assertIn("effort above 3 hour cap", verdict.reasons)

    def test_fee_and_expenses_reduce_payout(self):
        verdict = evaluate(
            candidate(
                amount_usd=500, effort_hours=2,
                payout_fee_fraction=0.1, expenses_usd=20,
            ),
            now=NOW,
        )
        self.assertAlmostEqual(verdict.effective_payout_usd, 430.0)
        self.assertAlmostEqual(verdict.effective_hourly_usd, 215.0)

    def test_low_effective_rate_blocks(self):
        verdict = evaluate(candidate(amount_usd=100, effort_hours=10), now=NOW)
        self.assertIn("effective rate below 30 USD/hour", verdict.reasons)

    def test_escrow_confidence_is_highest(self):
        self.assertEqual(evaluate(candidate(escrow_verified=True), now=NOW).confidence, 1.0)
        self.assertEqual(evaluate(candidate(platform="opire"), now=NOW).confidence, 0.9)
        self.assertEqual(evaluate(candidate(labels=[]), now=NOW).confidence, 0.7)

    def test_policy_override(self):
        strict = Policy(min_effective_hourly_usd=300)
        self.assertEqual(evaluate(candidate(), strict, now=NOW).decision, "NO-GO")


class TestAuditAndCsv(unittest.TestCase):
    def test_go_rows_sort_first(self):
        good = candidate()
        bad = candidate(issue_id="issue-0", amount_usd=None)
        verdicts = audit([bad, good], now=NOW)
        self.assertEqual([v.candidate.issue_id for v in verdicts], ["issue-1", "issue-0"])

    def test_summary_counts(self):
        verdicts = audit([candidate(), candidate(issue_id="issue-2", amount_usd=None)], now=NOW)
        summary = summarize(verdicts)
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["go"], 1)
        self.assertEqual(summary["no_go"], 1)
        self.assertEqual(summary["go_issue_ids"], ["issue-1"])
        self.assertAlmostEqual(summary["best_go_hourly_usd"], 250.0)

    def test_csv_has_header_and_rows(self):
        text = to_csv(audit([candidate()], now=NOW))
        lines = text.strip().splitlines()
        self.assertIn("decision", lines[0])
        self.assertIn("effective_hourly_usd", lines[0])
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[1].startswith("GO,"))

    def test_accepts_dicts(self):
        verdicts = audit(
            [
                {
                    "issue_id": "dict-1",
                    "url": "https://github.com/example/project/issues/1",
                    "repo": "example/project",
                    "title": "Fix a typo in the CLI help",
                    "amount_usd": 100,
                    "acceptance_criteria": "Help text shows the correct flag name.",
                    "repo_stars": 50,
                    "repo_pushed_at": "2026-11-01T00:00:00Z",
                    "effort_hours": 2,
                }
            ],
            now=NOW,
        )
        self.assertEqual(verdicts[0].decision, "GO")


class TestCandidateValidation(unittest.TestCase):
    def test_missing_field(self):
        with self.assertRaises(ValueError):
            Candidate.from_dict({"issue_id": "x"})

    def test_bool_is_not_a_number(self):
        with self.assertRaises(ValueError):
            candidate(amount_usd=True)

    def test_bad_boolean(self):
        with self.assertRaises(ValueError):
            candidate(archived="yes")

    def test_bad_integer(self):
        with self.assertRaises(ValueError):
            candidate(repo_stars=1.5)


if __name__ == "__main__":
    unittest.main()
