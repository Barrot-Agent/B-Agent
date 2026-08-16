"""
Knowledge Graph Builder – Background Task
==========================================
Builds a structured knowledge graph for the 8 capability gaps defined in
:mod:`barrot_agent.mcp_targets` while other work (MCP discovery, sandbox
evaluation, etc.) proceeds in parallel.

Architecture
------------
* **KnowledgeNode** – represents a concept, tool category, MCP server, or
  capability gap.
* **KnowledgeEdge** – a directed, labelled relationship between two nodes.
* **CapabilityGapGraph** – the sub-graph rooted at one capability gap.
* **KnowledgeGraphBuilder** – orchestrates the build across all 8 gaps,
  detects shared concepts, writes the result to disk, and can run in a
  daemon thread via :func:`run_background`.

Usage
-----
>>> from barrot_agent.knowledge_graph_builder import run_background
>>> thread = run_background()        # returns immediately
>>> # … do other work …
>>> thread.join()                    # optional – wait for completion

The output is written to ``capability_gap_knowledge_graph.json`` in the
repository root by default.
"""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from barrot_agent.mcp_targets import (
    CAPABILITY_TARGETS,
    SUPPORTED_MCP_SERVERS,
    CapabilityTarget,
    MCPServerSpec,
)

logger = logging.getLogger(__name__)

# Only the first 8 capability targets are in scope for this builder.
_GAP_LIMIT = 8

# ---------------------------------------------------------------------------
# Graph primitives
# ---------------------------------------------------------------------------


@dataclass
class KnowledgeNode:
    """A single vertex in the capability-gap knowledge graph."""

    node_id: str
    node_type: str  # "capability_gap" | "tool_category" | "mcp_server" | "concept"
    label: str
    description: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class KnowledgeEdge:
    """A directed, labelled edge between two :class:`KnowledgeNode` objects."""

    source_id: str
    target_id: str
    relation: str  # e.g. "requires", "covered_by", "shares_concept_with", "depends_on"
    weight: float = 1.0


@dataclass
class CapabilityGapGraph:
    """Sub-graph for one capability gap."""

    gap_id: str
    gap_name: str
    nodes: List[KnowledgeNode] = field(default_factory=list)
    edges: List[KnowledgeEdge] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


