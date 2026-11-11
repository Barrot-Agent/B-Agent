#!/usr/bin/env python3
"""
BARROT AGENT — deterministic repository repair worker.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import deque
from pathlib import Path
from threading import Lock
from typing import Any, Callable
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT_STR = str(ROOT)
SCRIPTS_DIR_STR = str(SCRIPTS_DIR)
if ROOT_STR in sys.path:
    sys.path.remove(ROOT_STR)
sys.path.insert(0, ROOT_STR)
if SCRIPTS_DIR_STR in sys.path:
    sys.path.remove(SCRIPTS_DIR_STR)
sys.path.insert(1, SCRIPTS_DIR_STR)

from sandbox import verify_result

from barrot_agent.orchestration.learning_curriculum import LearningCurriculum
from barrot_agent.orchestration.mission_registry import MissionRegistry
from barrot_agent.orchestration.verified_learning_store import VerifiedLearningStore
from barrot_agent.orchestration.shared_runtime import Capability, DefensiveWatchdog

from barrot_agent.orchestration.repository_repair import (
    ProjectIdentity,
    RepositoryRepairController,
    WorkQueueController,
    safe_checkout_branch,
)
from barrot_agent.orchestration.bundle_engineering import (
    BundleEngineeringController,
    BundleEngineeringResult,
    extract_authorization_boundaries,
    review_work_bundle,
)
from barrot_agent.orchestration.bundle_lifecycle import BundleLifecycleStore, dispatch_bundle_tasks
from barrot_agent.research import (
    ScientificDiscoveryController,
    is_scientific_discovery_task,
    should_route_scientific_discovery,
    select_scientific_problem_adapter,
)

REPO = os.environ["REPO"]
TASK = os.environ.get("TASK_BODY", "")
TITLE = os.environ.get("TASK_TITLE", "Barrot task")
TASK_MODE = os.environ.get("TASK_MODE", "engineering").strip().lower()
ISSUE = os.environ.get("ISSUE_NUMBER", "")
BRANCH = os.environ.get("BRANCH", "barrot/task")
LLM_PROVIDER = os.environ.get("BARROT_LLM_PROVIDER", "groq").strip().lower()
if LLM_PROVIDER not in {"groq", "local"}:
    raise ValueError("BARROT_LLM_PROVIDER must be 'groq' or 'local'.")

if LLM_PROVIDER == "local":
    GROQ_ENDPOINT = os.environ.get(
        "BARROT_LLM_BASE_URL",
        "http://127.0.0.1:8080/v1/chat/completions",
    ).strip()
    MODEL = os.environ.get("BARROT_LLM_MODEL", os.environ.get("BRAIN_MODEL", "")).strip()
    if not MODEL:
        raise ValueError(
            "BARROT_LLM_MODEL is required for the local provider; model selection is not guessed."
        )
    local_endpoint = urlsplit(GROQ_ENDPOINT)
    if local_endpoint.scheme != "http" or local_endpoint.hostname not in {
        "127.0.0.1",
        "localhost",
        "::1",
    }:
        raise ValueError(
            "Local inference must use an HTTP loopback endpoint; do not expose llama.cpp publicly."
        )
    GROQ_KEY = os.environ.get("BARROT_LLM_API_KEY", "")
else:
    GROQ_ENDPOINT = os.environ.get(
        "BARROT_LLM_BASE_URL",
        "https://api.groq.com/openai/v1/chat/completions",
    ).strip()
    MODEL = (
        os.environ.get("BARROT_LLM_MODEL", "").strip()
        or os.environ.get("BRAIN_MODEL", "").strip()
        or "openai/gpt-oss-120b"
    )
    GROQ_KEY = os.environ.get("BARROT_LLM_API_KEY", os.environ.get("GROQ_API_KEY", ""))
    remote_endpoint = urlsplit(GROQ_ENDPOINT)
    if remote_endpoint.scheme != "https" or remote_endpoint.hostname != "api.groq.com":
        raise ValueError(
            "Groq credentials may only be sent to https://api.groq.com; "
            "use BARROT_LLM_PROVIDER=local for loopback inference."
        )

MAX_REQUEST_TOKENS = int(os.environ.get("BARROT_MAX_REQUEST_TOKENS", "6500"))
MAX_TPM_TOKENS = int(os.environ.get("BARROT_TPM_TOKEN_BUDGET", "7000"))
MAX_TOOL_RESULT_CHARS = int(os.environ.get("BARROT_MAX_TOOL_RESULT_CHARS", "1800"))
if min(MAX_REQUEST_TOKENS, MAX_TPM_TOKENS, MAX_TOOL_RESULT_CHARS) <= 0:
    raise ValueError("Barrot LLM request, TPM, and tool-result budgets must be positive.")

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
        cleaned = str(path).strip() or "."
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

    def open_file(self, args: dict[str, Any]) -> str:
        """Read a bounded line range from one repository file."""
        try:
            target = self._resolve(args.get("path", ""))
            start = int(args.get("line_start", 1) or 1)
            requested_end = int(args.get("line_end", start + 79) or start + 79)
        except (TypeError, ValueError) as exc:
            return _tool_error(str(exc))
        if start < 1 or requested_end < start:
            return _tool_error("line_start must be >= 1 and line_end must be >= line_start.")
        if not target.exists() or not target.is_file():
            return _tool_error(f"repo_browser file does not exist: {args.get('path', '')}")
        end = min(requested_end, start + 59)
        try:
            lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            return _tool_error(f"could not read repository file: {exc}")
        selected = [
            f"{index + 1}: {lines[index][:300]}"
            for index in range(start - 1, min(end, len(lines)))
        ]
        rendered = "\n".join(selected)
        if len(rendered) > 12000:
            rendered = rendered[:12000] + "\n...[content truncated]"
        return json.dumps(
            {
                "success": True,
                "path": str(target.relative_to(self.root)),
                "line_start": start,
                "line_end": min(end, len(lines)),
                "total_lines": len(lines),
                "content": rendered,
            },
            sort_keys=True,
        )

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
    max_tokens: int = 1536,
    json_mode: bool = False,
    reasoning_effort: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort
    return payload


def _estimate_groq_request_tokens(payload: dict[str, Any]) -> int:
    """Conservative character-based estimate; not a substitute for provider tokenization."""
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    estimated_prompt_tokens = (len(serialized) * 2 + 4) // 5
    return estimated_prompt_tokens + max(0, int(payload.get("max_tokens", 0)))


def _bound_groq_messages(
    messages: list[dict[str, Any]],
    *,
    tools: list[dict[str, Any]] | None,
    max_tokens: int,
    max_request_tokens: int,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Drop oldest complete history/tool groups while preserving system, task and latest tool round."""
    source = list(messages)
    if not source:
        raise RuntimeError("LLM_CONTEXT_BUDGET_EXCEEDED: no request messages were supplied.")

    protected_indices = {i for i, item in enumerate(source) if item.get("role") == "system"}
    user_indices = [i for i, item in enumerate(source) if item.get("role") == "user"]
    latest_user_index = user_indices[-1] if user_indices else len(source) - 1
    protected_indices.add(latest_user_index)

    groups: list[list[int]] = []
    index = 0
    while index < len(source):
        if index in protected_indices:
            index += 1
            continue
        item = source[index]
        tool_calls = item.get("tool_calls") if item.get("role") == "assistant" else None
        if isinstance(tool_calls, list) and tool_calls:
            call_ids = {
                str(call.get("id", ""))
                for call in tool_calls
                if isinstance(call, dict) and call.get("id")
            }
            group = [index]
            cursor = index + 1
            while cursor < len(source) and source[cursor].get("role") == "tool":
                tool_call_id = str(source[cursor].get("tool_call_id", ""))
                if call_ids and tool_call_id not in call_ids:
                    break
                group.append(cursor)
                cursor += 1
            groups.append(group)
            index = cursor
        else:
            groups.append([index])
            index += 1

    latest_tool_group = None
    for group in groups:
        if max(group) <= latest_user_index:
            continue
        if any(
            source[item].get("role") == "assistant" and source[item].get("tool_calls")
            for item in group
        ):
            if latest_tool_group is None or max(group) > max(latest_tool_group):
                latest_tool_group = group

    retained = set(range(len(source)))
    optional_groups = [group for group in groups if group is not latest_tool_group]
    dropped_messages = 0

    def current_candidate() -> tuple[list[dict[str, Any]], int]:
        candidate = [source[item] for item in sorted(retained)]
        payload = _groq_payload(candidate, tools=tools, max_tokens=max_tokens)
        return candidate, _estimate_groq_request_tokens(payload)

    candidate, estimate = current_candidate()
    for group in sorted(optional_groups, key=lambda item: min(item)):
        if estimate <= max_request_tokens:
            break
        for item in group:
            retained.discard(item)
        dropped_messages += len(group)
        candidate, estimate = current_candidate()

    if estimate > max_request_tokens:
        raise RuntimeError(
            "LLM_CONTEXT_BUDGET_EXCEEDED: required system/current-task/recent-tool context "
            f"estimates {estimate} tokens against a {max_request_tokens}-token request budget."
        )
    return candidate, {
        "estimated_tokens": estimate,
        "dropped_messages": dropped_messages,
        "retained_messages": len(candidate),
    }


