#!/usr/bin/env python3

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REGISTRY = (
    ROOT
    / ".barrot"
    / "target_registry.json"
)


DEFAULT_REGISTRY = {
    "version": 1,
    "targets": [
        {
            "id": "autonomous_math",
            "path": (
                ".barrot/"
                "autonomous_tasks/"
                "math_task.py"
            ),
            "tests": [
                (
                    ".barrot/"
                    "autonomous_tasks/"
                    "test_math_task.py"
                )
            ],
            "mode": "controlled",
            "rollback": True,
            "enabled": True,
        }
    ],
}


def load_registry():

    if not REGISTRY.exists():

        REGISTRY.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        REGISTRY.write_text(
            json.dumps(
                DEFAULT_REGISTRY,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    return json.loads(
        REGISTRY.read_text(
            encoding="utf-8"
        )
    )


def main():

    registry = load_registry()

    print()
    print(
        "BARROT TARGET REGISTRY"
    )

    print()

    for target in registry.get(
        "targets",
        [],
    ):

        print(
            "ID:",
            target.get(
                "id"
            ),
        )

        print(
            "PATH:",
            target.get(
                "path"
            ),
        )

        print(
            "TESTS:",
            ", ".join(
                target.get(
                    "tests",
                    [],
                )
            ),
        )

        print(
            "ROLLBACK:",
            target.get(
                "rollback"
            ),
        )

        print(
            "ENABLED:",
            target.get(
                "enabled"
            ),
        )

        print()


if __name__ == "__main__":
    main()
