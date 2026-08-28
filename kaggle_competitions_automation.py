#!/usr/bin/env python3
"""Kaggle competition automation: list active competitions and log their status."""

import json
import os
import sys

MAX_COMPETITIONS = int(os.environ.get("KAGGLE_MAX_COMPETITIONS", "5"))

try:
    import kaggle  # noqa: F401 — validates credentials on import
    from kaggle.api.kaggle_api_extended import KaggleApiExtended
except ImportError as exc:
    print(f"kaggle package not installed: {exc}")
    sys.exit(1)


def main() -> None:
    username = os.environ.get("KAGGLE_USERNAME", "")
    key = os.environ.get("KAGGLE_KEY", "")
    if not username or not key:
        print("KAGGLE_USERNAME and KAGGLE_KEY must be set")
        sys.exit(1)

    api = KaggleApiExtended()
    api.authenticate()

    competitions = api.competitions_list(page=1)[:MAX_COMPETITIONS]
    if not competitions:
        print("No active competitions found.")
        return

    results = []
    for comp in competitions:
        results.append(
            {
                "ref": comp.ref,
                "title": comp.title,
                "deadline": str(comp.deadline),
                "category": comp.category,
                "reward": comp.reward,
            }
        )
        print(f"  {comp.ref}: {comp.title} (deadline: {comp.deadline})")

    out = json.dumps(results, indent=2)
    print(out)
    print(f"Listed {len(results)} competitions.")


if __name__ == "__main__":
    main()
