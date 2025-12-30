# barrot/core/cognition_lattice.py
from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class Node:
    id: str
    kind: str     # "concept", "theorem", "lemma", "proof_fragment", "obstruction", etc.
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Edge:
    source: str
    target: str
    relation: str  # "implies", "uses", "contradicts", "equivalent_to", etc.
    weight: float = 1.0

@dataclass
class CognitionLattice:
    nodes: Dict[str, Node] = field(default_factory=dict)
    edges: List[Edge] = field(default_factory=list)

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge) -> None:
        self.edges.append(edge)

    def neighbors(self, node_id: str) -> List[Node]:
        return [self.nodes[e.target] for e in self.edges if e.source == node_id]

    def find_by_kind(self, kind: str) -> List[Node]:
        return [n for n in self.nodes.values() if n.kind == kind]