def _truncate_tool_result(result: str, max_chars: int) -> str:
    text = str(result)
    if len(text) <= max_chars:
        return text
    marker = f"\n[TRUNCATED by Barrot request budget; original_chars={len(text)}]"
    return text[: max(0, max_chars - len(marker))] + marker


class SlidingWindowTokenBudget:
    """Per-process rolling token reservation; fails closed rather than retrying a provider."""

    def __init__(self, *, max_tokens: int = MAX_TPM_TOKENS, window_seconds: float = 60.0):
        if max_tokens <= 0 or window_seconds <= 0:
            raise ValueError("Sliding-window token budget values must be positive.")
        self.max_tokens = int(max_tokens)
        self.window_seconds = float(window_seconds)
        self._events: deque[tuple[float, int]] = deque()
        self._lock = Lock()

    def reserve(self, tokens: int, *, now: float | None = None) -> dict[str, int]:
        amount = max(0, int(tokens))
        timestamp = time.monotonic() if now is None else float(now)
        with self._lock:
            while self._events and timestamp - self._events[0][0] >= self.window_seconds:
                self._events.popleft()
            used = sum(value for _, value in self._events)
            if amount > self.max_tokens or used + amount > self.max_tokens:
                raise RuntimeError(
                    "LLM_RATE_LIMITED_TPM: local rolling budget would exceed "
                    f"{self.max_tokens} tokens per {int(self.window_seconds)} seconds "
                    f"(used={used}, requested={amount}). No provider retry was attempted."
                )
            self._events.append((timestamp, amount))
            return {"used_tokens": used + amount, "remaining_tokens": self.max_tokens - used - amount}


def _send_groq_request(
    payload: dict[str, Any],
    *,
    request_sender: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    _json_mode_retry: bool = False,
) -> dict[str, Any]:
    estimated_tokens = _estimate_groq_request_tokens(payload)
    if estimated_tokens > MAX_REQUEST_TOKENS:
        raise RuntimeError(
            "LLM_CONTEXT_BUDGET_EXCEEDED: request preflight estimated "
            f"{estimated_tokens} tokens against {MAX_REQUEST_TOKENS}."
        )
    if request_sender is not None:
        return request_sender(payload)
    body = json.dumps(payload).encode()
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Barrot-Agent/1.0",
    }
    if GROQ_KEY:
        headers["Authorization"] = "Bearer " + GROQ_KEY
    request = urllib.request.Request(GROQ_ENDPOINT, data=body, headers=headers)
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
        if (
            exc.code == 400
            and "json_validate_failed" in lowered
            and payload.get("response_format")
            and not _json_mode_retry
        ):
            print(
                "Groq rejected strict JSON mode; retrying once without response_format.",
                file=sys.stderr,
            )
            fallback_payload = dict(payload)
            fallback_payload.pop("response_format", None)
            return _send_groq_request(
                fallback_payload,
                request_sender=request_sender,
                _json_mode_retry=True,
            )
        if exc.code in {401, 403}:
            raise RuntimeError(f"LLM authentication failed: {detail}") from exc
        if exc.code in {413, 429} and ("tokens per minute" in lowered or "tpm" in lowered):
            raise RuntimeError(f"LLM_RATE_LIMITED_TPM: Groq HTTP {exc.code}: {detail}") from exc
        if exc.code == 413:
            raise RuntimeError(f"LLM_CONTEXT_BUDGET_EXCEEDED: Groq HTTP 413: {detail}") from exc
        if exc.code == 429 and "tokens per day" in lowered:
            raise RuntimeError(f"LLM_RATE_LIMITED_DAILY: Groq HTTP 429: {detail}") from exc
        if exc.code == 429:
            raise RuntimeError(f"LLM_RATE_LIMITED: Groq HTTP 429: {detail}") from exc
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
        enable_tools: bool = True,
        max_request_tokens: int = MAX_REQUEST_TOKENS,
        max_tool_result_chars: int = MAX_TOOL_RESULT_CHARS,
        token_budget: SlidingWindowTokenBudget | None = None,
    ):
        self.request_sender = request_sender
        self.repo_browser = RepoBrowser(repo_root)
        self.max_tool_rounds = max_tool_rounds
        self.enable_tools = enable_tools
        self.max_request_tokens = min(int(max_request_tokens), MAX_REQUEST_TOKENS)
        self.max_tool_result_chars = min(int(max_tool_result_chars), MAX_TOOL_RESULT_CHARS)
        if self.max_request_tokens <= 0 or self.max_tool_result_chars <= 0:
            raise ValueError("ScriptBrain request and tool-result budgets must be positive.")
        self.token_budget = token_budget or SlidingWindowTokenBudget(max_tokens=MAX_TPM_TOKENS)
        self.last_budget_stats: dict[str, int] = {
            "estimated_tokens": 0,
            "dropped_messages": 0,
            "retained_messages": 0,
            "total_dropped_messages": 0,
        }
        self.tool_funcs = {
            "repo_browser.print_tree": self.repo_browser.print_tree,
            "repo_browser.search": self.repo_browser.search,
            "repo_browser.open_file": self.repo_browser.open_file,
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
                            "path": {"type": "string"},
                            "depth": {"type": "integer", "minimum": 0, "maximum": 6},
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "repo_browser.open_file",
                    "description": "Read up to 60 lines from a real repository file path; paths must remain inside the repository root.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "minLength": 1},
                            "line_start": {"type": "integer", "minimum": 1},
                            "line_end": {"type": "integer", "minimum": 1, "maximum": 100000},
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
                            "path": {"type": "string"},
                            "recursive": {"type": "boolean"},
                            "max_results": {"type": "integer", "minimum": 1, "maximum": max(20, MAX_SEARCH_RESULTS)},
                        },
                        "required": ["query"],
                    },
                },
            },
        ]
        if not self.enable_tools:
            self.tools = []

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
        result = self.tool_funcs[name](arguments)
        return _truncate_tool_result(result, self.max_tool_result_chars)

    def think(self, message: str, history: list[dict[str, str]] | None = None, system: str | None = None, use_tools: bool | None = None, max_output_tokens: int | None = None) -> str:
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        tools_enabled = (
            self.enable_tools if use_tools is None else bool(use_tools) and bool(self.tools)
        )
        output_budget = max_output_tokens or (768 if tools_enabled else 1024)
        for _ in range(self.max_tool_rounds):
            active_tools = self.tools if tools_enabled else None
            bounded_messages, budget_stats = _bound_groq_messages(
                messages,
                tools=active_tools,
                max_tokens=output_budget,
                max_request_tokens=self.max_request_tokens,
            )
            payload = _groq_payload(
                bounded_messages,
                tools=active_tools,
                max_tokens=output_budget,
                json_mode=not tools_enabled,
                reasoning_effort=None if tools_enabled else "low",
            )
            estimated_tokens = _estimate_groq_request_tokens(payload)
            if estimated_tokens > self.max_request_tokens:
                raise RuntimeError(
                    "LLM_CONTEXT_BUDGET_EXCEEDED: bounded request still exceeds the configured limit."
                )
            self.token_budget.reserve(estimated_tokens)
            self.last_budget_stats["estimated_tokens"] = estimated_tokens
            self.last_budget_stats["dropped_messages"] = budget_stats["dropped_messages"]
            self.last_budget_stats["retained_messages"] = budget_stats["retained_messages"]
            self.last_budget_stats["total_dropped_messages"] += budget_stats["dropped_messages"]
            messages = bounded_messages
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


