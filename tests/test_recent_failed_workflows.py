import unittest
from datetime import datetime, timezone

from scripts.list_recent_failed_workflows import ScanError, flatten_pages, select_latest_failures

UTC = timezone.utc
NOW = datetime(2026, 10, 26, 5, 4, 20, tzinfo=UTC)
CUTOFF = datetime(2026, 10, 25, 5, 4, 20, tzinfo=UTC)


def run(run_id, name, created, conclusion, url=None):
    return {
        "id": run_id, "name": name, "created_at": created,
        "conclusion": conclusion,
        "html_url": url or f"https://github.com/Barrot-Agent/B-Agent/actions/runs/{run_id}",
    }


class RecentFailureTests(unittest.TestCase):
    def test_latest_failed_run_inside_window_is_reported(self):
        rows = [run(1, "CI", "2026-10-26T04:00:00Z", "failure")]
        out = select_latest_failures(rows, cutoff=CUTOFF, now=NOW)
        self.assertEqual([x["workflow_name"] for x in out], ["CI"])

    def test_older_failure_is_ignored(self):
        rows = [run(1, "CI", "2026-10-25T04:00:00Z", "failure")]
        self.assertEqual(select_latest_failures(rows, cutoff=CUTOFF, now=NOW), [])

    def test_later_success_suppresses_earlier_failure(self):
        rows = [
            run(1, "CI", "2026-10-26T02:00:00Z", "failure"),
            run(2, "CI", "2026-10-26T03:00:00Z", "success"),
        ]
        self.assertEqual(select_latest_failures(rows, cutoff=CUTOFF, now=NOW), [])

    def test_latest_failure_suppresses_prior_success(self):
        rows = [
            run(1, "CI", "2026-10-26T02:00:00Z", "success"),
            run(2, "CI", "2026-10-26T03:00:00Z", "failure"),
        ]
        self.assertEqual(len(select_latest_failures(rows, cutoff=CUTOFF, now=NOW)), 1)

    def test_multiple_workflows_sorted_deterministically(self):
        rows = [
            run(1, "Zeta", "2026-10-26T02:00:00Z", "failure"),
            run(2, "Alpha", "2026-10-26T02:01:00Z", "failure"),
        ]
        out = select_latest_failures(rows, cutoff=CUTOFF, now=NOW)
        self.assertEqual([x["workflow_name"] for x in out], ["Alpha", "Zeta"])

    def test_cutoff_is_inclusive(self):
        rows = [run(1, "CI", "2026-10-25T05:04:20Z", "failure")]
        self.assertEqual(len(select_latest_failures(rows, cutoff=CUTOFF, now=NOW)), 1)

    def test_naive_timestamp_fails_closed(self):
        with self.assertRaises(ScanError):
            select_latest_failures(
                [run(1, "CI", "2026-10-26T04:00:00", "failure")],
                cutoff=CUTOFF, now=NOW,
            )

    def test_invalid_timestamp_fails_closed(self):
        with self.assertRaises(ScanError):
            select_latest_failures([run(1, "CI", "not-a-time", "failure")], cutoff=CUTOFF, now=NOW)

    def test_future_timestamp_fails_closed(self):
        with self.assertRaises(ScanError):
            select_latest_failures([run(1, "CI", "2026-10-26T05:10:00Z", "failure")], cutoff=CUTOFF, now=NOW)

    def test_missing_run_url_fails_closed(self):
        with self.assertRaises(ScanError):
            select_latest_failures(
                [{"id": 1, "name": "CI", "created_at": "2026-10-26T04:00:00Z", "conclusion": "failure"}],
                cutoff=CUTOFF, now=NOW,
            )

    def test_page_count_mismatch_fails_closed(self):
        pages = [{"total_count": 2, "workflow_runs": [run(1, "CI", "2026-10-26T04:00:00Z", "failure")]}]
        with self.assertRaises(ScanError):
            flatten_pages(pages)

    def test_duplicate_run_ids_fail_closed(self):
        row = run(1, "CI", "2026-10-26T04:00:00Z", "failure")
        with self.assertRaises(ScanError):
            flatten_pages([{"total_count": 2, "workflow_runs": [row, row]}])

    def test_empty_failure_list_only_after_complete_scan(self):
        rows = [run(1, "CI", "2026-10-26T04:00:00Z", "success")]
        self.assertEqual(select_latest_failures(rows, cutoff=CUTOFF, now=NOW), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
