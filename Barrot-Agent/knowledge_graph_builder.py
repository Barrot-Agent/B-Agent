#!/usr/bin/env python3
"""
Knowledge Graph Builder
Builds comprehensive knowledge graph from ingested data
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime, timezone
import hashlib


class KnowledgeGraphBuilder:
    """Build and maintain knowledge graph from ingested content"""
    
    def __init__(self, repo_root: Path = None):
        """Initialize the knowledge graph builder"""
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent
        self.memory_bundles = self.repo_root / "memory-bundles"
        self.graph_path = self.memory_bundles / "knowledge_graph.json"
        
        # Load or initialize graph
        self.graph = self._load_graph()
        
        # Graph statistics
        self.stats = {
            "total_nodes": 0,
            "total_edges": 0,
            "node_types": {},
            "last_updated": None
        }
    
    def _load_graph(self) -> Dict[str, Any]:
        """Load existing knowledge graph or create new one"""
        if self.graph_path.exists():
            with open(self.graph_path, 'r') as f:
                return json.load(f)
        
        return {
            "nodes": {},
            "edges": [],
            "metadata": {
                "created": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0"
            }
        }
    
    def _save_graph(self):
        """Save knowledge graph to disk"""
        self.memory_bundles.mkdir(parents=True, exist_ok=True)
        self.graph["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        with open(self.graph_path, 'w') as f:
            json.dump(self.graph, f, indent=2)
    
    def add_node(self, node_id: str, node_type: str, properties: Dict[str, Any]):
        """Add a node to the knowledge graph"""
        self.graph["nodes"][node_id] = {
            "id": node_id,
            "type": node_type,
            "properties": properties,
            "created": datetime.now(timezone.utc).isoformat()
        }
        
        self.stats["total_nodes"] = len(self.graph["nodes"])
        self.stats["node_types"][node_type] = self.stats["node_types"].get(node_type, 0) + 1
    
    def add_edge(self, source_id: str, target_id: str, relationship: str, properties: Dict[str, Any] = None):
        """Add an edge (relationship) between two nodes"""
        edge = {
            "source": source_id,
            "target": target_id,
            "relationship": relationship,
            "properties": properties or {},
            "created": datetime.now(timezone.utc).isoformat()
        }
        
        self.graph["edges"].append(edge)
        self.stats["total_edges"] = len(self.graph["edges"])
    
    def build_from_ingested_data(self, data_path: Path):
        """Build knowledge graph from ingested data"""
        print(f"[KnowledgeGraph] Building graph from: {data_path}")
        
        # Process all ingested content
        if data_path.is_dir():
            for file_path in data_path.rglob("*.json"):
                self._process_ingested_file(file_path)
        elif data_path.is_file():
            self._process_ingested_file(data_path)
        
        # Save graph
        self._save_graph()
        
        print(f"[KnowledgeGraph] Graph built: {self.stats['total_nodes']} nodes, {self.stats['total_edges']} edges")
    
    def _process_ingested_file(self, file_path: Path):
        """Process a single ingested file and extract entities/relationships"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Extract entities and create nodes
            content_id = data.get('id', hashlib.sha256(str(file_path).encode()).hexdigest()[:16])
            content_type = data.get('type', 'unknown')
            
            # Add content node
            self.add_node(content_id, content_type, {
                "source": data.get('source', 'unknown'),
                "ingested_at": data.get('ingested_at'),
                "metadata": data.get('metadata', {})
            })
            
            # Extract relationships (simplified)
            self._extract_relationships(content_id, data)
            
        except Exception as e:
            print(f"[KnowledgeGraph] Error processing {file_path}: {str(e)}")
    
    def _extract_relationships(self, content_id: str, data: Dict[str, Any]):
        """Extract relationships from content data"""
        # Example: Link to source
        source = data.get('source')
        if source:
            source_id = hashlib.sha256(source.encode()).hexdigest()[:16]
            if source_id not in self.graph["nodes"]:
                self.add_node(source_id, "source_platform", {"name": source})
            self.add_edge(content_id, source_id, "from_source")
        
        # Example: Link to topics/tags
        topics = data.get('topics', data.get('tags', data.get('focus', [])))
        for topic in topics:
            if isinstance(topic, str):
                topic_id = hashlib.sha256(topic.encode()).hexdigest()[:16]
                if topic_id not in self.graph["nodes"]:
                    self.add_node(topic_id, "topic", {"name": topic})
                self.add_edge(content_id, topic_id, "relates_to")
    
    def query_nodes_by_type(self, node_type: str) -> List[Dict[str, Any]]:
        """Query all nodes of a specific type"""
        return [
            node for node in self.graph["nodes"].values()
            if node["type"] == node_type
        ]
    
    def get_connected_nodes(self, node_id: str) -> List[str]:
        """Get all nodes connected to a given node"""
        connected = set()
        
        for edge in self.graph["edges"]:
            if edge["source"] == node_id:
                connected.add(edge["target"])
            elif edge["target"] == node_id:
                connected.add(edge["source"])
        
        return list(connected)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        self.stats["total_nodes"] = len(self.graph["nodes"])
        self.stats["total_edges"] = len(self.graph["edges"])
        self.stats["last_updated"] = self.graph["metadata"].get("last_updated")
        return self.stats.copy()
    
    def export_visualization_data(self) -> Dict[str, Any]:
        """Export graph data in format suitable for visualization"""
        return {
            "nodes": [
                {
                    "id": node_id,
                    "label": node.get("properties", {}).get("name", node_id[:8]),
                    "type": node["type"]
                }
                for node_id, node in self.graph["nodes"].items()
            ],
            "edges": [
                {
                    "source": edge["source"],
                    "target": edge["target"],
                    "label": edge["relationship"]
                }
                for edge in self.graph["edges"]
            ]
        }


def main():
    """Main execution"""
    builder = KnowledgeGraphBuilder()
    
    # Build graph from auto-ingested data
    auto_ingested_path = builder.memory_bundles / "auto-ingested"
    if auto_ingested_path.exists():
        builder.build_from_ingested_data(auto_ingested_path)
    
    # Print stats
    stats = builder.get_stats()
    print(f"\nKnowledge Graph Statistics:")
    print(f"  Total Nodes: {stats['total_nodes']}")
    print(f"  Total Edges: {stats['total_edges']}")
    print(f"  Node Types: {stats['node_types']}")
    
    return builder


if __name__ == "__main__":
    main()