def external_action_approval_valid(action: str, branch: str) -> bool:
    approved_actions = {
        item.strip()
        for item in os.environ.get("BARROT_EXTERNAL_ACTIONS", "").split(",")
        if item.strip()
    }
    return (
        os.environ.get("BARROT_EXTERNAL_ACTION_APPROVED", "").strip().upper() == "YES"
        and bool(os.environ.get("BARROT_EXTERNAL_ACTION_APPROVAL_ID", "").strip())
        and os.environ.get("BARROT_EXTERNAL_ACTION_REPO", "").strip() == REPO
        and os.environ.get("BARROT_EXTERNAL_ACTION_BRANCH", "").strip() == branch
        and action in approved_actions
    )


def require_external_action_approval(action: str, branch: str) -> None:
    if not external_action_approval_valid(action, branch):
        raise RuntimeError(
            f"Blocked external action {action!r} for {REPO}@{branch}: require "
            "BARROT_EXTERNAL_ACTION_APPROVED=YES, a non-empty approval ID, exact repository/branch "
            "scope, and the action in BARROT_EXTERNAL_ACTIONS."
        )


def require_pr_dedup_attestation() -> None:
    if (
        os.environ.get("BARROT_PR_DEDUP_VERIFIED", "").strip().upper() != "YES"
        or not os.environ.get("BARROT_PR_DEDUP_EVIDENCE", "").strip()
    ):
        raise RuntimeError(
            "Branch/PR creation requires BARROT_PR_DEDUP_VERIFIED=YES and "
            "BARROT_PR_DEDUP_EVIDENCE referencing the completed open-PR, path-overlap, "
            "commit-ancestry and prior-work review."
        )


