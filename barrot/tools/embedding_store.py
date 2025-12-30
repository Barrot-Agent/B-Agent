# barrot/tools/embedding_store.py
from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class Embedding:
    id: str
    vector: List[float]
    metadata: Dict[str, Any]

class EmbeddingStore:
    """Store and retrieve embeddings for semantic search"""
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.embeddings: Dict[str, Embedding] = {}
    
    def add_embedding(self, embedding: Embedding) -> None:
        """Add an embedding to the store"""
        if len(embedding.vector) != self.dimension:
            raise ValueError(f"Expected dimension {self.dimension}, got {len(embedding.vector)}")
        self.embeddings[embedding.id] = embedding
    
    def search_similar(self, query_vector: List[float], limit: int = 10) -> List[Embedding]:
        """Find most similar embeddings using cosine similarity"""
        if len(query_vector) != self.dimension:
            raise ValueError(f"Expected dimension {self.dimension}, got {len(query_vector)}")
        
        # Calculate cosine similarities
        similarities = []
        query_np = np.array(query_vector)
        query_norm = np.linalg.norm(query_np)
        
        for emb in self.embeddings.values():
            emb_np = np.array(emb.vector)
            emb_norm = np.linalg.norm(emb_np)
            if query_norm > 0 and emb_norm > 0:
                similarity = np.dot(query_np, emb_np) / (query_norm * emb_norm)
                similarities.append((similarity, emb))
        
        # Sort by similarity and return top results
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [emb for _, emb in similarities[:limit]]
    
    def get_embedding(self, emb_id: str) -> Optional[Embedding]:
        """Retrieve an embedding by ID"""
        return self.embeddings.get(emb_id)
