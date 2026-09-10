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
from typing import Any, Callable

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
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
MAX_TOOL_ROUNDS = 4
MAX_SEARCH_RESULTS = 50

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


def _tool_error(message: str) -> str:
    return json.dumps({"success": False, "error": message}, sort_keys=True)


class RepoBrowser:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def _resolve(self, path: str) -> Path:
        cleaned = str(path).strip()
        if not cleaned:
            raise ValueError("repo_browser path must be non-empty; use '.' for the repository root.")
        if Path(cleaned).is_absolute():
            raise ValueError("repo_browser path must be relative to the repository root.")
        target = (self.root / cleaned).resolve()
        if target != self.root and self.root not in target.parents:
            raise ValueError("repo_browser path escapes the repository root.")
        return target

    @staticmethod
    def _is_noise(path: Path) -> bool:
        return any(part in NOISE_PREFIXES or part.startswith(".pytest_cache") for part in path.parts)

    def print_tree(self, args: dict[str, Any]) -> str:
        try:
            target = self._resolve(args.get("path", "."))
            depth = int(args.get("depth", 2) or 2)
        except (TypeError, ValueError) as exc:
            return _tool_error(str(exc))
        depth = max(0, min(depth, 6))
        if not target.exists():
            return _tool_error(f"repo_browser path does not exist: {args.get('path', '.')}")

        lines: list[str] = []

        def walk(current: Path, level: int) -> None:
            relative = "." if current == self.root else str(current.relative_to(self.root))
            prefix = "  " * level
            label = relative + ("/" if current.is_dir() and relative != "." else "")
            lines.append(f"{prefix}{label}")
            if level >= depth or not current.is_dir():
                return
            children = sorted(
                child for child in current.iterdir() if not self._is_noise(child)
            )
            for child in children[:100]:
                walk(child, level + 1)
            if len(children) > 100:
                lines.append(f"{prefix}  ... ({len(children) - 100} more entries omitted)")

        walk(target, 0)
        return "\n".join(lines[:500])

    def search(self, args: dict[str, Any]) -> str:
        query = str(args.get("query") or args.get("pattern") or "").strip()
        if not query:
            return _tool_error("repo_browser search query must be non-empty.")
        try:
            target = self._resolve(args.get("path", "."))
            recursive = bool(args.get("recursive", True))
            max_results = int(args.get("max_results", MAX_SEARCH_RESULTS) or MAX_SEARCH_RESULTS)
            pattern = re.compile(query)
        except (TypeError, ValueError, re.error) as exc:
            return _tool_error(str(exc))
        max_results = max(1, min(max_results, MAX_SEARCH_RESULTS))
        if not target.exists():
            return _tool_error(f"repo_browser path does not exist: {args.get('path', '.')}")

        candidates = target.rglob("*") if recursive else target.glob("*")
        matches: list[dict[str, Any]] = []
        for candidate in sorted(candidates):
            if self._is_noise(candidate) or candidate.is_dir():
                continue
            relative = str(candidate.relative_to(self.root))
            if pattern.search(relative):
                matches.append({"path": relative, "kind": "path"})
            if len(matches) >= max_results:
                break
            try:
                for line_number, line in enumerate(
                    candidate.read_text(encoding="utf-8", errors="replace").splitlines(),
                    start=1,
                ):
                    if pattern.search(line):
                        matches.append(
                            {
                                "path": relative,
                                "kind": "content",
                                "line": line_number,
                                "text": line[:200],
                            }
                        )
                    if len(matches) >= max_results:
                        break
            except OSError:
                continue
            if len(matches) >= max_results:
                break
        return json.dumps(
            {
                "success": True,
                "path": "." if target == self.root else str(target.relative_to(self.root)),
                "query": query,
                "matches": matches,
            },
            sort_keys=True,
        )