def list_open_pull_requests() -> list[dict[str, Any]]:
    result = run_gh(
        [
            "pr", "list", "--repo", REPO, "--state", "open", "--limit", "1000",
            "--json", "number,title,headRefName,baseRefName",
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Unable to enumerate the complete open-PR inventory; branch/PR creation is blocked. "
            + (result.stderr.strip() or result.stdout.strip())[:1000]
        )
    try:
        items = json.loads(result.stdout or "[]")
    except (TypeError, ValueError) as exc:
        raise RuntimeError("Open-PR inventory was not valid JSON; creation is blocked.") from exc
    if not isinstance(items, list) or len(items) >= 1000:
        raise RuntimeError("Open-PR inventory may be truncated; creation is blocked.")
    return [item for item in items if isinstance(item, dict)]


def _normalize_pr_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def find_open_pr_conflict(branch: str, title: str) -> tuple[dict[str, Any] | None, str | None]:
    wanted_title = _normalize_pr_title(title)
    for item in list_open_pull_requests():
        if str(item.get("headRefName") or "").strip() == branch:
            return item, "branch"
        if _normalize_pr_title(str(item.get("title") or "")) == wanted_title:
            return item, "title"
    return None, None


def build_repository_watchdog() -> DefensiveWatchdog:
    allowed = {
        Capability.READ,
        Capability.WRITE,
        Capability.EXECUTE,
        Capability.NETWORK,
    }
    if external_action_approval_valid("repository_sync", BRANCH):
        allowed.add(Capability.EXTERNAL_ACTION)
    return DefensiveWatchdog(
        ROOT,
        repository=REPO,
        task=TITLE,
        allowed_capabilities=allowed,
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
                "1000",
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
    """Reuse an existing task branch; require approval and dedup evidence before creating one."""
    existing, conflict_kind = find_open_pr_conflict(branch, TITLE)
    if existing and conflict_kind == "title" and existing.get("headRefName") != branch:
        raise RuntimeError(
            f"Open PR #{existing.get('number')} already has this objective on another branch; "
            "reuse/reconcile it instead of creating another branch."
        )
    local = run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        check=False,
        quiet=True,
    )
    remote = run(
        ["git", "ls-remote", "--exit-code", "--heads", "origin", branch],
        check=False,
        quiet=True,
    )
    branch_exists = local.returncode == 0 or remote.returncode == 0
    if not branch_exists:
        require_external_action_approval("repository_branch_create", branch)
        require_pr_dedup_attestation()
    try:
        safe_checkout_branch(ROOT, branch)
    except Exception as exc:
        raise RuntimeError(f"Safe task-branch checkout blocked: {exc}") from exc


def post_issue_comment(message: str) -> None:
    if not ISSUE or ISSUE == "0":
        return
    import tempfile

    with tempfile.TemporaryDirectory(prefix="barrot_comment_") as tmp_dir:
        comment_path = Path(tmp_dir) / "barrot_comment_body.md"
        comment_path.write_text(message[:60000], encoding="utf-8")
        result = run_gh(
            ["issue", "comment", ISSUE, "--repo", REPO, "--body-file", str(comment_path)]
        )
        if result.returncode != 0:
            print(result.stderr[:3000], file=sys.stderr)


def _cycle_dict(cycle: Any) -> dict[str, Any]:
    if isinstance(cycle, dict):
        return cycle
    if hasattr(cycle, "to_dict"):
        return cycle.to_dict()
    raise TypeError("cycle must be a dict or provide to_dict()")


def build_project_identity(repo: str) -> dict[str, Any]:
    return ProjectIdentity.from_seed(repo).to_dict()


def _work_dict(payload: dict[str, object] | Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    if hasattr(payload, "to_dict"):
        return payload.to_dict()
    raise TypeError("payload must be a dict or provide to_dict()")


def _extract_cycle_data(payload: dict[str, object] | Any) -> dict[str, Any]:
    payload_dict = _work_dict(payload)
    repair_cycle = payload_dict.get("repair_cycle")
    if isinstance(repair_cycle, dict) and repair_cycle:
        return repair_cycle
    return _cycle_dict(payload_dict)


def _is_research_cycle(payload: dict[str, Any]) -> bool:
    return "problem_id" in payload and "sources" in payload and "claims" in payload


def create_pull_request(cycle: dict[str, object] | Any) -> None:
    cycle_data = _extract_cycle_data(cycle)
    safe_title = TITLE.replace('"', "'").replace("`", "'").replace("$", "")
    head_branch = (
        str(cycle_data.get("commit", {}).get("branch", "")).strip()
        or str(cycle_data.get("issue", {}).get("branch", "")).strip()
        or BRANCH
    )
    existing, conflict_kind = find_open_pr_conflict(head_branch, f"Barrot: {safe_title}")
    if existing:
        if conflict_kind == "branch":
            print(f"EXISTING_OPEN_PR=#{existing.get('number')}; reusing branch; no duplicate PR created.")
            return
        raise RuntimeError(
            f"Open PR #{existing.get('number')} already has this objective; update/reconcile it instead."
        )
    require_external_action_approval("pull_request_create", head_branch)
    require_pr_dedup_attestation()
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
    import tempfile

    with tempfile.TemporaryDirectory(prefix="barrot_pr_") as tmp_dir:
        pr_path = Path(tmp_dir) / "barrot_pr_body.md"
        pr_path.write_text("\n".join(body), encoding="utf-8")
        # GitHub CLI must read the body before the temporary directory is removed.
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
                "--draft",
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


def persist_scientific_discovery(cycle: dict[str, object] | Any) -> dict[str, Any]:
    """Commit research evidence to the resumable task branch and open a draft PR."""
    payload = _work_dict(cycle)
    latest = write_collaboration_record(payload)
    cycle_id = re.sub(r"[^A-Za-z0-9._-]", "_", str(payload.get("cycle_id") or "unknown"))
    per_cycle = latest.parent / f"{cycle_id}.json"
    paths = [str(latest.relative_to(ROOT)), str(per_cycle.relative_to(ROOT))]
    safe_title = TITLE.replace(chr(96), " ").replace('"', "'").replace("$", " ").replace("\n", " ").replace("\r", " ").strip()[:180] or "Scientific discovery"
    existing_pr, conflict_kind = find_open_pr_conflict(BRANCH, f"Barrot research: {safe_title}")
    if existing_pr and conflict_kind == "title" and existing_pr.get("headRefName") != BRANCH:
        raise RuntimeError(
            f"Open PR #{existing_pr.get('number')} already covers this research objective on another branch."
        )
    require_external_action_approval("repository_sync", BRANCH)
    require_pr_dedup_attestation()
    staged = run(["git", "add", "--", *paths], check=False)
    if staged.returncode != 0:
        raise RuntimeError(staged.stderr.strip() or "Unable to stage scientific-discovery evidence")
    diff = run(["git", "diff", "--cached", "--quiet"], check=False, quiet=True)
    commit_sha = run(["git", "rev-parse", "HEAD"], quiet=True).stdout.strip()
    if diff.returncode == 1:
        run(["git", "commit", "-m", f"Barrot: persist scientific research cycle {cycle_id}"])
        run(["git", "push", "--set-upstream", "origin", BRANCH])
        commit_sha = run(["git", "rev-parse", "HEAD"], quiet=True).stdout.strip()
    elif diff.returncode != 0:
        raise RuntimeError("Unable to determine whether scientific-discovery evidence changed")
    else:
        remote = run(["git", "rev-parse", f"origin/{BRANCH}"], check=False, quiet=True)
        if remote.returncode != 0:
            raise RuntimeError("No new evidence to commit and no remote task branch exists")

    pr_body = (
        f"Barrot scientific-discovery evidence for issue #{ISSUE}.\n\n"
        f"- cycle_id: {cycle_id}\n"
        f"- problem_id: {payload.get('problem_id')}\n"
        f"- cycle_status: {payload.get('status')}\n"
        f"- acceptance_gate_passed: {payload.get('acceptance_gate_passed')}\n"
        f"- unresolved_questions: {len(payload.get('unresolved_questions', []))}\n\n"
        "This is an evidence-preserving draft. It makes no claim that the Millennium problem is solved."
    )
    existing_pr, conflict_kind = find_open_pr_conflict(BRANCH, f"Barrot research: {safe_title}")
    if existing_pr:
        if conflict_kind == "branch":
            return {
                "record_path": str(latest.relative_to(ROOT)),
                "commit_sha": commit_sha,
                "remote_persisted": True,
                "draft_pr": f"reused existing open PR #{existing_pr.get('number')}",
            }
        raise RuntimeError(
            f"Open PR #{existing_pr.get('number')} already covers this research objective; no new PR created."
        )
    require_external_action_approval("pull_request_create", BRANCH)
    require_pr_dedup_attestation()
    import tempfile
    with tempfile.TemporaryDirectory(prefix="barrot_research_pr_") as tmp_dir:
        body_path = Path(tmp_dir) / "research_pr_body.md"
        body_path.write_text(pr_body, encoding="utf-8")
        result = run_gh([
            "pr", "create", "--draft", "--repo", REPO,
            "--title", f"Barrot research: {safe_title}",
            "--body-file", str(body_path), "--head", BRANCH, "--base", "main",
        ])
    combined = (result.stdout + "\n" + result.stderr).lower()
    if result.returncode != 0 and "already exists" not in combined:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Unable to create draft research PR")
    return {
        "record_path": str(latest.relative_to(ROOT)),
        "commit_sha": commit_sha,
        "remote_persisted": True,
        "draft_pr": result.stdout.strip() or "existing draft PR",
    }


def write_collaboration_record(cycle: dict[str, object] | Any) -> Path:
    payload = _work_dict(cycle)
    if _is_research_cycle(payload):
        record_dir = ROOT / ".barrot" / "collaboration_records"
        record_dir.mkdir(parents=True, exist_ok=True)
        record = {
            "work_bundle": "scientific_discovery",
            "cycle_id": payload.get("cycle_id"),
            "problem_id": payload.get("problem_id"),
            "actions_performed": payload.get("state_history", []),
            "results": {
                "status": payload.get("status"),
                "problem_resolution_status": payload.get("problem_resolution_status"),
                "acceptance_gate_passed": payload.get("acceptance_gate_passed"),
            },
            "evidence": {
                "problem": payload.get("problem", {}),
                "sources": payload.get("sources", []),
                "claims": payload.get("claims", []),
                "evidence": payload.get("evidence", []),
                "tracks": payload.get("tracks", []),
                "cross_pollination": payload.get("cross_pollination", []),
                "convergence_analysis": payload.get("convergence_analysis", {}),
                "formal_verifications": payload.get("formal_verifications", []),
                "adversarial_reviews": payload.get("adversarial_reviews", []),
                "unresolved_questions": payload.get("unresolved_questions", []),
                "artifacts": payload.get("artifacts", []),
            },
            "failures": payload.get("failure"),
            "final_state": payload.get("current_state"),
            "remaining_blockers": payload.get("unresolved_questions", []),
        }
        latest = record_dir / "latest_scientific_discovery.json"
        latest.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        cycle_id = re.sub(r"[^A-Za-z0-9._-]", "_", str(payload.get("cycle_id") or "unknown"))
        per_cycle = record_dir / f"{cycle_id}.json"
        per_cycle.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        return latest

    cycle_data = _extract_cycle_data(payload)
    # Engineering runtime evidence is local execution state, not a tracked handoff.
    # Keep it under .git so it cannot overwrite the historical .barrot record or
    # leave generated files that contaminate the user's worktree.
    record_dir = ROOT / ".git" / "barrot_repair" / "collaboration_records"
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
            "queue_status": payload.get("status"),
            "queue_advanced": payload.get("queue_advanced"),
        },
        "failures": cycle_data.get("failure"),
        "evidence": {
            "issue": cycle_data.get("issue", {}),
            "repair_plan": cycle_data.get("repair_plan", {}),
            "changes": cycle_data.get("changes", []),
            "commit": cycle_data.get("commit", {}),
            "sync": cycle_data.get("sync", []),
            "project_identity": payload.get("project_identity", {}),
            "work_queue": {
                "work_id": payload.get("work_id"),
                "current_state": payload.get("current_state"),
                "retry_history": payload.get("retry_history", []),
                "sync_operation": payload.get("sync_operation", {}),
            },
        },
        "commits": [cycle_data.get("commit", {})] if cycle_data.get("commit", {}).get("sha") else [],
        "remote_verification": cycle_data.get("sync", []),
        "final_state": payload.get("current_state", cycle_data.get("current_state")),
        "remaining_blockers": payload.get("sync_operation", {}) or cycle_data.get("failure"),
        "source_materials": {
            "night_watcher_failure": {
                "summary": "Repeated unchanged transfer checks ended with empty path/namespace and required safe blocking without overwriting the last valid project identity.",
                "requirements": [
                    "preserve last valid project identity",
                    "reject empty path/namespace observations",
                    "bound retries and backoff",
                    "persist retry history and required external action",
                ],
            },
            "copilot_analysis": {
                "source": ".barrot/collaboration_records/autonomous_takeover_ready.json",
                "summary": "Existing Barrot repair takeover already required evidence-gated completion, durable cycle persistence, and tool-conflict-safe repair planning.",
            },
            "barrot_requirements": {
                "source": "barrot_agent/orchestration/repository_repair.py",
                "summary": "The authoritative repair controller requires reproduction, guarded patching, validation, commit evidence, remote verification, and completion gating.",
            },
            "cross_correlation": {
                "agreements": [
                    "state changes require evidence",
                    "failures must block false completion",
                    "durable persistence and safe resume are required",
                ],
                "missing_capabilities_filled": [
                    "durable project identity preservation",
                    "progress-aware external retry handling",
                    "queue advancement gating on verified repair success",
                ],
            },
        },
    }
    latest = record_dir / "latest_repository_repair.json"
    latest.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    cycle_id = re.sub(r"[^A-Za-z0-9._-]", "_", str(cycle_data.get("cycle_id") or "unknown"))
    per_cycle = record_dir / f"{cycle_id}.json"
    per_cycle.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    return latest


