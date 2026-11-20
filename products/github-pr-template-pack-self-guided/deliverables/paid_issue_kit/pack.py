"""Build and validate a pull request body and an evidence pack.

The validator is deliberately strict. It rejects placeholder text, unverifiable
claims, a missing test command, a missing issue link, and a body that does not
say what the risk and rollback are. A PR that fails here is not ready to send.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

REQUIRED_SECTIONS = (
    "## What changed",
    "## Why",
    "## Proof",
    "## Risk and rollback",
    "## Checklist",
)

BANNED_CLAIMS = (
    (re.compile(r"\bguarantee(?:d|s)?\b", re.IGNORECASE), "guarantee language"),
    (re.compile(r"\b100\s?%", re.IGNORECASE), "100% claim"),
    (re.compile(r"\bzero[- ]risk\b", re.IGNORECASE), "zero-risk claim"),
    (re.compile(r"\bnever fails?\b", re.IGNORECASE), "never-fails claim"),
    (re.compile(r"\bfixes (?:everything|all)\b", re.IGNORECASE), "fixes-everything claim"),
    (re.compile(r"\bproduction[- ]ready\b", re.IGNORECASE), "unverifiable production-ready claim"),
    (re.compile(r"\bbulletproof\b", re.IGNORECASE), "unverifiable bulletproof claim"),
)

PLACEHOLDERS = (
    "TODO",
    "TBD",
    "FIXME",
    "CHANGEME",
    "lorem ipsum",
    "<insert",
    "{{",
)

TEST_COMMAND = re.compile(
    r"(pytest|python3? -m (?:pytest|unittest)|npm (?:run )?test|go test|cargo test|"
    r"make test|bash [\w./-]+\.sh|\./[\w./-]+\.sh)",
    re.IGNORECASE,
)

ISSUE_LINK = re.compile(
    r"https?://\S*(?:github\.com/[^/\s]+/[^/\s]+/issues/\d+|opire\.dev/\S+|"
    r"algora\.io/\S+/issue/\d+)",
    re.IGNORECASE,
)

PR_BODY_MIN_CHARS = 200
PR_BODY_MAX_CHARS = 20_000


def build_pr_body(plan: dict[str, Any]) -> str:
    """Render a deterministic PR body from a plan. Missing keys raise ValueError."""
    bullets = plan.get("change_bullets")
    if not isinstance(bullets, list) or not bullets:
        raise ValueError("plan field 'change_bullets' must be a non-empty list")
    checklist = plan.get("checklist")
    if not isinstance(checklist, list) or not checklist:
        raise ValueError("plan field 'checklist' must be a non-empty list")
    for key in (
        "issue_url",
        "summary",
        "why",
        "test_command",
        "test_result",
        "risk",
        "rollback",
    ):
        value = plan.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"plan field {key!r} must be a non-empty string")

    bullet_text = "\n".join(f"- {str(item).strip()}" for item in bullets)
    checklist_text = "\n".join(f"- [x] {str(item).strip()}" for item in checklist)
    note = str(plan.get("note", "")).strip()
    prefix = f"<!-- {note} -->\n\n" if note else ""
    body = f"""{prefix}## What changed

{plan['summary'].strip()}

{bullet_text}

## Why

Issue: {plan['issue_url'].strip()}

{plan['why'].strip()}

## Proof

Command: `{plan['test_command'].strip()}`
Result: {plan['test_result'].strip()}

## Risk and rollback

Risk: {plan['risk'].strip()}
Rollback: {plan['rollback'].strip()}

## Checklist

