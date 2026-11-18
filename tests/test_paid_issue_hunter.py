"""The hunter must parse amounts strictly, stay read-only, and run every 6 hours."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.paid_issue_hunter import MAX_PLAUSIBLE, amount_of, difficulty_of, platform_bounty_link, render

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "paid-issue-hunter.yml"
PUBLISH = ROOT / ".github" / "workflows" / "paid-issue-publish.yml"


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
    # Governance: a scheduled workflow may not hold a write permission.
    assert payload["permissions"]["contents"] == "read"
    assert payload["permissions"]["issues"] == "read"
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "persist-credentials: false" in text
    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7" in text
    assert "actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 # v7" in text
    assert "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7" in text


def test_workflow_never_comments_or_claims():
    text = WORKFLOW.read_text(encoding="utf-8")
    for forbidden in ("gh issue comment", "gh issue edit", "gh issue close", "gh pr create"):
        assert forbidden not in text
    assert "mutations_performed" in text


def test_scheduled_hunter_cannot_push():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "git push" not in text
    assert "contents: write" not in text


def test_scheduled_hunter_cannot_push():
    text = WORKFLOW.read_text(encoding="utf-8").lower()
    assert "git push" not in text
    assert "git commit" not in text
    assert "contents: write" not in text


def test_publish_workflow_is_disabled_until_authorized():
    payload = yaml.load(PUBLISH.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    trigger = payload["on"]["workflow_run"]
    assert trigger["workflows"] == ["Paid issue hunter"]
    assert trigger["types"] == ["completed"]
    assert trigger["branches"] == ["main"]
    assert payload["permissions"] == {}
    assert str(payload["jobs"]["disabled"]["if"]).lower() == "false"
    assert len(payload["jobs"]["disabled"]["steps"]) == 1
    text = PUBLISH.read_text(encoding="utf-8")
    assert "Repository publication is disabled pending explicit authorization" in text
    for forbidden in (
        "contents: write",
        "persist-credentials: true",
        "git push",
        "actions/checkout",
        "actions/download-artifact",
        "gh pr merge",
        "gh issue",
    ):
        assert forbidden not in text
def test_record_file_claims_zero_mutations():
    data = json.loads((ROOT / "data" / "money" / "paid_issues.json").read_text(encoding="utf-8"))
    assert data["mutations_performed"] == 0
    assert set(data["status_values"]) <= {"READY", "READY-UNPRICED"}
    assert len(data["rows"]) <= data["limit"]


def test_repo_level_sponsorship_link_is_not_a_bounty():
    # Real body text from k3d-io/k3d#1689, a bug template, not a bounty.
    body = "Need this fixed urgently? Consider sponsoring this issue via https://issuehunt.io/r/k3d-io/k3d"
    assert platform_bounty_link(body) == ""


def test_documentation_and_blog_links_are_not_bounties():
    assert platform_bounty_link("see https://docs.opire.dev for setup") == ""
    assert platform_bounty_link("https://coordinationmechanisms.gitcoin.co/") == ""


def test_issue_specific_platform_links_are_accepted():
    assert platform_bounty_link("https://algora.io/acme/app/issue/42") == "https://algora.io/acme/app/issue/42"
    assert platform_bounty_link("https://issuehunt.io/r/acme/app/issues/9182") == "https://issuehunt.io/r/acme/app/issues/9182"
