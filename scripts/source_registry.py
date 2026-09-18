#!/usr/bin/env python3

from pathlib import Path
import argparse
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent

# Direct execution puts scripts/ ahead of the repository package namespace.
# Remove every scripts-path entry before importing barrot_agent so that
# scripts/barrot_agent.py cannot shadow the real barrot_agent package.
cleaned = []
for entry in sys.path:
    try:
        resolved = Path(entry or os.getcwd()).resolve()
    except Exception:
        cleaned.append(entry)
        continue

    if resolved == SCRIPTS:
        continue

    cleaned.append(entry)

sys.path[:] = [str(ROOT)] + [
    entry for entry in cleaned
    if entry != str(ROOT)
]

from barrot_agent.sources.source_registry import SourceRegistry


DEFAULT_REGISTRY = ROOT / ".barrot" / "source_registry" / "registry.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY),
    )
    parser.add_argument(
        "command",
        choices=["summary", "list", "gaps"],
    )
    args = parser.parse_args()

    registry = SourceRegistry(args.registry)

    if args.command == "summary":
        output = registry.summary()
    elif args.command == "gaps":
        output = registry.find_gaps()
    else:
        output = [
            record.to_dict()
            for record in registry.list_sources()
        ]

    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
