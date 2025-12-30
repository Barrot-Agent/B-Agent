# barrot/tools/graph_store.py
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field

@dataclass
class GraphNode:
    id: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GraphEdge:
    source: str
    target: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)

class GraphStore:
    """Store and query graph structures for knowledge representation"""
    
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        # Index for efficient neighbor lookup
        self._outgoing: Dict[str, List[GraphEdge]] = {}
        self._incoming: Dict[str, List[GraphEdge]] = {}
    
    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph"""
        self.nodes[node.id] = node
        if node.id not in self._outgoing:
            self._outgoing[node.id] = []
        if node.id not in self._incoming:
            self._incoming[node.id] = []
    
    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the graph"""
        self.edges.append(edge)
        self._outgoing.setdefault(edge.source, []).append(edge)
        self._incoming.setdefault(edge.target, []).append(edge)
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID"""
        return self.nodes.get(node_id)
    
    def get_neighbors(self, node_id: str, direction: str = "out") -> List[GraphNode]:
        """Get neighboring nodes"""
        if direction == "out":
            edges = self._outgoing.get(node_id, [])
            return [self.nodes[e.target] for e in edges if e.target in self.nodes]
        elif direction == "in":
            edges = self._incoming.get(node_id, [])
            return [self.nodes[e.source] for e in edges if e.source in self.nodes]
        else:
            raise ValueError("direction must be 'in' or 'out'")
    
    def find_path(self, start: str, end: str, max_depth: int = 5) -> Optional[List[str]]:
        """Find a path between two nodes using BFS"""
        if start not in self.nodes or end not in self.nodes:
            return None
        
        queue = [(start, [start])]
        visited: Set[str] = {start}
        
        while queue:
            current, path = queue.pop(0)
            if len(path) > max_depth:
                continue
            
            if current == end:
                return path
            
            for edge in self._outgoing.get(current, []):
                if edge.target not in visited:
                    visited.add(edge.target)
                    queue.append((edge.target, path + [edge.target]))
        
        return None
