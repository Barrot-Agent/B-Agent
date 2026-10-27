#!/usr/bin/env python3

import json
import sys
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MEMORY = (
    ROOT
    / "ping-pongings"
    / "knowledge-base"
    / "barrot_connectome_memory.json"
)


def score_node(node, query_words):

    score = 0

    path = node["path"].lower()
    symbols = " ".join(node.get("symbols", [])).lower()
    dependencies = " ".join(node.get("dependencies", [])).lower()

    for word in query_words:

        if word in path:
            score += 20

        if word in symbols:
            score += 30

        if word in dependencies:
            score += 10

    return score


def main():

    query = " ".join(sys.argv[1:]).strip()

    if not query:
        print("Usage:")
        print(
            "python3 scripts/barrot_memory_recall.py <goal>"
        )
        return

    if not MEMORY.exists():

        print("Connectome memory missing.")
        print(
            "Run: python3 scripts/barrot_connectome_memory.py"
        )
        return

    data = json.loads(
        MEMORY.read_text(encoding="utf-8")
    )

    query_words = [
        word.lower()
        for word in query.split()
        if len(word.strip()) > 1
    ]

    nodes = {
        node["id"]: node
        for node in data["nodes"]
    }

    graph = defaultdict(set)

    for edge in data["edges"]:

        source = edge["source"]
        target = edge["target"]

        if source in nodes and target in nodes:

            graph[source].add(target)
            graph[target].add(source)

    ranked = []

    for node in data["nodes"]:

        score = score_node(
            node,
            query_words,
        )

        if score > 0:

            ranked.append(
                (
                    score,
                    node["id"],
                )
            )

    ranked.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    seeds = [
        node_id
        for _, node_id in ranked[:10]
    ]

    discovered = {}
    queue = deque()

    for node_id in seeds:

        queue.append(
            (
                node_id,
                0,
                100,
            )
        )

    while queue:

        node_id, depth, relevance = queue.popleft()

        previous = discovered.get(node_id)

        if previous is not None and previous >= relevance:
            continue

        discovered[node_id] = relevance

        if depth >= 2:
            continue

        for neighbor in graph.get(
            node_id,
            [],
        ):

            queue.append(
                (
                    neighbor,
                    depth + 1,
                    relevance // 2,
                )
            )

    results = []

    for node_id, relevance in discovered.items():

        node = nodes[node_id]

        results.append(
            (
                relevance,
                node,
            )
        )

    results.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    print()
    print("BARROT CONNECTOME RECALL")
    print("GOAL:", query)
    print()
    print(
        "DIRECT MATCHES:",
        len(ranked),
    )
    print(
        "CONNECTED COMPONENTS:",
        len(results),
    )
    print()

    for relevance, node in results[:40]:

        print(
            f"[{relevance}] {node['path']}"
        )

        if node.get("symbols"):

            print(
                "  symbols:",
                ", ".join(
                    node["symbols"][:12]
                ),
            )

        if node.get("dependencies"):

            print(
                "  dependencies:",
                ", ".join(
                    node["dependencies"][:12]
                ),
            )

        print()


if __name__ == "__main__":
    main()
