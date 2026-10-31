#!/usr/bin/env python3
"""
BARROT-Ω ISSUE RESOLVER — first real version of autonomous GitHub
issue resolution, scoped to the "[Auto] Workflow failing: X" issue
class specifically, since it's structured and tractable: the issue
title names a real workflow, and resolution is genuinely checkable
(did the most recent run of that workflow pass or fail?), unlike a
general free-form bug report which needs much more context to resolve
safely.

Real process:
1. Fetch the real issue (title, body, number).
2. Extract the real workflow name from the title.
3. Query the real GitHub Actions API for that workflow's most recent
   run status - ground truth, not assumption.
4. If the most recent run succeeded: the issue is genuinely stale
   (already fixed since the notification fired). Post a real comment
   explaining what happened and close it.
5. If still failing: pull the real log tail, do NOT auto-fix yet -
   post an honest diagnostic comment and leave it open. Auto-fixing
   is a bigger, riskier step for a later version once this diagnostic
   step is proven correct.

Usage: python3 resolve_issue.py <issue_number>
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

import requests

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "Barrot-Agent/B-Agent")


def gh(*args):
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr}")
    return result.stdout


def get_issue(issue_number):
    raw = gh("issue", "view", str(issue_number), "--json", "title,body,number,state")
    return json.loads(raw)


def extract_workflow_name(title):
    m = re.match(r"\[Auto\] Workflow failing: (.+)", title)
    return m.group(1).strip() if m else None


def find_workflow_file(workflow_name):
    """Real workflow files use their 'name:' field which may differ from
    the filename - list all workflows and match by real display name.
    Uses --limit 200 since gh's default page size can miss workflows
    once a repo accumulates many of them (confirmed real risk in this
    project - 20+ workflows exist). Prints the real full list if no
    match is found, so a failure is diagnosable, not a silent guess."""
    raw = gh("workflow", "list", "--all", "--limit", "200", "--json", "name,id,path")
    workflows = json.loads(raw)
    print(f"Real workflow count found: {len(workflows)}")
    for wf in workflows:
        if wf["name"].strip().lower() == workflow_name.strip().lower():
            return wf
    print("No match. Real workflow names found:")
    for wf in workflows:
        print(f"  - {wf['name']!r}")
    return None


def extract_original_run_id(issue_body):
    """Return the run ID explicitly linked by the issue, only for this repository."""
    if not isinstance(issue_body, str):
        return None
    pattern = rf"https://github\.com/{re.escape(REPO)}/actions/runs/(\d+)(?:[/?#\s)]|$)"
    match = re.search(pattern, issue_body, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def _parse_github_timestamp(value):
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _api_get(path, params=None):
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    response = requests.get(
        f"https://api.github.com/repos/{REPO}/{path}",
        headers=headers,
        params=params,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def get_run_by_id(run_id):
    return _api_get(f"actions/runs/{run_id}")


def get_latest_run_status(workflow_id, branch):
    data = _api_get(
        f"actions/workflows/{workflow_id}/runs",
        params={"branch": branch, "per_page": 1},
    )
    runs = data.get("workflow_runs", [])
    return runs[0] if runs else None


def get_verified_recovery_runs(issue_body, workflow_id):
    """Require a newer successful run of the same workflow on the failed run's branch.

    A success on an unrelated PR branch must never close an issue raised by a
    different branch's failure. Missing or inconsistent evidence fails closed.
    """
    original_run_id = extract_original_run_id(issue_body)
    if original_run_id is None:
        print("Issue does not contain a verifiable failed-run URL for this repository.")
        return None

    original = get_run_by_id(original_run_id)
    if original.get("workflow_id") != workflow_id or original.get("conclusion") != "failure":
        print("Linked run is not a failed run of the matched workflow.")
        return None

    branch = original.get("head_branch")
    if not isinstance(branch, str) or not branch.strip():
        print("Linked failed run has no verifiable head branch.")
        return None

    latest = get_latest_run_status(workflow_id, branch)
    if not latest:
        print("No later workflow run exists on the original failed run's branch.")
        return None
    if (
        latest.get("workflow_id") != workflow_id
        or latest.get("head_branch") != branch
        or latest.get("id") == original_run_id
        or latest.get("status") != "completed"
    ):
        print("Latest run does not establish a completed recovery on the same branch.")
        return None

    original_created = _parse_github_timestamp(original.get("created_at"))
    latest_created = _parse_github_timestamp(latest.get("created_at"))
    if original_created is None or latest_created is None or latest_created <= original_created:
        print("Latest run is not provably later than the linked failure.")
        return None

    return {"original": original, "latest": latest}

def get_run_log_tail(run_id, lines=40):
    raw = gh("run", "view", str(run_id), "--log")
    all_lines = raw.strip().split("\n")
    return "\n".join(all_lines[-lines:])


def resolve(issue_number):
    print(f"=== Resolving issue #{issue_number} ===")
    issue = get_issue(issue_number)
    print(f"Title: {issue['title']}")
    print(f"State: {issue['state']}")

    if issue["state"] != "OPEN":
        print("Issue is already closed - nothing to do.")
        return

    workflow_name = extract_workflow_name(issue["title"])
    if not workflow_name:
        print("Not a [Auto] Workflow failing issue - leaving untouched.")
        return

    print(f"Real workflow name extracted: {workflow_name}")
    wf = find_workflow_file(workflow_name)
    if not wf:
        print(f"Could not find a real workflow named '{workflow_name}' - leaving issue open.")
        return

    print(f"Found real workflow: id={wf['id']}, path={wf['path']}")
    evidence = get_verified_recovery_runs(issue.get("body", ""), wf["id"])
    if not evidence:
        print("Recovery is not proven by a later completed run on the original branch. Leaving issue open.")
        return

    original = evidence["original"]
    latest_run = evidence["latest"]
    conclusion = latest_run.get("conclusion")
    run_id = latest_run.get("id")
    run_url = latest_run.get("html_url")
    original_run_id = original.get("id")
    print(
        f"Original failed run: id={original_run_id}, branch={original.get('head_branch')}; "
        f"later run: id={run_id}, conclusion={conclusion}"
    )

    if conclusion == "success":
        comment = (
            f"Verified recovery for the original failed run ([#{original_run_id}]"
            f"(https://github.com/{REPO}/actions/runs/{original_run_id})): a later "
            f"completed run of '{workflow_name}' on the same branch "
            f"([#{run_id}]({run_url})) succeeded. Closing this workflow-failure issue "
            f"based on same-branch, time-ordered run evidence."
        )
        print("Verified same-branch recovery: SUCCESS - closing issue.")
        gh("issue", "comment", str(issue_number), "--body", comment)
        gh("issue", "close", str(issue_number))
        print(f"Issue #{issue_number} closed.")
    elif conclusion == "failure":
        log_tail = get_run_log_tail(run_id)
        comment = (
            f"Checked the latest completed run of '{workflow_name}' on the same branch "
            f"as the original failed run ([#{run_id}]({run_url})): it still failed. "
            f"Leaving this issue open for diagnosis. Log tail:\n\n"
            f"```\n{log_tail}\n```"
        )
        print("Same-branch run still failing - posting diagnostic comment, leaving open.")
        gh("issue", "comment", str(issue_number), "--body", comment)
        print(f"Diagnostic comment posted to issue #{issue_number}. Left open for review.")
    else:
        print(f"Latest same-branch run concluded '{conclusion}'. No automatic issue action taken.")

def resolve_all_open():
    """Real batch mode: scan every open issue, attempt to resolve any
    that match the [Auto] Workflow failing pattern. Skips (does not
    touch) anything that doesn't match - same safe, honest behavior
    as the single-issue path."""
    raw = gh("issue", "list", "--state", "open", "--limit", "200",
              "--json", "number,title")
    issues = json.loads(raw)
    candidates = [i for i in issues if extract_workflow_name(i["title"])]
    print(f"Found {len(issues)} open issues, {len(candidates)} match "
          f"the [Auto] Workflow failing pattern.")
    for issue in candidates:
        try:
            resolve(issue["number"])
        except Exception as e:
            print(f"  Real error resolving #{issue['number']}: {e}")
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python3 resolve_issue.py <issue_number>|--all")
    if sys.argv[1] == "--all":
        resolve_all_open()
    else:
        resolve(int(sys.argv[1]))
