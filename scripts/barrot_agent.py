#!/usr/bin/env python3
"""
BARROT AGENT — deterministic repository repair worker.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sandbox import verify_result

from barrot_agent.orchestration.repository_repair import (
    RepositoryRepairController,
)


ROOT = Path(__file__).resolve().parents[1]
REPO = os.environ["REPO"]
TASK = os.environ.get("TASK_BODY", "")
TITLE = os.environ.get("TASK_TITLE", "Barrot task")
ISSUE = os.environ.get("ISSUE_NUMBER", "")
BRANCH = os.environ.get("BRANCH", "barrot/task")
MODEL = os.environ.get("BRAIN_MODEL", "").strip() or "openai/gpt-oss-120b"
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

NOISE_PREFIXES = (".git", ".npm", "node_modules", ".cache", "_cacache")


def run(args: list[str], *, check: bool = True, quiet: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(args))
    result = subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if not quiet:
        if result.stdout.strip():
            print(result.stdout[:3000])
        if result.stderr.strip():
            print(result.stderr[:3000])
    if check and result.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(args)}\n{result.stderr[:1000]}")
    return result


def repo_inventory(max_files: int = 120, task_text: str = "") -> str:
    files = run(["git", "ls-files"], check=False, quiet=True).stdout.splitlines()
    files = [item for item in files if not any(item.startswith(prefix) for prefix in NOISE_PREFIXES)]
    top_dirs = sorted({item.split("/")[0] for item in files if "/" in item})
    lowered = task_text.lower()
    scope = None
    for directory in top_dirs:
        if f"{directory.lower()}/" in lowered:
            scope = directory
            break
    if scope:
        scoped = [item for item in files if item.startswith(scope + "/")]
        if scoped:
            files = scoped
    cap = len(files) if scope else max_files
    tree: list[str] = []
    for item in files[:cap]:
        try:
            size = (ROOT / item).stat().st_size
        except OSError:
            size = 0
        tree.append(f"{item} ({size}b)")
    extra = len(files) - cap
    if extra > 0:
        tree.append(f"... ({extra} more files omitted)")
    return "\n".join(tree)


def ask_brain(system: str, user: str) -> str:
    body = json.dumps(
        {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": 4096,
            "temperature": 0.2,
        }
    ).encode()
    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"******",
            "Content-Type": "application/json",
            "User-Agent": "Barrot-Agent/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.load(response)["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:600]
        raise RuntimeError(f"Groq HTTP {exc.code}: {detail}") from exc
    except TimeoutError as exc:
        raise TimeoutError("Groq request timed out") from exc


class ScriptBrain:
    def think(self, message: str, history: list[dict[str, str]] | None = None, system: str | None = None) -> str:
        del history
        return ask_brain(system or "", message)


def build_directory_context(all_files: list[str], task_text: str) -> str:
    top_dirs = sorted({item.split("/")[0] for item in all_files if "/" in item})
    lowered = task_text.lower()
    scope_dir = None
    for directory in top_dirs:
        if f"{directory.lower()}/" in lowered:
            scope_dir = directory
            break
    if not scope_dir:
        return ""
    scoped_files = [item for item in all_files if item.startswith(scope_dir + "/")]
    sized: list[tuple[int, str]] = []
    for item in scoped_files:
        try:
            sized.append(((ROOT / item).stat().st_size, item))
        except OSError:
            continue
    sized.sort()
    budget = 5000
    shown: list[str] = []
    omitted: list[str] = []
    for size, item in sized:
        if size <= budget:
            shown.append(item)
            budget -= size
        else:
            omitted.append(item)
    chunks = [
        "\n\nREAL FULL CONTENT of files in the scoped directory "
        "(only these - do NOT describe or invent internals of any other file):"
    ]
    for item in shown:
        try:
            chunks.append(f"\n=== {item} ===\n{(ROOT / item).read_text(encoding='utf-8')}")
        except Exception:
            continue
    if omitted:
        chunks.append(
            "\n\nThe following files exist but their content was NOT shown to you "
            "(too large for this pass): "
            + ", ".join(omitted)
            + ". Do not describe their internals or invent file contents."
        )
    return "\n".join(chunks)


def build_file_context(task_title: str, task_body: str) -> str:
    named = re.findall(r"[\w./-]+\.(?:py|jsonl|json|ya?ml|md|txt|toml)", f"{task_title}\n{task_body}")
    budget = 6000
    context = ""
    omitted: list[str] = []
    for file_path in list(dict.fromkeys(named))[:5]:
        target = ROOT / file_path
        if not target.exists() or not target.is_file():
            continue
        try:
            size = target.stat().st_size
            if size > budget:
                omitted.append(f"{file_path} ({size}b)")
                continue
            content = target.read_text(encoding="utf-8")
            if len(content) > budget:
                omitted.append(f"{file_path} ({size}b)")
                continue
            context += f"\n=== CURRENT CONTENT OF {file_path} ===\n{content}\n=== END {file_path} ===\n"
            budget -= len(content)
        except Exception:
            continue
    if omitted:
        context += (
            "\n\nThe following named files exist but were too large to include in full: "
            + ", ".join(omitted)
            + ". Do not invent their internal contents."
        )
    return context


def run_gh(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def build_github_context(task_text: str) -> str:
    lowered = task_text.lower()
    github_context = ""
    if "pull request" in lowered or " pr " in lowered or "prs" in lowered:
        result = run_gh(
            [
                "pr",
                "list",
                "--repo",
                REPO,
                "--state",
                "open",
                "--limit",
                "100",
                "--json",
                "number,title,mergeable,additions,deletions,author",
                "-q",
                '.[] | "#\\(.number) | \\(.mergeable) | +\\(.additions)/-\\(.deletions) | @\\(.author.login) | \\(.title)"',
            ]
        )
        if result.returncode == 0 and result.stdout.strip():
            github_context += (
                "\n=== REAL OPEN PULL REQUESTS (use ONLY these, never invent) ===\n"
                + result.stdout[:12000]
                + "\n=== END PRS ===\n"
            )
    pr_numbers = re.findall(r"#(\d+)", task_text)
    if pr_numbers:
        diffs: list[str] = []
        for number in dict.fromkeys(pr_numbers):
            if len(diffs) >= 4:
                break
            result = run_gh(["pr", "diff", number, "--repo", REPO])
            if result.returncode == 0 and result.stdout.strip():
                diffs.append(f"--- PR #{number} DIFF ---\n{result.stdout[:1200]}")
        if diffs:
            github_context += (
                "\n=== REAL PR DIFFS (actual file changes — judge ONLY from these) ===\n"
                + "\n\n".join(diffs)
                + "\n=== END DIFFS ===\n"
            )
    if "issue" in lowered:
        result = run_gh(
            [
                "issue",
                "list",
                "--repo",
                REPO,
                "--state",
                "open",
                "--limit",
                "100",
                "--json",
                "number,title,author",
                "-q",
                '.[] | "#\\(.number) | \\(.author.login) | \\(.title)"',
            ]
        )
        if result.returncode == 0 and result.stdout.strip():
            github_context += (
                "\n=== REAL OPEN ISSUES (use ONLY these, never invent) ===\n"
                + result.stdout[:8000]
                + "\n=== END ISSUES ===\n"
            )
    return github_context


def build_audit_context(task_title: str, task_body: str) -> dict[str, str]:
    task_text = f"{task_title} {task_body}"
    inventory = repo_inventory(task_text=task_text)
    all_files = run(["git", "ls-files"], check=False, quiet=True).stdout.splitlines()
    file_context = build_file_context(task_title, task_body)
    directory_context = build_directory_context(all_files, task_text)
    github_context = build_github_context(task_text)
    note = ""
    if file_context:
        note += (
            "\n\nIMPORTANT: if editing any shown file, preserve all unrelated content and change only "
            "what is needed to resolve the reproduced issue."
        )
    if github_context:
        note += (
            "\n\nCRITICAL: the pull requests and issues above are the only real ones in scope. "
            "Use them verbatim or do not reference them."
        )
    return {
        "inventory": inventory,
        "file_context": file_context,
        "directory_context": directory_context,
        "github_context": github_context,
        "note": note,
    }


def configure_git() -> None:
    run(["git", "config", "user.email", "barrot@barrot-agent.com"])
    run(["git", "config", "user.name", "Barrot-Agent"])


def checkout_branch(branch: str) -> None:
    result = run(["git", "checkout", "-B", branch], check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"Unable to checkout branch {branch}")


def post_issue_comment(message: str) -> None:
    if not ISSUE or ISSUE == "0":
        return
    comment_path = Path("/tmp/barrot_comment_body.md")
    comment_path.write_text(message[:60000], encoding="utf-8")
    result = run_gh(["issue", "comment", ISSUE, "--repo", REPO, "--body-file", str(comment_path)])
    if result.returncode != 0:
        print(result.stderr[:3000], file=sys.stderr)


def create_pull_request(cycle: dict[str, object]) -> None:
    safe_title = TITLE.replace('"', "'").replace("`", "'").replace("$", "")
    body = [
        f"Autonomous execution of #{ISSUE} by Barrot." if ISSUE and ISSUE != "0" else "Autonomous execution by Barrot.",
        "",
        f"- cycle_id: {cycle.get('cycle_id')}",
        f"- status: {cycle.get('status')}",
        f"- issue: {cycle.get('issue', {}).get('summary', '')}",
        f"- commit_sha: {cycle.get('commit', {}).get('sha', '')}",
        f"- remote_verified: {cycle.get('commit', {}).get('remote_verified', False)}",
        "",
        "Validation:",
        f"- issue_reproduced: {cycle.get('issue_reproduced')}",
        f"- local_validation_passed: {cycle.get('local_validation_passed')}",
        f"- resolution_verified: {cycle.get('resolution_verified')}",
    ]
    pr_path = Path("/tmp/barrot_pr_body.md")
    pr_path.write_text("\n".join(body), encoding="utf-8")
    result = run_gh(
        [
            "pr",
            "create",
            "--repo",
            REPO,
            "--title",
            f"Barrot: {safe_title}",
            "--body-file",
            str(pr_path),
            "--head",
            BRANCH,
            "--base",
            "main",
        ]
    )
    if result.returncode != 0 and "already exists" not in (result.stderr + result.stdout).lower():
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "gh pr create failed")
    if result.stdout.strip():
        print(result.stdout[:3000])
    if result.stderr.strip():
        print(result.stderr[:3000])


def main() -> None:
    if not GROQ_KEY:
        raise SystemExit("GROQ_API_KEY not set")

    configure_git()
    checkout_branch(BRANCH)

    controller = RepositoryRepairController(
        brain=ScriptBrain(),
        workspace=ROOT,
        workspace_verifier=verify_result,
    )
    cycle = controller.run(
        task_title=TITLE,
        task_body=TASK,
        issue_number=ISSUE,
        repo=REPO,
        branch=BRANCH,
        audit_context=build_audit_context(TITLE, TASK),
    )

    rendered = json.dumps(cycle.to_dict(), indent=2)
    print(rendered)

    if cycle.status == "no_repair_required":
        message = cycle.report or "No deterministic repository repair was required."
        post_issue_comment(message)
        return

    if cycle.status != "complete":
        post_issue_comment(
            "Barrot repair failed safely.\n\n```json\n"
            + rendered[:55000]
            + "\n```"
        )
        raise SystemExit(1)

    create_pull_request(cycle.to_dict())


if __name__ == "__main__":
    main()
