"""Find connections across sources and store them as a graph.

The graph is descriptive, not creative: nodes are stored memory records, edges
are shared rare content terms between records from *different* sources.  Any
"combined capability" text is emitted with ``status: hypothesis`` so it can
never be mistaken for an ingested fact.
"""

from __future__ import annotations

from collections import Counter

from ..gist_memory import content_terms
from .models import MemoryRecord, utc_now
from .storage import Store

MAX_NODES = 400
MAX_EDGES = 500
MAX_EDGES_PER_NODE = 5
MIN_SHARED_TERMS = 2
MAX_DF_RATIO = 0.4
MAX_SUGGESTIONS = 20


class CrossAnalyzer:
    """Build and persist the cross-source connection graph."""

    def __init__(
        self,
        store: Store,
        max_nodes: int = MAX_NODES,
        max_edges: int = MAX_EDGES,
        max_edges_per_node: int = MAX_EDGES_PER_NODE,
    ):
        self.store = store
        self.max_nodes = max_nodes
        self.max_edges = max_edges
        self.max_edges_per_node = max_edges_per_node

    def build(self, records: list[MemoryRecord] | None = None) -> dict:
        """Rebuild ``data/connections.json`` and return the graph."""
        items = list(records if records is not None else self.store.load_memory())
        items = items[-self.max_nodes :]
        terms = {record.id: set(content_terms(record.statement)) for record in items}
        counts: Counter[str] = Counter()
        for record_terms in terms.values():
            counts.update(record_terms)
        limit = max(2, int(len(items) * MAX_DF_RATIO)) if items else 1
        rare = {
            term for term, count in counts.items() if len(term) > 3 and count <= limit
        }

        nodes = [
            {
                "id": record.id,
                "label": record.statement[:120],
                "kind": record.kind,
                "capability": record.capability,
                "source_url": record.source_url,
                "retrieved_at": record.retrieved_at,
            }
            for record in items
        ]

        candidates: list[tuple[int, str, str, list[str]]] = []
        for left in range(len(items)):
            for right in range(left + 1, len(items)):
                first, second = items[left], items[right]
                if first.source_url == second.source_url:
                    continue
                shared = sorted((terms[first.id] & terms[second.id]) & rare)
                if len(shared) < MIN_SHARED_TERMS:
                    continue
                candidates.append((len(shared), first.id, second.id, shared))
        candidates.sort(key=lambda item: (-item[0], item[1], item[2]))

        edges: list[dict] = []
        degree: Counter[str] = Counter()
        for weight, first_id, second_id, shared in candidates:
            if len(edges) >= self.max_edges:
                break
            if (
                degree[first_id] >= self.max_edges_per_node
                or degree[second_id] >= self.max_edges_per_node
            ):
                continue
            by_id = {record.id: record for record in items}
            edges.append(
                {
                    "source": first_id,
                    "target": second_id,
                    "weight": weight,
                    "terms": shared[:6],
                    "cross_kind": by_id[first_id].kind != by_id[second_id].kind,
                }
            )
            degree[first_id] += 1
            degree[second_id] += 1

        graph = {
            "generated_at": utc_now(),
            "stats": {
                "nodes": len(nodes),
                "edges": len(edges),
                "sources": len({node["source_url"] for node in nodes}),
                "kinds": len({node["kind"] for node in nodes}),
            },
            "nodes": nodes,
            "edges": edges,
            "suggestions": self._suggestions(edges, nodes),
        }
        self.store.save_connections(graph)
        return graph

    def _suggestions(self, edges: list[dict], nodes: list[dict]) -> list[dict]:
        """Label cross-paradigm edges as hypotheses, never as facts."""
        by_id = {node["id"]: node for node in nodes}
        out: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for edge in edges:
            if not edge["cross_kind"]:
                continue
            first, second = by_id[edge["source"]], by_id[edge["target"]]
            key = tuple(sorted((first["kind"], second["kind"])))
            if key in seen or not edge["terms"]:
                continue
            seen.add(key)
            out.append(
                {
                    "status": "hypothesis",
                    "term": edge["terms"][0],
                    "kinds": [first["kind"], second["kind"]],
                    "records": [first["id"], second["id"]],
                    "hypothesis": (
                        f"'{edge['terms'][0]}' appears in both a {first['kind']} record and a "
                        f"{second['kind']} record; candidate combined capability."
                    ),
                }
            )
            if len(out) >= MAX_SUGGESTIONS:
                break
        return out
