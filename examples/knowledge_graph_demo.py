"""
Example Usage: Knowledge Graph and Reasoning Demo

Run from repository root with:
    PYTHONPATH=. python examples/knowledge_graph_demo.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.knowledge_graph import initialize_knowledge_graph

def main():
    print("=" * 60)
    print("Knowledge Graph and Reasoning Demo")
    print("=" * 60)
    
    # Initialize
    components = initialize_knowledge_graph()
    kg = components['knowledge_graph']
    reasoning = components['reasoning']
    
    # 1. Build knowledge graph
    print("\n1. Building knowledge graph...")
    
    # Add nodes
    kg.add_node('python', 'language', {'domain': 'programming', 'paradigm': 'multi'})
    kg.add_node('java', 'language', {'domain': 'programming', 'paradigm': 'oop'})
    kg.add_node('ml', 'concept', {'domain': 'ai', 'field': 'machine_learning'})
    kg.add_node('dl', 'concept', {'domain': 'ai', 'field': 'deep_learning'})
    kg.add_node('nlp', 'concept', {'domain': 'ai', 'application': 'language'})
    
    print(f"   Nodes added: {len(kg.nodes)}")
    
    # Add relationships
    kg.add_relationship('python', 'ml', 'USED_FOR')
    kg.add_relationship('ml', 'dl', 'INCLUDES')
    kg.add_relationship('dl', 'nlp', 'ENABLES')
    kg.add_relationship('java', 'ml', 'USED_FOR')
    
    print(f"   Relationships added: {len(kg.relationships)}")
    
    # 2. Query neighbors
    print("\n2. Querying neighbors...")
    neighbors = kg.query_neighbors('ml')
    print(f"   Neighbors of 'ml': {[n['id'] for n in neighbors]}")
    
    # 3. Find paths
    print("\n3. Finding paths...")
    paths = kg.query_path('python', 'nlp')
    print(f"   Paths from 'python' to 'nlp': {len(paths)}")
    for i, path in enumerate(paths):
        print(f"   Path {i+1}: {' -> '.join(path)}")
    
    # 4. Contextual reasoning
    print("\n4. Performing contextual reasoning...")
    inferred = reasoning.infer_relationships('ai')
    print(f"   Inferred relationships in 'ai' domain: {len(inferred)}")
    for rel in inferred[:3]:  # Show first 3
        print(f"   - {rel['source']} -[{rel['type']}]-> {rel['target']} (confidence: {rel['confidence']:.2f})")
    
    # 5. Cross-domain reasoning
    print("\n5. Cross-domain reasoning...")
    cross = reasoning.cross_domain_reasoning('programming', 'ai')
    print(f"   Domains: {cross['domains']}")
    print(f"   Nodes in domain 1: {cross['domain1_nodes']}")
    print(f"   Nodes in domain 2: {cross['domain2_nodes']}")
    print(f"   Cross-domain connections: {len(cross['connections'])}")
    for insight in cross['insights']:
        print(f"   - {insight}")
    
    print("\n" + "=" * 60)
    print("Demo Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