def _parse_scientific_track_output(raw: str, brain: ScriptBrain, request: dict[str, Any]) -> dict[str, Any]:
    def decode_object(candidate: str) -> dict[str, Any]:
        content = candidate.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
            if content.endswith("```"):
                content = content[:-3].strip()
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("Model response must be a JSON object.")

        required_keys = ("findings", "open_questions", "counterarguments", "recommended_checks")
        if set(parsed) != set(required_keys):
            missing = sorted(set(required_keys) - set(parsed))
            unexpected = sorted(set(parsed) - set(required_keys))
            raise ValueError(
                f"Model response keys mismatch (missing={missing}, unexpected={unexpected})."
            )

        for key in required_keys:
            values = parsed[key]
            if not isinstance(values, list):
                raise ValueError(f"Model response field {key!r} must be an array.")
            if len(values) > 3:
                raise ValueError(f"Model response field {key!r} exceeds the three-item limit.")
            for index, value in enumerate(values):
                if not isinstance(value, str):
                    raise ValueError(f"Model response field {key!r}[{index}] must be a string.")
                if len(value) > 300:
                    raise ValueError(f"Model response field {key!r}[{index}] exceeds 300 characters.")

        return parsed

    try:
        return decode_object(raw)
    except (json.JSONDecodeError, ValueError) as first_error:
        track = request.get("track") if isinstance(request.get("track"), dict) else {}
        repair_request = {
            "task": "Retry the research-track response as compact valid JSON.",
            "track_id": track.get("track_id", "unknown"),
            "required_keys": ["findings", "open_questions", "counterarguments", "recommended_checks"],
            "limits": {
                "maximum_items_per_array": 3,
                "maximum_characters_per_item": 300,
                "all_values_must_be_strings": True,
            },
            "invalid_response": raw[:6000],
            "instruction": (
                "Preserve the meaning only where it is clear. Do not invent evidence or citations. "
                "If the original is unusable, return empty arrays and explain uncertainty in open_questions."
            ),
        }
        retry_raw = brain.think(
            json.dumps(repair_request, sort_keys=True),
            system=(
                "Return one syntactically valid JSON object only. Required keys are findings, open_questions, "
                "counterarguments, recommended_checks; each value must be an array of at most three strings, "
                "each at most 300 characters. No markdown, no prose outside JSON, no invented evidence."
            ),
        )
        try:
            return decode_object(retry_raw)
        except (json.JSONDecodeError, ValueError) as retry_error:
            raise RuntimeError(
                "Model returned invalid response after one compact retry: "
                f"{str(retry_error)[:250]}; initial response rejected: {str(first_error)[:250]}"
            ) from retry_error

def build_read_only_audit_snapshot() -> dict[str, Any]:
    """Collect bounded, read-only Git and Actions evidence for audit-only tasks."""
    snapshot: dict[str, Any] = {}
    commands = {
        "working_tree": ["git", "status", "--short", "--branch"],
        "head": ["git", "rev-parse", "HEAD"],
        "recent_history": [
            "git", "log", "--all", "-n", "30", "--date=short",
            "--pretty=format:%h|%ad|%d|%s",
        ],
        "branch_refs": [
            "git", "for-each-ref", "--sort=-committerdate",
            "--format=%(refname:short)|%(objectname:short)|%(committerdate:short)|%(subject)",
            "refs/heads", "refs/remotes/origin",
        ],
        "geometry_checkpoint_vs_main": [
            "git", "diff", "--stat",
            "origin/main...origin/barrot/mesh-topology-obj-triangulation-20261024",
        ],
        "geometry_checkpoint_vs_fresh_main": [
            "git", "diff", "--stat",
            "origin/barrot/mesh-topology-obj-triangulation-20261024...origin/barrot/mesh-topology-fresh-main-20261026-0837",
        ],
    }
    outputs: dict[str, str] = {}
    for name, args in commands.items():
        result = run(args, check=False, quiet=True)
        limit = 1200 if name.startswith("geometry_") else 4000
        outputs[name] = result.stdout.strip() if name == "branch_refs" else result.stdout.strip()[:limit]
        if result.returncode != 0:
            outputs[name] = (
                f"UNAVAILABLE (exit={result.returncode}): "
                + (result.stderr.strip()[:1000] or result.stdout.strip()[:1000])
            )
    snapshot["working_tree"] = outputs["working_tree"][:1200]
    snapshot["head"] = outputs["head"][:200]
    snapshot["recent_history"] = "\\n".join(outputs["recent_history"].splitlines()[:4])

    branch_output = outputs["branch_refs"]
    relevant_markers = (
        "mesh-topology", "structural-core", "mmi", "tool-call-resilience",
        "barrot/task-1167",
    )
    if branch_output.startswith("UNAVAILABLE"):
        snapshot["branch_count"] = None
        snapshot["relevant_branch_heads"] = branch_output
    else:
        branch_lines = branch_output.splitlines()
        relevant_branches = [
            line for line in branch_lines
            if line.split("|", 1)[0] in {"main", "origin/main"}
            or any(marker in line.split("|", 1)[0].lower() for marker in relevant_markers)
        ]
        snapshot["branch_count"] = len(branch_lines)
        snapshot["relevant_branch_heads"] = relevant_branches[:10]
    snapshot["geometry_diffs"] = {
        "checkpoint_vs_main": outputs["geometry_checkpoint_vs_main"],
        "checkpoint_vs_fresh_main": outputs["geometry_checkpoint_vs_fresh_main"],
    }

    actions = run_gh(["api", f"repos/{REPO}/actions/runs?per_page=100"])
    if actions.returncode == 0:
        try:
            payload = json.loads(actions.stdout)
            runs = payload.get("workflow_runs", [])
            def summarize(item: dict[str, Any]) -> dict[str, Any]:
                return {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "event": item.get("event"),
                    "status": item.get("status"),
                    "conclusion": item.get("conclusion"),
                    "created_at": item.get("created_at"),
                    "branch": item.get("head_branch"),
                    "title": item.get("display_title"),
                    "url": item.get("html_url"),
                    "sha": item.get("head_sha"),
                }
            recent = [summarize(item) for item in runs[:2]]
            relevant = [
                summarize(item) for item in runs
                if any(token in (
                    str(item.get("display_title", "")) + " "
                    + str(item.get("name", "")) + " "
                    + str(item.get("head_branch", ""))
                ).lower() for token in ("mesh", "geometry", "triangulation", "tetrahedron", "audit", "barrot agent"))
            ]
            snapshot["actions"] = {
                "total_count": payload.get("total_count"),
                "recent_runs": recent,
                "relevant_runs": relevant[:4],
            }
        except (TypeError, ValueError, AttributeError) as exc:
            snapshot["actions"] = {"status": "UNPARSEABLE", "error": type(exc).__name__}
    else:
        snapshot["actions"] = {
            "status": "UNAVAILABLE",
            "exit_code": actions.returncode,
            "error": actions.stderr.strip()[:1000],
        }
    return snapshot


