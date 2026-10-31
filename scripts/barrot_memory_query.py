#!/usr/bin/env python3

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MEMORY = (
    ROOT
    / "ping-pongings"
    / "knowledge-base"
    / "barrot_connectome_memory.json"
)


def score_node(node, query):

    query = query.lower()

    score = 0

    path = node["path"].lower()

    if query in path:
        score += 100

    for word in query.split():

        if word in path:
            score += 20

        for symbol in node.get(
            "symbols",
            [],
        ):

            if word in symbol.lower():
                score += 30

        for dependency in node.get(
            "dependencies",
            [],
        ):

            if word in dependency.lower():
                score += 10

    return score


def main():

    query = " ".join(
        sys.argv[1:]
    ).strip()

    if not query:
        print(
            "Usage: python3 scripts/barrot_memory_query.py <query>"
        )
        return

    if not MEMORY.exists():

        print(
            "Connectome memory missing. Run:"
        )

        print(
            "python3 scripts/barrot_connectome_memory.py"
        )

        return

    data = json.loads(
        MEMORY.read_text()
    )

    ranked = []

    for node in data["nodes"]:

        score = score_node(
            node,
            query,
        )

        if score > 0:

            ranked.append(
                (
                    score,
                    node,
                )
            )

    ranked.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    print()
    print("BARROT MEMORY QUERY")
    print("QUERY:", query)
    print()

    for score, node in ranked[:25]:

        print(
            f"[{score}] {node['path']}"
        )

        if node.get("symbols"):

            print(
                "  symbols:",
                ", ".join(
                    node["symbols"][:15]
                ),
            )

        if node.get("dependencies"):

            print(
                "  dependencies:",
                ", ".join(
                    node["dependencies"][:15]
                ),
            )

        print()


if __name__ == "__main__":
    main()
