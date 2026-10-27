#!/usr/bin/env python3

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ARCH_CONTEXT = (
    ROOT
    / "scripts"
    / "barrot_architecture_context.py"
)

LEARNING = (
    ROOT
    / "ping-pongings"
    / "knowledge-base"
    / "barrot_code_evolution.jsonl"
)

MAX_ATTEMPTS = 3


def now():
    return datetime.now(
        timezone.utc
    ).isoformat()


def run(command):

    result = subprocess.run(
        command,
        cwd=ROOT,
        shell=True,
        text=True,
        capture_output=True,
    )

    return {
        "command": command,
        "returncode": result.returncode,
        "success": result.returncode == 0,
        "stdout": result.stdout[-20000:],
        "stderr": result.stderr[-20000:],
    }


def architecture_recall(goal):

    result = subprocess.run(
        [
            sys.executable,
            str(ARCH_CONTEXT),
            goal,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:

        return {
            "available": False,
            "error": result.stderr[-10000:],
        }

    try:

        context = json.loads(
            result.stdout
        )

    except Exception:

        return {
            "available": False,
            "error": result.stdout[-10000:],
        }

    context["available"] = True

    return context


def record(episode):

    LEARNING.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with LEARNING.open(
        "a",
        encoding="utf-8",
    ) as file:

        file.write(
            json.dumps(episode)
            + "\n"
        )


def discover_tests():

    tests_dir = ROOT / "tests"

    if not tests_dir.exists():

        return []

    return sorted(
        str(
            path.relative_to(ROOT)
        )
        for path in tests_dir.rglob(
            "test_*.py"
        )
        if path.is_file()
    )


def component_test_candidates(
    component_path,
    available_tests,
):

    name = Path(
        component_path
    ).stem.lower()

    candidates = []

    for test in available_tests:

        test_name = Path(
            test
        ).stem.lower()

        if name in test_name:

            candidates.append(
                test
            )

    return candidates


def test_commands(context):

    available_tests = discover_tests()

    paths = [
        component.get(
            "path",
            "",
        )
        for component in context.get(
            "components",
            [],
        )
    ]

    selected = []

    for path in paths:

        for candidate in (
            component_test_candidates(
                path,
                available_tests,
            )
        ):

            if candidate not in selected:

                selected.append(
                    candidate
                )

    if not selected:

        selected = available_tests

    if not selected:

        return [
            (
                "python3 -m pytest -q "
                "--no-cov"
            )
        ]

    return [
        (
            "python3 -m pytest -q "
            "--no-cov "
            f"{test}"
        )
        for test in selected
    ]


def classify_failure(result):

    text = (
        result["stdout"]
        + "\n"
        + result["stderr"]
    )

    if (
        "file or directory not found"
        in text
    ):

        return (
            "missing_test_target"
        )

    if (
        "Required test coverage"
        in text
    ):

        return (
            "coverage_gate"
        )

    if (
        "SyntaxError"
        in text
    ):

        return (
            "syntax_error"
        )

    if (
        "ImportError"
        in text
        or "ModuleNotFoundError"
        in text
    ):

        return (
            "dependency_or_import_error"
        )

    if (
        "failed"
        in text.lower()
    ):

        return (
            "test_failure"
        )

    return (
        "unknown_failure"
    )


def main():

    goal = " ".join(
        sys.argv[1:]
    ).strip()

    if not goal:

        print(
            "Usage: "
            "python3 "
            "scripts/barrot_code_evolution.py "
            '"goal"'
        )

        raise SystemExit(1)

    context = architecture_recall(
        goal
    )

    episode = {
        "timestamp": now(),
        "goal": goal,
        "architecture_context": context,
        "attempts": [],
    }

    print()
    print(
        "BARROT CODE EVOLUTION"
    )

    print(
        "GOAL:",
        goal,
    )

    if not context.get(
        "available"
    ):

        episode[
            "status"
        ] = (
            "architecture_recall_failed"
        )

        record(
            episode
        )

        print(
            "ARCHITECTURE RECALL FAILED"
        )

        print(
            context.get(
                "error",
                "",
            )
        )

        raise SystemExit(1)

    commands = test_commands(
        context
    )

    print()
    print(
        "SELECTED CHECKS:"
    )

    for command in commands:

        print(
            "-",
            command,
        )

    for attempt in range(
        1,
        MAX_ATTEMPTS + 1,
    ):

        print()
        print(
            f"ATTEMPT "
            f"{attempt}/"
            f"{MAX_ATTEMPTS}"
        )

        attempt_result = {
            "attempt": attempt,
            "timestamp": now(),
            "checks": [],
        }

        success = True

        for command in commands:

            result = run(
                command
            )

            result[
                "classification"
            ] = (
                "success"
                if result[
                    "success"
                ]
                else classify_failure(
                    result
                )
            )

            attempt_result[
                "checks"
            ].append(
                result
            )

            print()
            print(
                "COMMAND:",
                command,
            )

            print(
                "SUCCESS:",
                result[
                    "success"
                ],
            )

            print(
                "CLASSIFICATION:",
                result[
                    "classification"
                ],
            )

            if not result[
                "success"
            ]:

                success = False

                print()
                print(
                    result[
                        "stdout"
                    ][-4000:]
                )

                print(
                    result[
                        "stderr"
                    ][-4000:]
                )

        attempt_result[
            "success"
        ] = success

        episode[
            "attempts"
        ].append(
            attempt_result
        )

        record(
            {
                "type":
                    "coding_episode",
                "timestamp":
                    now(),
                "goal":
                    goal,
                "attempt":
                    attempt,
                "success":
                    success,
                "results": [
                    {
                        "command":
                            check[
                                "command"
                            ],
                        "classification":
                            check[
                                "classification"
                            ],
                        "success":
                            check[
                                "success"
                            ],
                    }
                    for check
                    in attempt_result[
                        "checks"
                    ]
                ],
            }
        )

        if success:

            episode[
                "status"
            ] = "validated"

            print()
            print(
                "VALIDATED"
            )

            break

        print()
        print(
            "FAILURE CLASSIFIED "
            "AND STORED"
        )

        time.sleep(
            min(
                attempt * 5,
                20,
            )
        )

    else:

        episode[
            "status"
        ] = (
            "needs_external_patch"
        )

    record(
        episode
    )

    print()
    print(
        "BARROT EVOLUTION "
        "CYCLE COMPLETE"
    )

    print(
        "STATUS:",
        episode.get(
            "status"
        ),
    )

    print(
        "LEARNING MEMORY:",
        LEARNING,
    )


if __name__ == "__main__":
    main()
