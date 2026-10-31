from __future__ import annotations

import json
import subprocess
import time

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RepairResult:
    success: bool
    attempts: int
    checks: list[dict[str, Any]] = field(default_factory=list)
    message: str = ""


def run_command(command, cwd):
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=120,
        )

        return {
            "command": " ".join(command),
            "classification": (
                "PASS"
                if result.returncode == 0
                else "FAIL"
            ),
            "success": result.returncode == 0,
            "stdout": result.stdout[-4000:],
            "stderr": result.stderr[-4000:],
        }

    except Exception as exc:
        return {
            "command": " ".join(command),
            "classification": "ERROR",
            "success": False,
            "stdout": "",
            "stderr": str(exc),
        }


def repository_checks(workspace):
    workspace = Path(workspace)

    checks = []

    python_files = [
        str(path)
        for path in workspace.rglob("*.py")
        if ".git" not in path.parts
        and ".venv" not in path.parts
        and "venv" not in path.parts
        and "__pycache__" not in path.parts
        and ".barrot-backup" not in path.parts
    ]

    if python_files:
        checks.append(
            run_command(
                [
                    "python",
                    "-m",
                    "py_compile",
                    *python_files[:150],
                ],
                workspace,
            )
        )

    return checks


def build_repair_report(checks):
    return "\n\n".join(
        "\n".join(
            [
                f"COMMAND: {check['command']}",
                f"STATUS: {check['classification']}",
                "STDOUT:",
                check.get("stdout", ""),
                "STDERR:",
                check.get("stderr", ""),
            ]
        )
        for check in checks
    )


def call_llm_with_retry(
    llm,
    messages,
    max_retries=6,
):
    delay = 5

    for retry in range(max_retries):
        try:
            return llm.chat(messages)

        except Exception as exc:
            error = str(exc)

            rate_limited = (
                "429" in error
                or "Too Many Requests" in error
                or "rate limit" in error.lower()
            )

            if not rate_limited:
                raise

            if retry >= max_retries - 1:
                raise

            print(
                f"Groq rate limit reached. "
                f"Waiting {delay} seconds "
                f"before retry {retry + 1}/{max_retries}..."
            )

            time.sleep(delay)

            delay = min(
                delay * 2,
                120,
            )

    raise RuntimeError(
        "LLM retry limit reached."
    )


def run_repository_repair_loop(
    workspace=None,
    llm=None,
    max_attempts=3,
    **kwargs,
):
    if workspace is None:
        workspace = kwargs.get(
            "repo",
            ".",
        )

    workspace = Path(workspace).resolve()

    history = []

    for attempt in range(
        1,
        max_attempts + 1,
    ):
        print(
            f"Running repository validation "
            f"attempt {attempt}/{max_attempts}..."
        )

        checks = repository_checks(
            workspace,
        )

        history.extend(checks)

        failures = [
            check
            for check in checks
            if not check["success"]
        ]

        if not failures:
            return RepairResult(
                success=True,
                attempts=attempt,
                checks=history,
                message=(
                    "Repository validation passed."
                ),
            )

        if llm is None:
            return RepairResult(
                success=False,
                attempts=attempt,
                checks=history,
                message=(
                    "Validation failed and no LLM "
                    "repair backend was supplied."
                ),
            )

        report = build_repair_report(
            failures,
        )

        prompt = f"""
Repair the smallest possible cause of
these repository validation failures.

FAILURES:

{report[:10000]}

Return ONLY valid JSON:

{{
  "diagnosis": "short explanation",
  "changes": [
    {{
      "path": "relative/path",
      "old": "exact existing text",
      "new": "replacement text"
    }}
  ]
}}

Rules:
- Minimal changes only.
- Do not modify unrelated files.
- Do not delete functionality.
- The old text must match exactly.
"""

        try:
            answer = call_llm_with_retry(
                llm,
                [
                    {
                        "role": "system",
                        "content": (
                            "You are a precise "
                            "repository repair engine. "
                            "Return JSON only."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )

        except Exception as exc:
            return RepairResult(
                success=False,
                attempts=attempt,
                checks=history,
                message=(
                    "LLM request failed after "
                    f"rate-limit retries: {exc}"
                ),
            )

        try:
            plan = json.loads(answer)

        except Exception as exc:
            return RepairResult(
                success=False,
                attempts=attempt,
                checks=history,
                message=(
                    "Repair model returned "
                    f"invalid JSON: {exc}"
                ),
            )

        changes = plan.get(
            "changes",
            [],
        )

        if not changes:
            return RepairResult(
                success=False,
                attempts=attempt,
                checks=history,
                message=(
                    "No repair changes were "
                    "generated: "
                    + str(
                        plan.get(
                            "diagnosis",
                            "",
                        )
                    )
                ),
            )

        applied = 0

        for change in changes:
            relative_path = change.get(
                "path",
                "",
            )

            if not relative_path:
                continue

            target = (
                workspace
                / relative_path
            ).resolve()

            if (
                target != workspace
                and workspace not in target.parents
            ):
                return RepairResult(
                    success=False,
                    attempts=attempt,
                    checks=history,
                    message=(
                        "Unsafe repair path rejected: "
                        f"{relative_path}"
                    ),
                )

            if not target.exists():
                continue

            old = change.get(
                "old",
                "",
            )

            new = change.get(
                "new",
                "",
            )

            text = target.read_text(
                encoding="utf-8",
            )

            if old not in text:
                continue

            target.write_text(
                text.replace(
                    old,
                    new,
                    1,
                ),
                encoding="utf-8",
            )

            applied += 1

        if applied == 0:
            return RepairResult(
                success=False,
                attempts=attempt,
                checks=history,
                message=(
                    "Repair plan produced no "
                    "applicable changes."
                ),
            )

        print(
            f"Applied {applied} repair "
            f"change(s). Re-validating..."
        )

    return RepairResult(
        success=False,
        attempts=max_attempts,
        checks=history,
        message=(
            "Maximum repair attempts reached."
        ),
    )
