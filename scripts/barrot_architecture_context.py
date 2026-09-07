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


def words(text):
    return {
        word.lower()
        for word in text.replace("_", " ").replace("-", " ").split()
        if len(word) > 1
    }


def score(node, query_words):

    path_words = words(node["path"])

    symbol_words = set()

    for symbol in node.get("symbols", []):
        symbol_words |= words(symbol)

    dependency_words = set()

    for dependency in node.get(
        "dependencies",
        [],
    ):
        dependency_words |= words(dependency)

    return (
        len(query_words & path_words) * 20
        + len(query_words & symbol_words) * 30
        + len(query_words & dependency_words) * 10
    )


def recall(query, limit=25, depth=2):

    if not MEMORY.exists():
        return {
            "available": False,
            "reason": "connectome_memory_missing",
            "components": [],
        }

    data = json.loads(
        MEMORY.read_text(
            encoding="utf-8"
        )
    )

    query_words = words(query)

    nodes = {
        node["id"]: node
        for node in data["nodes"]
    }

    graph = defaultdict(set)

    for edge in data.get("edges", []):

        source = edge["source"]
        target = edge["target"]

        if source in nodes and target in nodes:
            graph[source].add(target)
            graph[target].add(source)

    ranked = []

    for node in nodes.values():

        node_score = score(
            node,
            query_words,
        )

        if node_score > 0:
            ranked.append(
                (
                    node_score,
                    node["id"],
                )
            )

    ranked.sort(
        reverse=True
    )

    queue = deque()
    discovered = {}

    for node_score, node_id in ranked[:10]:

        queue.append(
            (
                node_id,
                0,
                node_score,
            )
        )

    while queue:

        node_id, level, relevance = queue.popleft()

        if node_id in discovered:
            continue

        discovered[node_id] = relevance

        if level >= depth:
            continue

        for neighbor in graph.get(
            node_id,
            [],
        ):

            queue.append(
                (
                    neighbor,
                    level + 1,
                    max(
                        relevance // 2,
                        1,
                    ),
                )
            )

    results = []

    for node_id, relevance in discovered.items():

        node = nodes[node_id]

        results.append(
            {
                "path": node["path"],
                "type": node.get("type"),
                "symbols": node.get("symbols", [])[:20],
                "dependencies": node.get(
                    "dependencies",
                    [],
                )[:20],
                "relevance": relevance,
            }
        )

    results.sort(
        key=lambda item: item["relevance"],
        reverse=True,
    )

    return {
        "available": True,
        "query": query,
        "components": results[:limit],
        "memory_statistics": data.get(
            "statistics",
            {},
        ),
    }


def main():

    query = " ".join(
        sys.argv[1:]
    ).strip()

    if not query:
        print(
            json.dumps(
                {
                    "error": "query required"
                },
                indent=2,
            )
        )
        return

    print(
        json.dumps(
            recall(query),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