def _groq_payload(
    messages: list[dict[str, Any]],
    *,
    tools: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.2,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    return payload


def _send_groq_request(
    payload: dict[str, Any],
    *,
    request_sender: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if request_sender is not None:
        return request_sender(payload)
    body = json.dumps(payload).encode()
    request = urllib.request.Request(
        GROQ_ENDPOINT,
        data=body,
        headers={
            "Authorization": "Bearer " + GROQ_KEY,
            "Content-Type": "application/json",
            "User-Agent": "Barrot-Agent/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:600]
        lowered = detail.lower()
        if (
            exc.code == 400
            and "tool choice is none" in lowered
            and "model called a tool" in lowered
        ):
            raise RuntimeError(f"LLM tool conflict: {detail}") from exc
        if exc.code in {401, 403}:
            raise RuntimeError(f"LLM authentication failed: {detail}") from exc
        raise RuntimeError(f"Groq HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"LLM network error: {exc}") from exc
    except TimeoutError as exc:
        raise TimeoutError("Groq request timed out") from exc


class ScriptBrain:
    def __init__(
        self,
        *,
        request_sender: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
        repo_root: Path = ROOT,
        max_tool_rounds: int = MAX_TOOL_ROUNDS,
    ):
        self.request_sender = request_sender
        self.repo_browser = RepoBrowser(repo_root)
        self.max_tool_rounds = max_tool_rounds
        self.tool_funcs = {
            "repo_browser.print_tree": self.repo_browser.print_tree,
            "repo_browser.search": self.repo_browser.search,
        }
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "repo_browser.print_tree",
                    "description": "Print a real repository tree for a relative path. Use '.' for the repository root.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "minLength": 1},
                            "depth": {"type": "integer", "minimum": 0, "maximum": 6},
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "repo_browser.search",
                    "description": "Search real repository file paths and file contents with a regex query inside a relative path.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "minLength": 1},
                            "path": {"type": "string", "minLength": 1},
                            "recursive": {"type": "boolean"},
                            "max_results": {"type": "integer", "minimum": 1, "maximum": MAX_SEARCH_RESULTS},
                        },
                        "required": ["query", "path"],
                    },
                },
            },
        ]

    def _tool_result(self, tool_call: dict[str, Any]) -> str:
        function = tool_call.get("function") or {}
        name = str(function.get("name", "")).strip()
        raw_arguments = function.get("arguments") or "{}"
        if name not in self.tool_funcs:
            raise RuntimeError(f"Unsupported tool requested by LLM: {name}")
        try:
            arguments = json.loads(raw_arguments)
        except json.JSONDecodeError as exc:
            return _tool_error(f"Invalid JSON arguments for {name}: {exc}")
        if not isinstance(arguments, dict):
            return _tool_error(f"Tool arguments for {name} must be an object.")
        return self.tool_funcs[name](arguments)

    def think(self, message: str, history: list[dict[str, str]] | None = None, system: str | None = None) -> str:
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        for _ in range(self.max_tool_rounds):
            payload = _groq_payload(messages, tools=self.tools)
            data = _send_groq_request(payload, request_sender=self.request_sender)
            try:
                reply = data["choices"][0]["message"]
            except (KeyError, IndexError, TypeError) as exc:
                raise RuntimeError(f"Unexpected Groq response: {str(data)[:600]}") from exc
            tool_calls = reply.get("tool_calls") or []
            if tool_calls:
                messages.append(
                    {
                        "role": "assistant",
                        "content": reply.get("content") or "",
                        "tool_calls": tool_calls,
                    }
                )
                for tool_call in tool_calls:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.get("id", ""),
                            "content": self._tool_result(tool_call),
                        }
                    )
                continue
            content = reply.get("content")
            if not isinstance(content, str) or not content.strip():
                raise RuntimeError("Groq returned an empty completion.")
            return content
        raise RuntimeError("LLM retry exhaustion: tool-calling rounds exceeded without a final answer.")


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


def _cycle_dict(cycle: Any) -> dict[str, Any]:
    if isinstance(cycle, dict):
        return cycle
    if hasattr(cycle, "to_dict"):
        return cycle.to_dict()
    raise TypeError("cycle must be a dict or provide to_dict()")


def create_pull_request(cycle: dict[str, object] | Any) -> None:
    cycle_data = _cycle_dict(cycle)
    safe_title = TITLE.replace('"', "'").replace("`", "'").replace("$", "")
    head_branch = (
        str(cycle_data.get("commit", {}).get("branch", "")).strip()
        or str(cycle_data.get("issue", {}).get("branch", "")).strip()
        or BRANCH
    )
    body = [
        f"Autonomous execution of #{ISSUE} by Barrot." if ISSUE and ISSUE != "0" else "Autonomous execution by Barrot.",
        "",
        f"- cycle_id: {cycle_data.get('cycle_id')}",
        f"- status: {cycle_data.get('status')}",
        f"- issue: {cycle_data.get('issue', {}).get('summary', '')}",
        f"- commit_sha: {cycle_data.get('commit', {}).get('sha', '')}",
        f"- remote_verified: {cycle_data.get('commit', {}).get('remote_verified', False)}",
        "",
        "Validation:",
        f"- issue_reproduced: {cycle_data.get('issue_reproduced')}",
        f"- local_validation_passed: {cycle_data.get('local_validation_passed')}",
        f"- resolution_verified: {cycle_data.get('resolution_verified')}",
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
            head_branch,
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


def write_collaboration_record(cycle: dict[str, object] | Any) -> Path:
    cycle_data = _cycle_dict(cycle)
    record_dir = ROOT / ".barrot" / "collaboration_records"
    record_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "work_bundle": "autonomous_repository_repair",
        "cycle_id": cycle_data.get("cycle_id"),
        "actions_performed": cycle_data.get("state_history", []),
        "files_changed": cycle_data.get("commit", {}).get("changed_paths", []),
        "tests": cycle_data.get("validation", {}),
        "results": {
            "status": cycle_data.get("status"),
            "repair_verified": cycle_data.get("repair_verified"),
            "remote_sync_verified": cycle_data.get("remote_sync_verified"),
            "resolution_verified": cycle_data.get("resolution_verified"),
        },
        "failures": cycle_data.get("failure"),
        "evidence": {
            "issue": cycle_data.get("issue", {}),
            "repair_plan": cycle_data.get("repair_plan", {}),
            "changes": cycle_data.get("changes", []),
            "commit": cycle_data.get("commit", {}),
            "sync": cycle_data.get("sync", []),
        },
        "commits": [cycle_data.get("commit", {})] if cycle_data.get("commit", {}).get("sha") else [],
        "remote_verification": cycle_data.get("sync", []),
        "final_state": cycle_data.get("current_state"),
        "remaining_blockers": cycle_data.get("failure"),
    }
    latest = record_dir / "latest_repository_repair.json"
    latest.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    cycle_id = str(cycle_data.get("cycle_id") or "unknown")
    per_cycle = record_dir / f"{cycle_id}.json"
    per_cycle.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    return latest


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
    write_collaboration_record(cycle.to_dict())

    if cycle.status == "no_repair_required":
        if cycle.report_only:
            return
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
