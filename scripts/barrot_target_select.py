#!/usr/bin/env python3

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REGISTRY = (
    ROOT
    / ".barrot"
    / "target_registry.json"
)


def load_registry():

    return json.loads(
        REGISTRY.read_text(
            encoding="utf-8"
        )
    )


def score_target(
    goal,
    target,
):

    goal_words = set(
        goal.lower().split()
    )

    searchable = " ".join(
        [
            target.get(
                "id",
                ""
            ),
            target.get(
                "path",
                ""
            ),
            " ".join(
                target.get(
                    "tags",
                    [],
                )
            ),
        ]
    ).lower()

    score = 0

    for word in goal_words:

        if word in searchable:

            score += 1

    return score


def select_target(goal):

    registry = load_registry()

    candidates = []

    for target in registry.get(
        "targets",
        [],
    ):

        if not target.get(
            "enabled",
            False,
        ):

            continue

        if target.get(
            "mode"
        ) != "controlled":

            continue

        score = score_target(
            goal,
            target,
        )

        candidates.append(
            (
                score,
                target,
            )
        )

    if not candidates:

        return None

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    best_score, best = (
        candidates[0]
    )

    if best_score <= 0:

        return None

    return best


def main():

    goal = " ".join(
        sys.argv[1:]
    ).strip()

    if not goal:

        raise SystemExit(
            "usage: "
            "barrot_target_select.py "
            '"goal"'
        )

    selected = select_target(
        goal
    )

    if selected is None:

        print(
            json.dumps(
                {
                    "selected": False
                }
            )
        )

        raise SystemExit(1)

    print(
        json.dumps(
            {
                "selected": True,
                "id": selected.get(
                    "id"
                ),
                "path": selected.get(
                    "path"
                ),
                "tests": selected.get(
                    "tests",
                    [],
                ),
                "tags": selected.get(
                    "tags",
                    [],
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