{checklist_text}
"""
    return body.strip() + "\n"


def validate_pr_body(text: str) -> list[str]:
    """Return every problem found. Empty list means the body passed."""
    problems: list[str] = []
    if not isinstance(text, str) or not text.strip():
        return ["pr body is empty"]

    headings = {line.strip() for line in text.splitlines()}
    for section in REQUIRED_SECTIONS:
        if section not in headings:
            problems.append(f"missing section: {section}")

    if len(text) < PR_BODY_MIN_CHARS:
        problems.append(f"pr body shorter than {PR_BODY_MIN_CHARS} characters")
    if len(text) > PR_BODY_MAX_CHARS:
        problems.append(f"pr body longer than {PR_BODY_MAX_CHARS} characters")
    if not ISSUE_LINK.search(text):
        problems.append("no issue-specific link found")
    if "Command:" not in text or not TEST_COMMAND.search(text):
        problems.append("no runnable test command found")
    if "Result:" not in text:
        problems.append("no test result found")
    if "Rollback:" not in text:
        problems.append("no rollback statement found")

    checked = len(re.findall(r"^\s*-\s*\[[xX]\]", text, re.MULTILINE))
    if checked < 2:
        problems.append("fewer than two checked checklist items")

    problems.extend(_text_problems(text))
    return problems


def build_evidence_pack(plan: dict[str, Any], generated_at: datetime | None = None) -> str:
    """Render an evidence pack. Every claim must carry evidence and a limit."""
    claims = plan.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ValueError("plan field 'claims' must be a non-empty list")
    for key in ("issue_id", "issue_url", "command", "output"):
        value = plan.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"plan field {key!r} must be a non-empty string")
    exit_code = plan.get("exit_code")
    if isinstance(exit_code, bool) or not isinstance(exit_code, int):
        raise ValueError("plan field 'exit_code' must be an integer")

    moment = (generated_at or datetime.now(timezone.utc)).isoformat().replace("+00:00", "Z")
    lines = [
        f"# Evidence pack - {plan['issue_id'].strip()}",
        "",
        f"Generated: {moment}",
        f"Issue: {plan['issue_url'].strip()}",
        f"Commit: {str(plan.get('commit', 'uncommitted')).strip()}",
        f"Environment: {str(plan.get('environment', 'not stated')).strip()}",
        "",
        "## Command",
        "",
        "```",
        plan["command"].strip(),
        "```",
        "",
        f"Exit code: {exit_code}",
        "",
        "## Output",
        "",
        "```",
        plan["output"].strip(),
        "```",
        "",
        "## Claims",
        "",
    ]
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValueError("each claim must be an object with text, evidence, limit")
        for key in ("text", "evidence", "limit"):
            if not isinstance(claim.get(key), str) or not claim[key].strip():
                raise ValueError(f"claim field {key!r} must be a non-empty string")
        lines.extend(
            [
                f"### {claim['text'].strip()}",
                "",
                f"- Evidence: {claim['evidence'].strip()}",
                f"- Limit: {claim['limit'].strip()}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def validate_evidence_plan(plan: dict[str, Any]) -> list[str]:
    """Validate the evidence plan before rendering. Empty list means pass."""
    problems: list[str] = []
    claims = plan.get("claims")
    if not isinstance(claims, list) or not claims:
        problems.append("at least one claim is required")
        claims = []
    for index, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict):
            problems.append(f"claim {index} is not an object")
            continue
        for key in ("text", "evidence", "limit"):
            value = claim.get(key)
            if not isinstance(value, str) or not value.strip():
                problems.append(f"claim {index} missing {key}")
        text = str(claim.get("text", ""))
        if len(text) < 10:
            problems.append(f"claim {index} is shorter than 10 characters")
        for pattern, label in BANNED_CLAIMS:
            if pattern.search(text):
                problems.append(f"claim {index}: {label}")

    issue_url = plan.get("issue_url")
    if not isinstance(issue_url, str) or not re.match(r"^https?://\S+$", issue_url.strip()):
        problems.append("issue_url is not an http(s) URL")

    exit_code = plan.get("exit_code")
    if isinstance(exit_code, bool) or not isinstance(exit_code, int):
        problems.append("exit_code must be an integer")
    elif exit_code != 0:
        problems.append("exit_code is not 0; a failing run cannot be presented as proof")

    if not str(plan.get("output", "")).strip():
        problems.append("command output is empty")
    return problems


def _text_problems(text: str) -> list[str]:
    problems: list[str] = []
    lowered = text.lower()
    for placeholder in PLACEHOLDERS:
        if placeholder.lower() in lowered:
            problems.append(f"placeholder text present: {placeholder}")
    for match in re.finditer(r"\[([^\]\n]{3,})\]", text):
        content = match.group(1)
        if content[:1] in ("#", "x", "X", " "):
            continue  # issue reference, checkbox, or blank task box
        if text[match.end():match.end() + 1] == "(":
            continue  # markdown link text
        if " " in content or "..." in content:
            problems.append(f"placeholder bracket present: [{content}]")
            break
    for pattern, label in BANNED_CLAIMS:
        if pattern.search(text):
            problems.append(f"unverifiable claim present: {label}")
    return problems