def build_read_only_source_snapshot() -> dict[str, Any]:
    """Return compact, read-only source excerpts for one-shot audit inference."""
    specs = [
        (".github/workflows/barrot-agent.yml", ("workflow_dispatch", "barrot-task", "permissions:", "scripts/barrot_agent.py"), 6),
        ("barrot_agent/rendering/mesh_topology.py", ("def analyze_mesh_topology", "degenerate_triangles", "is_watertight", "topology_status"), 6),
        ("barrot_agent/rendering/obj_mesh_loader.py", ("triangulate_polygon", "triangulation", "EAR_CLIPPING"), 6),
        ("barrot_agent/rendering/polygon_triangulation.py", ("def triangulate_polygon", "convex", "ear"), 6),
        ("barrot_agent/rendering/quality_metrics.py", ("def _check_geometry", "NOT_ASSESSED", "mesh_vertices is None"), 6),
        ("tests/test_mesh_topology.py", ("tetrahedron", "degenerate", "nonmanifold"), 4),
        ("tests/test_obj_mesh_loader.py", ("tetrahedron", "concave", "degenerate_triangles"), 6),
        ("tests/test_polygon_triangulation.py", ("concave", "area"), 4),
        ("barrot_agent/orchestration/repository_repair.py", ("def _barrett_autonomous_audit", "report_only", "PATCHING", "COMMITTING", "REMOTE_VERIFICATION"), 6),
        ("scripts/barrot_agent.py", ("def think(", "def build_read_only_audit_snapshot", "def is_explicit_read_only_audit_task", "READ_ONLY_AUDIT=COMPLETE", "BundleEngineeringController"), 6),
        ("scripts/barrot_repo_state_manifest.py", ("manifest", "sha256", "source"), 4),
        ("barrot_agent/repo_state_corroborator.py", ("stale", "missing", "corrobor"), 4),
        ("barrot_agent/orchestration/bundle_delivery.py", ("checksum", "verify", "def "), 4),
    ]
    result: dict[str, Any] = {}
    total_chars = 0
    for relative_path, terms, max_lines in specs:
        path = ROOT / relative_path
        if not path.is_file():
            result[relative_path] = {"status": "MISSING"}
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            result[relative_path] = {"status": "UNAVAILABLE", "error": type(exc).__name__}
            continue
        selected: set[int] = set()
        for index, line in enumerate(lines):
            if any(term.casefold() in line.casefold() for term in terms):
                selected.update(range(max(0, index - 1), min(len(lines), index + 2)))
        excerpts = sorted(selected)[:max_lines]
        rendered = "\n".join(f"{index + 1}: {lines[index][:130]}" for index in excerpts)
        allowance = max(0, 9000 - total_chars)
        rendered = rendered[:allowance]
        result[relative_path] = {
            "status": "READ",
            "total_lines": len(lines),
            "excerpt": rendered,
        }
        total_chars += len(rendered)
        if total_chars >= 9000:
            break
    test_paths = [
        "tests/test_mmi_contract.py",
        "tests/test_mmi_execution.py",
        "tests/test_mmi_integration.py",
        "tests/test_verified_bundle_delivery.py",
        "tests/test_bundle_delivery.py",
        "tests/test_termux_self_drop.py",
        "tests/test_external_deploys_require_confirmation.py",
    ]
    result["test_file_presence"] = {
        path: (ROOT / path).is_file() for path in test_paths
    }
    return result


def is_explicit_read_only_audit_task(title: str, body: str) -> bool:
    """Recognize tasks that explicitly forbid repository implementation changes."""
    normalized = f"{title}\n{body}".casefold()
    return (
        "audit and recommend only" in normalized
        and "no implementation changes are authorized by this issue" in normalized
    )


def build_primary_mission_dispatch() -> dict[str, Any]:
    """Return the next verified primary-mission goal without provider or repository writes.

    This mode is deterministic and read-only. It is suitable for an explicitly
    invoked mission-planning step; it does not execute the goal or authorize
    external actions.
    """
    registry = MissionRegistry()
    manifest = registry.manifest
    foundation = manifest["foundation"]
    if manifest["status"] != "active":
        return {
            "status": "NOT_ACTIVE",
            "mission_id": registry.mission_id,
            "priority": 1,
            "foundation": foundation["name"],
            "next_goal": None,
            "provider_calls": False,
            "repository_mutation": False,
            "external_actions_authorized": False,
        }

    learning_store = VerifiedLearningStore(ROOT / "data" / "evolution" / "verified_lessons.jsonl")
    curriculum = LearningCurriculum(
        workspace=str(ROOT),
        learning_store=learning_store,
        mission_registry=registry,
    )
    goal = curriculum.next_goal()
    if not isinstance(goal, str) or not goal.strip():
        raise RuntimeError("Primary mission curriculum returned no active goal.")
    topic = re.search(r"(?m)^MISSION_TOPIC_ID:\s*([a-zA-Z0-9_.-]+)\s*$", goal)
    if topic is None:
        raise RuntimeError("Primary mission goal is missing its topic identifier.")

    return {
        "status": "READY",
        "dispatch_mode": "read_only_mission_plan",
        "mission_id": registry.mission_id,
        "priority": 1,
        "topic_id": topic.group(1),
        "foundation": {
            "id": foundation["id"],
            "name": foundation["name"],
            "preserve": foundation["preserve"],
        },
        "next_goal": goal,
        "acceptance_criteria": list(manifest["acceptance_criteria"]),
        "guardrails": list(manifest["guardrails"]),
        "provider_calls": False,
        "repository_mutation": False,
        "external_actions_authorized": False,
    }


def _is_groq_rate_limit_error(error: BaseException) -> bool:
    rendered = f"{type(error).__name__}: {error}".lower()
    return any(
        marker in rendered
        for marker in (
            "groq http 413",
            "groq http 429",
            "rate_limit_exceeded",
            "tokens per minute",
            "tpm",
            "tokens per day",
            "per-minute token limit",
            "daily token limit",
            "rate limit exhausted",
        )
    )


def _build_deterministic_rate_limit_report(
    *,
    task_title: str,
    issue_number: str,
    error: BaseException,
    audit_context: dict[str, str],
    snapshot: dict[str, Any],
) -> str:
    context = {
        "repository_inventory": str(audit_context.get("inventory", ""))[:5000],
        "github_context": str(audit_context.get("github_context", ""))[:9000],
        "targeted_file_context": str(audit_context.get("file_context", ""))[:2500],
        "directory_context": str(audit_context.get("directory_context", ""))[:2500],
        "read_only_snapshot": snapshot,
    }
    return (
        "## Barrot deterministic fallback — provider rate limit\n\n"
        "**Status:** `BLOCKED_PROVIDER_RATE_LIMIT`\n\n"
        f"**Task:** {task_title}\n"
        f"**Issue:** #{issue_number if issue_number and issue_number != '0' else 'not supplied'}\n"
        f"**Provider failure:** {type(error).__name__}: {str(error)[:1000]}\n\n"
        "### Deterministic work completed\n"
        "- Repository file inventory and targeted file/directory context were collected.\n"
        "- Read-only Git branch, HEAD, recent-history, working-tree and Actions evidence was attempted; unavailable fields are labeled.\n"
        "- Recent GitHub Actions evidence was collected where the GitHub CLI was available.\n"
        "- Any available open-PR/issue context is preserved below; it is not model-interpreted.\n\n"
        "### Evidence snapshot\n"
        "```json\n"
        + json.dumps(context, ensure_ascii=False, sort_keys=True, indent=2, default=str)[:26000]
        + "\n```\n\n"
        "### Execution boundary\n"
        "No LLM-backed bundle was accepted. No repository source file was changed; no commit, push, pull request, merge, deployment, secret operation, paper trade or financial action was performed. "
        "Repository repair is **not complete** and this task remains blocked. Retry the provider after the rate-limit window resets; retain this deterministic evidence rather than inventing a model-backed result."
    )