class KnowledgeGraphBuilder:
    """
    Incrementally builds a knowledge graph for the 8 capability gaps.

    Parameters
    ----------
    output_path:
        Where to write the serialised graph.  Defaults to
        ``capability_gap_knowledge_graph.json`` in the repo root.
    gap_limit:
        How many capability targets to process (default 8).
    """

    def __init__(
        self,
        output_path: Optional[Path] = None,
        gap_limit: int = _GAP_LIMIT,
    ) -> None:
        self._output_path = output_path or (
            Path(__file__).resolve().parents[1] / "capability_gap_knowledge_graph.json"
        )
        self._gap_limit = gap_limit
        self._gaps: List[CapabilityGapGraph] = []
        self._global_nodes: Dict[str, KnowledgeNode] = {}
        self._cross_edges: List[KnowledgeEdge] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(self) -> Dict:
        """
        Run the full build pipeline and return the serialisable graph dict.

        Steps:
        1. For each of the 8 capability targets, create a root node.
        2. Expand each gap with tool-category nodes and MCP-server nodes.
        3. Detect shared concepts across gaps and add cross-gap edges.
        4. Persist to ``output_path``.
        """
        targets = CAPABILITY_TARGETS[: self._gap_limit]
        logger.info(
            "KnowledgeGraphBuilder: building graph for %d capability gaps", len(targets)
        )

        for target in targets:
            gap_graph = self._build_gap_graph(target)
            self._gaps.append(gap_graph)
            logger.debug("Built sub-graph for %s (%s)", target.id, target.name)

        self._add_cross_gap_edges()
        graph = self._serialise()
        self._write(graph)
        logger.info(
            "KnowledgeGraphBuilder: graph written to %s", self._output_path
        )
        return graph

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_gap_graph(self, target: CapabilityTarget) -> CapabilityGapGraph:
        """Construct the sub-graph for a single capability gap."""
        gap_graph = CapabilityGapGraph(gap_id=target.id, gap_name=target.name)

        # Root node – the capability gap itself
        root = KnowledgeNode(
            node_id=target.id,
            node_type="capability_gap",
            label=target.name,
            description=target.description,
            metadata={"priority": target.priority, "min_maturity": target.min_maturity},
        )
        gap_graph.nodes.append(root)
        self._global_nodes[root.node_id] = root

        # Tool-category nodes
        for category in target.required_tool_categories:
            cat_id = f"cat:{category}"
            cat_node = self._global_nodes.get(cat_id) or KnowledgeNode(
                node_id=cat_id,
                node_type="tool_category",
                label=category.replace("_", " ").title(),
                description=f"Tooling category: {category}",
            )
            self._global_nodes[cat_id] = cat_node
            gap_graph.nodes.append(cat_node)
            gap_graph.edges.append(
                KnowledgeEdge(
                    source_id=target.id,
                    target_id=cat_id,
                    relation="requires",
                )
            )

            # MCP-server nodes that cover this category
            covering_servers = _servers_for_category(category)
            for srv in covering_servers:
                srv_id = f"srv:{srv.server_id}"
                srv_node = self._global_nodes.get(srv_id) or KnowledgeNode(
                    node_id=srv_id,
                    node_type="mcp_server",
                    label=srv.name,
                    description=srv.description,
                    metadata={
                        "license": srv.license,
                        "requires_auth": str(srv.requires_auth),
                        "homepage": srv.homepage,
                    },
                )
                self._global_nodes[srv_id] = srv_node
                gap_graph.nodes.append(srv_node)
                gap_graph.edges.append(
                    KnowledgeEdge(
                        source_id=cat_id,
                        target_id=srv_id,
                        relation="covered_by",
                    )
                )

        return gap_graph

    def _add_cross_gap_edges(self) -> None:
        """
        Detect tool categories shared by more than one gap and connect the
        corresponding root nodes with ``shares_concept_with`` edges.
        """
        # Map each tool-category to the gap IDs that require it
        category_to_gaps: Dict[str, List[str]] = {}
        for gap_graph in self._gaps:
            for edge in gap_graph.edges:
                if edge.target_id.startswith("cat:") and edge.relation == "requires":
                    category_to_gaps.setdefault(edge.target_id, []).append(
                        gap_graph.gap_id
                    )

        for cat_id, gap_ids in category_to_gaps.items():
            if len(gap_ids) < 2:
                continue
            # Connect every pair that shares this category
            for i in range(len(gap_ids)):
                for j in range(i + 1, len(gap_ids)):
                    self._cross_edges.append(
                        KnowledgeEdge(
                            source_id=gap_ids[i],
                            target_id=gap_ids[j],
                            relation="shares_concept_with",
                            weight=0.5,
                        )
                    )
                    logger.debug(
                        "Cross-gap edge: %s ↔ %s via %s",
                        gap_ids[i],
                        gap_ids[j],
                        cat_id,
                    )

    def _serialise(self) -> Dict:
        """Produce the final serialisable representation."""
        return {
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "gap_limit": self._gap_limit,
            "gaps": [
                {
                    "gap_id": g.gap_id,
                    "gap_name": g.gap_name,
                    "nodes": [asdict(n) for n in g.nodes],
                    "edges": [asdict(e) for e in g.edges],
                }
                for g in self._gaps
            ],
            "cross_gap_edges": [asdict(e) for e in self._cross_edges],
            "all_nodes": {nid: asdict(n) for nid, n in self._global_nodes.items()},
        }

    def _write(self, graph: Dict) -> None:
        """Write the graph to ``output_path``."""
        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._output_path, "w", encoding="utf-8") as fh:
            json.dump(graph, fh, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _servers_for_category(category: str) -> List[MCPServerSpec]:
    """Return the supported MCP servers whose tool_categories include *category*."""
    return [
        srv for srv in SUPPORTED_MCP_SERVERS if category in srv.tool_categories
    ]


# ---------------------------------------------------------------------------
# Background-thread entry point
# ---------------------------------------------------------------------------


def run_background(
    output_path: Optional[Path] = None,
    gap_limit: int = _GAP_LIMIT,
) -> threading.Thread:
    """
    Start the knowledge-graph build in a daemon thread and return immediately.

    This lets Barrot begin building the knowledge graph while the MCP
    discovery, scoring, sandbox, and approval pipelines run concurrently.

    Parameters
    ----------
    output_path:
        Override the output file location.
    gap_limit:
        Number of capability gaps to process (default 8).

    Returns
    -------
    threading.Thread
        The running daemon thread.  Call ``.join()`` if you need to wait for
        the build to complete.

    Example
    -------
    >>> thread = run_background()
    >>> run_other_pipeline()        # runs while graph is being built
    >>> thread.join()               # wait if needed
    """
    builder = KnowledgeGraphBuilder(output_path=output_path, gap_limit=gap_limit)

    thread = threading.Thread(
        target=_build_with_logging,
        args=(builder,),
        name="knowledge-graph-builder",
        daemon=True,
    )
    thread.start()
    logger.info(
        "Knowledge graph builder started in background thread (gap_limit=%d)",
        gap_limit,
    )
    return thread


def _build_with_logging(builder: KnowledgeGraphBuilder) -> None:
    """Wrapper so exceptions in the daemon thread are surfaced via logging."""
    try:
        graph = builder.build()
        n_gaps = len(graph.get("gaps", []))
        n_nodes = len(graph.get("all_nodes", {}))
        n_cross = len(graph.get("cross_gap_edges", []))
        logger.info(
            "Knowledge graph complete: %d gaps, %d nodes, %d cross-gap edges",
            n_gaps,
            n_nodes,
            n_cross,
        )
    except Exception:  # noqa: BLE001
        logger.exception("Knowledge graph builder encountered an error")
