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

import requests

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "Barrot-Agent/B-Agent")
AUTO_CLOSE_LABELS = {"autogen", "digest", "noise"}


def gh(*args):
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr}")
    return result.stdout


def get_issue(issue_number):
    raw = gh("issue", "view", str(issue_number), "--json", "title,body,number,state,labels")
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


def get_latest_run_status(workflow_id):
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    r = requests.get(
        f"https://api.github.com/repos/{REPO}/actions/workflows/{workflow_id}/runs",
        headers=headers,
        params={"per_page": 1},
        timeout=15,
    )
    r.raise_for_status()
    runs = r.json().get("workflow_runs", [])
    if not runs:
        return None
    return runs[0]


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
    labels = {label["name"].lower() for label in issue.get("labels", [])}
    if not labels & AUTO_CLOSE_LABELS:
        print(
            "Issue has no auto-close policy label "
            f"({', '.join(sorted(AUTO_CLOSE_LABELS))}); leaving untouched."
        )
        return

    workflow_name = extract_workflow_name(issue["title"])
    if not workflow_name:
        print("Not a [Auto] Workflow failing issue - this resolver doesn't "
              "handle general issues yet. Leaving untouched.")
        return

    print(f"Real workflow name extracted: {workflow_name}")
    wf = find_workflow_file(workflow_name)
    if not wf:
        print(f"Could not find a real workflow named '{workflow_name}' - "
              f"cannot verify current status. Leaving issue open, no action taken.")
        return

    print(f"Found real workflow: id={wf['id']}, path={wf['path']}")
    latest_run = get_latest_run_status(wf["id"])
    if not latest_run:
        print("No runs found for this workflow. Leaving issue open, no action taken.")
        return

    conclusion = latest_run.get("conclusion")
    run_id = latest_run.get("id")
    run_url = latest_run.get("html_url")
    print(f"Most recent real run: id={run_id}, conclusion={conclusion}")

    if conclusion == "success":
        comment = (
            f"Checked the real, current status of the '{workflow_name}' workflow: "
            f"its most recent run ([#{run_id}]({run_url})) completed successfully. "
            f"This issue was opened by an earlier failed run, but the underlying "
            f"problem has since been fixed and the workflow is genuinely passing now. "
            f"Closing as resolved - verified against live workflow status, not assumed."
        )
        print("Real conclusion: SUCCESS - closing issue with honest explanation")
        gh("issue", "comment", str(issue_number), "--body", comment)
        gh("issue", "close", str(issue_number))
        print(f"Issue #{issue_number} closed.")
    else:
        log_tail = get_run_log_tail(run_id)
        comment = (
            f"Checked the real, current status of the '{workflow_name}' workflow: "
            f"its most recent run ([#{run_id}]({run_url})) still shows "
            f"conclusion='{conclusion}'. This is a real, current failure, not stale. "
            f"Leaving this issue open - diagnosis needed before a fix should be "
            f"attempted. Real log tail from the failing run:\n\n```\n{log_tail}\n```"
        )
        print("Real conclusion: STILL FAILING - posting diagnostic comment, leaving open")
        gh("issue", "comment", str(issue_number), "--body", comment)
        print(f"Diagnostic comment posted to issue #{issue_number}. Left open for review.")


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