def main() -> None:
    global MAX_SEARCH_RESULTS
    if TASK_MODE == "mission":
        print(json.dumps(build_primary_mission_dispatch(), indent=2, sort_keys=True))
        return

    configure_git()
    checkout_branch(BRANCH)

    if should_route_scientific_discovery(TASK_MODE, TITLE, TASK):
        if not GROQ_KEY:
            raise SystemExit("GROQ_API_KEY not set; refusing to label metadata-only research as live scientific discovery.")
        brain = ScriptBrain(enable_tools=False)

        def execute_scientific_track(track):
            request = {
                "task": "Analyze this research track using the supplied record only as context.",
                "track": track.to_dict(),
                "rules": [
                    "Do not claim that a theorem is proved, accepted, or independently verified.",
                    "Do not invent citations, source URLs, experiments, or formal proof results.",
                    "Separate hypotheses from established source-backed facts.",
                    "Return concise findings, open questions, counterarguments, and recommended checks.",
                    "Any model-generated finding is provisional and must remain unverified until separately corroborated.",
                    "Return no more than three items per array, each no longer than 300 characters.",
                ],
                "output_limits": {"items_per_array": 3, "characters_per_item": 300},
                "output_schema": {
                    "findings": ["string"],
                    "open_questions": ["string"],
                    "counterarguments": ["string"],
                    "recommended_checks": ["string"],
                },
            }
            raw = brain.think(
                json.dumps(request, sort_keys=True),
                system=(
                    "You are Barrot's scientific research worker. Return one JSON object only with "
                    "string arrays named findings, open_questions, counterarguments, and recommended_checks. "
                    "Do not upgrade claim status or represent model output as independent verification. "
                    "Keep each string under 300 characters and each array to at most three items."
                ),
            )
            parsed = _parse_scientific_track_output(raw, brain, request)
            return {"provider": f"groq:{MODEL}", "result": parsed}

        cycle = ScientificDiscoveryController(workspace=ROOT).run(
            select_scientific_problem_adapter(TITLE, TASK),
            track_executor=execute_scientific_track,
        )
        rendered = json.dumps(cycle.to_dict(), indent=2)
        print(rendered)
        persistence = persist_scientific_discovery(cycle)
        track_records = [
            track.get("execution_records", [])[-1]
            for track in cycle.to_dict().get("tracks", [])
            if track.get("execution_records")
        ]
        provider_execution_failed = (
            not track_records
            or any(
                record.get("state") != "COMPLETE"
                or not record.get("response", {}).get("provider_backed", False)
                for record in track_records
            )
        )
        if cycle.status not in {"complete", "no_solution_claim"} or provider_execution_failed:
            post_issue_comment(
                "Barrot scientific discovery failed safely; provider-backed track execution did not fully pass.\n\n"
                + json.dumps({"persistence": persistence}, indent=2)
                + "\n\n```json\n"
                + rendered[:55000]
                + "\n```"
            )
            raise SystemExit(1)
        post_issue_comment(
            "Barrot scientific discovery recorded and persisted to the task branch.\n\n"
            + json.dumps({"persistence": persistence}, indent=2)
            + "\n\n```json\n"
            + rendered[:55000]
            + "\n```"
        )
        return

    if not GROQ_KEY:
        raise SystemExit("GROQ_API_KEY not set")

    work_id = f"{ISSUE or 'manual'}:{BRANCH}"
    brain = ScriptBrain()
    bundle_brain = ScriptBrain(enable_tools=False)
    audit_context = build_audit_context(TITLE, TASK)
    if is_explicit_read_only_audit_task(TITLE, TASK):
        audit_request = {
            "objective": TITLE,
            "task_body_summary": "Read-only repository-wide audit. Known geometry checkpoint: barrot/mesh-topology-obj-triangulation-20261024 at ab362f9fc9512cd7ffea312d24978f11bbc2de3e; duplicate candidate branch barrot/mesh-topology-obj-triangulation-20261024-115709. Investigate the reported tetrahedron degenerate-triangle/watertightness discrepancy, concave OBJ triangulation and metadata, missing-mesh NOT_ASSESSED behavior, CI evidence, agent repair safety, MMI/provenance, and delivery. Return prioritized next steps with acceptance criteria.",
            "repository_context": {
                "inventory": str(audit_context.get("inventory", ""))[:500],
                "github_context": str(audit_context.get("github_context", ""))[:500],
                "note": str(audit_context.get("note", ""))[:200],
            },
            "live_read_only_snapshot": build_read_only_audit_snapshot(),
            "live_source_snapshot": build_read_only_source_snapshot(),
            "required_sections": [
                "Executive status and critical risks",
                "Repository, branch, and commit map",
                "CI/workflow configuration versus actual run evidence",
                "Geometry discrepancy, triangulation, and NOT_ASSESSED behavior",
                "Agent safety, MMI/provenance, and delivery readiness",
                "Prioritized next actions with acceptance criteria",
                "Checks blocked or not performed, with reasons",
            ],
            "rules": [
                "This is a read-only audit. Do not repair, patch, write files, install dependencies, commit, push, merge, open pull requests, or delete/overwrite/reset/clean anything.",
                "Inspect repository files using only the available read-only repo_browser tools and the supplied repository context.",
                "Never claim a test ran or passed unless execution output or a specific GitHub Actions run proves it.",
                "Separate CONFIRMED, LIKELY, UNVERIFIED, and BLOCKED findings.",
                "Cite exact paths, relevant lines, SHAs, workflow run IDs/URLs, and actual output when available.",
                "If the local checkout cannot establish remote or historical facts, state the limitation rather than guessing.",
                "Return the complete evidence-backed report, not a plan to perform the audit later.",
            ],
        }
        audit_system = (
            "You are Barrot performing a strictly read-only repository audit. "
            "You are given a compact live Git/Actions snapshot and source excerpts; do not call tools. "
            "Return one JSON object with a single string field named report. That string must contain the complete Markdown audit. "
            "Do not execute repair logic or imply changes were made. Do not claim tests ran unless the supplied Actions evidence proves it. "
            "Separate CONFIRMED, LIKELY, UNVERIFIED, and BLOCKED findings. If evidence is absent, say so."
        )
        try:
            audit_brain = ScriptBrain(enable_tools=False, max_tool_rounds=1)
            raw_report = audit_brain.think(
                json.dumps(audit_request, ensure_ascii=False, sort_keys=True),
                system=audit_system,
                use_tools=False,
                max_output_tokens=2048,
            )
            try:
                parsed_report = json.loads(raw_report)
                report = parsed_report.get("report", raw_report) if isinstance(parsed_report, dict) else raw_report
            except (TypeError, ValueError):
                report = raw_report
        except Exception as exc:
            if _is_groq_rate_limit_error(exc):
                try:
                    deterministic_snapshot = {
                        "git_and_actions": build_read_only_audit_snapshot(),
                        "source_excerpt_status": "already_collected_for_the_failed_read_only_audit",
                    }
                except Exception as snapshot_error:
                    deterministic_snapshot = {
                        "status": "UNAVAILABLE",
                        "error": f"{type(snapshot_error).__name__}: {str(snapshot_error)[:500]}",
                    }
                message = _build_deterministic_rate_limit_report(
                    task_title=TITLE,
                    issue_number=ISSUE,
                    error=exc,
                    audit_context=audit_context,
                    snapshot=deterministic_snapshot,
                )
            else:
                message = (
                    "Barrot read-only audit failed safely; repository repair was not started.\n\n"
                    f"Failure: {type(exc).__name__}: {str(exc)[:1200]}"
                )
            post_issue_comment(message)
            raise SystemExit(message) from exc
        if not report.strip():
            message = "Barrot read-only audit returned an empty report; repository repair was not started."
            post_issue_comment(message)
            raise SystemExit(message)
        post_issue_comment("## Barrot Read-Only Audit Report\n\n" + report)
        print("READ_ONLY_AUDIT=COMPLETE")
        return

    lifecycle_store = BundleLifecycleStore(ROOT)
    bundle_constraints = [
        "Preserve the exact user objective and constraints across revisions.",
        "Do not perform consequential external actions without required authorization.",
        "Never claim completion without recorded validation, commit, remote verification, and resolution evidence.",
        "Use the existing RepositoryRepairController and WorkQueueController; do not create a parallel executor.",
        "Bound retries, persist state and evidence, and stop safely on invalid output or failed gates.",
    ]
    # Quote the user's explicit authorization boundaries (if the task states them).
    # Without such a section the gate's AUTHORIZATION_CONSTRAINT_MISSING check still applies.
    bundle_constraints.extend(extract_authorization_boundaries(TASK))
    request_fingerprint = "sha256:" + hashlib.sha256(
        "\\0".join([REPO, BRANCH, TITLE.strip(), TASK.strip()]).encode("utf-8")
    ).hexdigest()
    saved_plan = lifecycle_store.load(work_id)
    bundle_result = None
    if (
        saved_plan
        and saved_plan.get("request_fingerprint") == request_fingerprint
        and saved_plan.get("status") == "READY_FOR_EXECUTION_REVIEW"
        and isinstance(saved_plan.get("bundle"), dict)
        and saved_plan["bundle"].get("objective") == TITLE.strip()
        and saved_plan["bundle"].get("constraints") == bundle_constraints
    ):
        saved_review = review_work_bundle(saved_plan["bundle"])
        if saved_review.valid:
            bundle_result = BundleEngineeringResult(
                status="READY_FOR_EXECUTION_REVIEW",
                bundle=saved_plan["bundle"],
                review=saved_review,
                attempts=tuple(saved_plan.get("attempts") or ()),
            )
            print("Resuming persisted bundle:", saved_review.fingerprint)

    if bundle_result is None:
        try:
            bundle_result = BundleEngineeringController(bundle_brain, max_revision_attempts=2).run(
                objective=TITLE.strip(),
                constraints=bundle_constraints,
                task_context=TASK.strip(),
                repository_context=(
                    audit_context.get("inventory", "")
                    + audit_context.get("file_context", "")
                    + audit_context.get("directory_context", "")
                )[:2000],
            )
        except Exception as exc:  # fail closed before repository mutation
            if _is_groq_rate_limit_error(exc):
                try:
                    deterministic_snapshot = build_read_only_audit_snapshot()
                except Exception as snapshot_error:
                    deterministic_snapshot = {
                        "status": "UNAVAILABLE",
                        "error": f"{type(snapshot_error).__name__}: {str(snapshot_error)[:500]}",
                    }
                message = _build_deterministic_rate_limit_report(
                    task_title=TITLE,
                    issue_number=ISSUE,
                    error=exc,
                    audit_context=audit_context,
                    snapshot=deterministic_snapshot,
                )
            else:
                message = (
                    "Barrot bundle authoring/review failed safely; repository repair was not started.\n\n"
                    f"Failure: {type(exc).__name__}: {str(exc)[:1200]}"
                )
            post_issue_comment(message)
            print(message)
            raise SystemExit(message) from exc

    lifecycle_path = lifecycle_store.save_plan(
        work_id, bundle_result, request_fingerprint=request_fingerprint
    )
    print(f"Bundle plan persisted: {lifecycle_path}")
    print(
        "Bundle gate:",
        bundle_result.status,
        "quality_score=",
        bundle_result.review.quality_score,
        "fingerprint=",
        bundle_result.review.fingerprint,
    )
    if bundle_result.status != "READY_FOR_EXECUTION_REVIEW":
        message = (
            "Barrot bundle failed its deterministic quality gate; repository repair was not started.\n\n"
            + json.dumps(bundle_result.to_dict(), indent=2)[:12000]
        )
        post_issue_comment(message)
        # Also log it: dispatch runs without an issue (ISSUE_NUMBER=0) post no comment,
        # and the findings would otherwise be lost.
        print(message)
        raise SystemExit(1)

    task_work_scope = request_fingerprint.split(":", 1)[-1][:16]
    controller = RepositoryRepairController(
        brain=brain,
        workspace=ROOT,
        workspace_verifier=verify_result,
        watchdog=build_repository_watchdog(),
    )
    queue = WorkQueueController(repair_controller=controller)
    def execute_bundle_task(task: dict[str, Any]) -> Any:
        task_title = f"{TITLE} — {task['title']}"
        task_body = "\n".join([
            f"Parent objective: {TITLE}",
            f"Original user request: {TASK}",
            f"Bundle task ID: {task['id']}",
            f"Task description: {task['description']}",
            "Target files: " + ", ".join(task.get("files", [])),
            "Acceptance criteria:\n- " + "\n- ".join(task.get("acceptance_criteria", [])),
            "Required tests:\n- " + "\n- ".join(task.get("tests", [])),
            "Rollback plan:\n- " + "\n- ".join(task.get("rollback_plan", [])),
            "Only perform this task after its declared dependencies are complete. Validate the result using the existing repair workflow.",
        ])
        task_context = build_audit_context(task_title, task_body)
        return queue.run(
            work_id=f"{work_id}:request:{task_work_scope}:task:{task['id']}",
            project_identity=build_project_identity(REPO),
            task_title=task_title,
            task_body=task_body,
            issue_number=ISSUE,
            repo=REPO,
            branch=BRANCH,
            audit_context=task_context,
        )

    def recover_completed_bundle_task(task: dict[str, Any]) -> dict[str, Any] | None:
        # Close the crash window where WorkQueueController persisted a successful
        # repair but the process died before bundle lifecycle evidence was appended.
        task_work_id = f"{work_id}:request:{task_work_scope}:task:{task['id']}"
        saved_work = queue.work_store.load(task_work_id)
        if not isinstance(saved_work, dict) or saved_work.get("status") != "complete":
            return None
        if saved_work.get("queue_advanced") is not True:
            return None
        cycle = saved_work.get("repair_cycle")
        if not isinstance(cycle, dict) or cycle.get("status") != "complete":
            return None
        commit = cycle.get("commit") or {}
        if not (
            cycle.get("local_validation_passed") is True
            and commit.get("remote_verified") is True
            and cycle.get("resolution_verified") is True
            and isinstance(commit.get("sha"), str)
            and commit.get("sha")
        ):
            return None
        return saved_work

    dispatch = dispatch_bundle_tasks(
        store=lifecycle_store,
        work_id=work_id,
        bundle=bundle_result.bundle,
        execute_task=execute_bundle_task,
        recover_task=recover_completed_bundle_task,
    )
    work = dispatch.get("last_result")
    task_ids = [
        task.get("id")
        for task in bundle_result.bundle.get("tasks", [])
        if isinstance(task, dict) and isinstance(task.get("id"), str)
    ]
    if (
        task_ids
        and dispatch.get("no_change_task_ids")
        and set(dispatch["no_change_task_ids"]) == set(task_ids)
    ):
        message = (
            "Barrot made no repository changes because deterministic validation confirmed "
            "that the requested issue does not reproduce. No repair is being reported as "
            "complete, and no pull request was created.\n\n"
            + json.dumps({
                "status": "NO_CHANGE_REQUIRED",
                "no_change_task_ids": dispatch["no_change_task_ids"],
            }, indent=2)
        )
        lifecycle_store.record_execution(work_id, {
            "status": "NO_CHANGE_REQUIRED",
            "bundle_complete": False,
            "no_change_task_ids": dispatch["no_change_task_ids"],
            "blocked_tasks": dispatch["blocked_tasks"],
            "pull_request_created": False,
        })
        post_issue_comment(message)
        print(message)
        return

    if work is None:
        message = (
            "Barrot bundle execution is blocked: no verified task result is available.\n\n"
            + json.dumps({
                "completed_task_ids": dispatch["completed_task_ids"],
                "blocked_tasks": dispatch["blocked_tasks"],
            }, indent=2)
        )
        lifecycle_store.record_execution(work_id, {
            "status": "BLOCKED",
            "bundle_complete": False,
            "completed_task_ids": dispatch["completed_task_ids"],
            "blocked_tasks": dispatch["blocked_tasks"],
        })
        post_issue_comment(message)
        raise SystemExit(1)

    work_data = _work_dict(work)
    cycle = work_data.get("repair_cycle") or {}
    cycle_data = cycle if isinstance(cycle, dict) else {}
    lifecycle_store.record_execution(work_id, {
        "status": "COMPLETE" if dispatch["complete"] else "BLOCKED",
        "bundle_complete": dispatch["complete"],
        "completed_task_ids": dispatch["completed_task_ids"],
        "executed_task_ids": dispatch["executed_task_ids"],
        "blocked_tasks": dispatch["blocked_tasks"],
        "cycle_id": cycle_data.get("cycle_id"),
        "queue_advanced": work_data.get("queue_advanced", False),
        "commit_sha": (cycle_data.get("commit") or {}).get("sha", ""),
        "local_validation_passed": cycle_data.get("local_validation_passed"),
        "remote_verified": (cycle_data.get("commit") or {}).get("remote_verified", False),
        "resolution_verified": cycle_data.get("resolution_verified", False),
        "failure": cycle_data.get("failure"),
    })

    rendered = json.dumps(work_data, indent=2)
    # last_result is the raw WorkItemEvidence; render the serialized form instead.
    dispatch_summary = {key: value for key, value in dispatch.items() if key != "last_result"}
    print(json.dumps({"bundle_dispatch": dispatch_summary, "last_work": work_data}, indent=2, default=str)[:55000])
    write_collaboration_record(work_data)

    if not dispatch["complete"]:
        post_issue_comment(
            "Barrot bundle execution is blocked; unfinished tasks were not reported complete.\n\n```json\n"
            + json.dumps({"completed_task_ids": dispatch["completed_task_ids"], "blocked_tasks": dispatch["blocked_tasks"]}, indent=2)[:50000]
            + "\n```"
        )
        raise SystemExit(1)

    if cycle.get("status") == "no_repair_required":
        if cycle.get("report_only"):
            return
        message = cycle.get("report") or "No deterministic repository repair was required."
        post_issue_comment(message)
        return

    if cycle.get("status") != "complete" or not work_data.get("queue_advanced", False):
        post_issue_comment(
            "Barrot repair failed safely.\n\n```json\n"
            + rendered[:55000]
            + "\n```"
        )
        raise SystemExit(1)

    create_pull_request(work)


if __name__ == "__main__":
    main()
