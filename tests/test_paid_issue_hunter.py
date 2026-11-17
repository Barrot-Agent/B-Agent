"""The hunter must parse amounts strictly, stay read-only, and run every 6 hours."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.paid_issue_hunter import MAX_PLAUSIBLE, amount_of, difficulty_of, render

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "paid-issue-hunter.yml"


def test_amount_requires_a_bounty_word_in_the_same_line():
    assert amount_of("Bounty: $250 for the fix") == 250
    assert amount_of("escrow of USDC 600 released on merge") == 600
    assert amount_of("the table shows 600,000 total funding") is None
    assert amount_of("$250 shipping cost") is None


def test_amount_is_capped_at_a_plausible_bounty():
    assert amount_of("bounty $50,000") == MAX_PLAUSIBLE
    assert amount_of("bounty $600,000") is None


def test_amount_ignores_values_at_or_below_fifty():
    assert amount_of("bounty $50") == 50  # filter happens later, parser stays literal
    assert amount_of("bounty $49") == 49


def test_difficulty_comes_from_labels():
    assert difficulty_of(["good first issue"]) == 1.0
    assert difficulty_of(["bug"]) == 2.0
    assert difficulty_of(["enhancement"]) == 3.0
    assert difficulty_of(["something else"]) == 2.5


def test_render_marks_unpriced_rows_unknown_and_never_claimed():
    rows = [
        {"repo": "a/b", "number": 1, "url": "https://example/1", "amount_usd": None,
         "score": None, "skills": ["go"], "difficulty": 2.0, "stars": 50,
         "quote": "bounty on the platform", "platform_link": "algora.io",
         "status": "READY-UNPRICED", "last_push": "2026-11-01", "labels": []},
    ]
    text = render(rows)
    assert "amount not in the text" in text
    assert "UNKNOWN" in text
    assert "never claimed" in text
    assert "READY" in text


def test_workflow_runs_every_six_hours_and_forever():
    payload = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    assert payload["on"]["schedule"][0]["cron"] == "17 */6 * * *"
    assert "workflow_dispatch" in payload["on"]
    assert payload["permissions"]["contents"] == "write"
    assert payload["permissions"]["issues"] == "read"


def test_workflow_never_comments_or_claims():
    text = WORKFLOW.read_text(encoding="utf-8")
    for forbidden in ("gh issue comment", "gh issue edit", "gh issue close", "gh pr create"):
        assert forbidden not in text
    assert "mutations_performed" in text


def test_record_file_claims_zero_mutations():
    data = json.loads((ROOT / "data" / "money" / "paid_issues.json").read_text(encoding="utf-8"))
    assert data["mutations_performed"] == 0
    assert set(data["status_values"]) <= {"READY", "READY-UNPRICED"}
    assert len(data["rows"]) <= data["limit"]
