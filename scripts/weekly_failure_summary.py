#!/usr/bin/env python3
"""Create a weekly, deduplicated summary of failed GitHub Actions runs."""

import json
import os
import re
import subprocess
from collections import Counter, defaultdict

REPO = os.environ.get("GITHUB_REPOSITORY", "Barrot-Agent/B-Agent")
TITLE = "Weekly workflow failure summary"


def gh(*args):
    result = subprocess.run(["gh", *args], check=True, capture_output=True, text=True)
    return result.stdout


def main():
    runs = json.loads(
        gh(
            "run",
            "list",
            "--repo",
            REPO,
            "--status",
            "failure",
            "--limit",
            "100",
            "--json",
            "workflowName,createdAt,url,databaseId",
        )
    )
    grouped = defaultdict(list)
    for run in runs:
        if run["createdAt"] >= "":  # retain the API's ISO timestamps for sorting
            grouped[run["workflowName"]].append(run)

    lines = ["## Weekly workflow failure summary", "", "Failures observed in the latest Actions window:"]
    if not grouped:
        lines.append("- None.")
    else:
        for workflow, workflow_runs in sorted(grouped.items()):
            lines.append(f"- **{workflow}**: {len(workflow_runs)} failure(s)")
            for run in sorted(workflow_runs, key=lambda item: item["createdAt"], reverse=True)[:3]:
                lines.append(f"  - [{run['createdAt']}]({run['url']})")

    causes = Counter()
    patterns = {
        "dependency/install": r"(pip install|npm install|dependency|could not find)",
        "lint/format": r"(flake8|black|isort|lint|format)",
        "test/assertion": r"(pytest|assertionerror|test failed)",
        "timeout/cancellation": r"(timed out|timeout|cancelled)",
        "permissions": r"(permission denied|resource not accessible|forbidden)",
    }
    for workflow_runs in grouped.values():
        for run in workflow_runs[:3]:
            try:
                log = gh("run", "view", str(run["databaseId"]), "--repo", REPO, "--log")
            except subprocess.CalledProcessError:
                continue
            for name, pattern in patterns.items():
                if re.search(pattern, log, re.IGNORECASE):
                    causes[name] += 1
    lines.extend(["", "### Recurring root-cause signals"])
    lines.extend(f"- `{name}`: {count} run(s)" for name, count in causes.most_common())
    lines.append("\n_This report is generated weekly; inspect linked runs before applying fixes._")
    body = "\n".join(lines)
    existing = gh("issue", "list", "--repo", REPO, "--state", "open", "--search", f'"{TITLE}" in:title', "--json", "number")
    if json.loads(existing):
        return
    url = gh("issue", "create", "--repo", REPO, "--title", TITLE, "--body", body).strip()
    number = url.rsplit("/", 1)[-1]
    subprocess.run(["gh", "issue", "edit", number, "--repo", REPO, "--add-label", "digest", "--add-label", "autogen"], check=False)


if __name__ == "__main__":
    main()
