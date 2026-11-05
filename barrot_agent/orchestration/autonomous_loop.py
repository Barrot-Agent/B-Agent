"""Autonomous execution loop for Barrot.

Model-proposed commands are passed through BarrotExecutor's argv allowlist.
They are never interpreted by a shell.
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass
from pathlib import Path

from .autonomous_state import AutonomousTaskStore
from .executor import BarrotExecutor
from .verifier import BarrotVerifier


@dataclass
class AutonomousResult:
    success: bool
    attempts: int
    history: list[dict]
    task_id: str = ""
    status: str = "paused"
    checkpoint_path: str = ""


class BarrotAutonomousLoop:

    def __init__(
        self,
        brain,
        workspace: str = ".",
        max_attempts: int = 5,
    ):
        if isinstance(max_attempts, bool) or not isinstance(max_attempts, int) or max_attempts < 1:
            raise ValueError("max_attempts must be a positive integer")
        self.brain = brain
        self.workspace = Path(workspace).resolve()
        self.executor = BarrotExecutor(self.workspace)
        self.verifier = BarrotVerifier(self.executor)
        self.store = AutonomousTaskStore(self.workspace)
        self.max_attempts = max_attempts

    def _extract_json(self, text: str) -> dict:
        """Extract the first JSON object from a model response."""
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in Barrot response")
        return json.loads(match.group(0))

    @staticmethod
    def _redact(text: str) -> str:
        """Remove common credential formats before checkpointing model/tool output."""
        text = re.sub(r"(?i)\b(api[_-]?key|token|secret|password)\b(\s*[:=]\s*)[^\s,;]+", r"\1\2[REDACTED]", text)
        text = re.sub(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]+=*", "Bearer [REDACTED]", text)
        text = re.sub(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b", "[REDACTED_GITHUB_TOKEN]", text)
        text = re.sub(r"\bsk-[A-Za-z0-9_-]{20,}\b", "[REDACTED_API_KEY]", text)
        return text

    @classmethod
    def _redact_value(cls, value):
        """Recursively sanitize text before persisting a checkpoint."""
        if isinstance(value, str):
            return cls._redact(value)
        if isinstance(value, dict):
            return {str(key): cls._redact_value(item) for key, item in value.items()}
        if isinstance(value, list):
            return [cls._redact_value(item) for item in value]
        if isinstance(value, tuple):
            return [cls._redact_value(item) for item in value]
        return value

    def run(self, goal: str, *, task_id: str | None = None) -> AutonomousResult:
        """Run or resume a durable task; pass the returned task_id to continue later."""
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("goal must be a non-empty string")
        task_id = task_id or uuid.uuid4().hex
        goal_hash = hashlib.sha256(goal.encode("utf-8")).hexdigest()
        state = self.store.load(task_id)
        if state is None:
            state = {
                "task_id": task_id,
                "goal_sha256": goal_hash,
                "status": "queued",
                "attempts_completed": 0,
                "history": [],
            }
        elif state.get("goal_sha256") != goal_hash:
            raise ValueError("task_id is already bound to a different goal")
        history = state["history"]
        checkpoint = self.store.path_for(task_id)
        if state.get("status") == "complete":
            return AutonomousResult(True, len(history), history, task_id, "complete", str(checkpoint))

        start = int(state.get("attempts_completed", len(history))) + 1
        stop = start + self.max_attempts
        for attempt in range(start, stop):
            state["status"] = "running"
            state["attempts_completed"] = attempt
            task = f"""
You are Barrot, operating a real Python repository in a controlled workspace.

GOAL:
{goal}

ATTEMPT:
{attempt}

RECENT CHECKPOINT HISTORY:
{json.dumps(history[-3:], ensure_ascii=False)}

Return ONLY valid JSON using this exact schema:

{{
  "analysis": "brief diagnosis",
  "commands": [
    "find . -maxdepth 2 -type f -not -path ./.git/*",
    "python -m compileall -q barrot_agent scripts"
  ]
}}

CRITICAL EXECUTION RULES:
- Every command is parsed into argv and executed with shell=False.
- There is no shell, pipeline, redirection, command substitution, or command chaining.
- Use one command per string. Never include shell operators such as semicolon, &&, ||, pipe, >, <, backticks, or command substitution.
- Never invoke sh, bash, powershell, cmd, curl, wget, pip, npm, or arbitrary executables.
- Python is limited to python -m pytest with explicit test paths and python -m compileall -q barrot_agent scripts.
- pytest is limited to explicit in-workspace test paths and bounded read-only test options.
- Git is limited to git status --short and git diff --no-ext-diff, optionally with --stat.
- Read-only inspection commands may include pwd, ls, bounded find, grep -rIn --exclude-dir=.git -- PATTERN PATH, cat, and numeric-range sed.
- File paths must remain inside the configured workspace.
- Do not modify files unless the goal explicitly requires modification.
- Do not expose or modify secrets.
- Do not restore Orbit or removed integrations.
- Keep actions minimal and prefer inspection before modification.
- If a command is rejected, inspect the error and choose an allowed command; do not attempt a shell workaround.
"""
            plan_text = self._redact(str(self.brain.think(task)))
            record = {"attempt": attempt, "plan": plan_text, "execution": [], "verification": []}
            history.append(record)
            self.store.save(task_id, state)
            try:
                plan = self._extract_json(plan_text)
            except Exception as exc:
                record["planning_error"] = self._redact(str(exc))
                self.store.save(task_id, state)
                continue
            commands = plan.get("commands", [])
            if not isinstance(commands, list):
                record["planning_error"] = "commands field is not a list"
                self.store.save(task_id, state)
                continue
            for command in commands:
                if not isinstance(command, str):
                    record["execution"].append({"success": False, "error": "Command was not a string"})
                else:
                    try:
                        result = self.executor.run(command)
                        record["execution"].append({
                            "command": command,
                            "success": result.success,
                            "stdout": self._redact(result.stdout),
                            "stderr": self._redact(result.stderr),
                            "returncode": result.returncode,
                        })
                    except Exception as exc:
                        record["execution"].append({
                            "command": command, "success": False,
                            "error": self._redact(str(exc)),
                        })
                self.store.save(task_id, state)
            verification = self.verifier.verify_python()
            record["verification"] = self._redact_value(verification.checks)
            commands_ok = len(record["execution"]) > 0 and all(
                item.get("success", False) for item in record["execution"]
            )
            if commands_ok and verification.success:
                state["status"] = "complete"
                self.store.save(task_id, state)
                return AutonomousResult(True, len(history), history, task_id, "complete", str(checkpoint))
            self.store.save(task_id, state)
        state["status"] = "paused"
        self.store.save(task_id, state)
        return AutonomousResult(False, len(history), history, task_id, "paused", str(checkpoint))
