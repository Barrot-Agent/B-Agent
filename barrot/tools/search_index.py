# barrot/tools/search_index.py
from typing import List, Dict, Any
from dataclasses import dataclass, field

@dataclass
class Document:
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class SearchIndex:
    """Simple search index for documents"""
    
    def __init__(self):
        self.documents: Dict[str, Document] = {}
    
    def add_document(self, doc: Document) -> None:
        """Add a document to the index"""
        self.documents[doc.id] = doc
    
    def search(self, query: str, limit: int = 10) -> List[Document]:
        """Search for documents matching query"""
        # Simple substring search - would use proper search engine in production
        results = []
        query_lower = query.lower()
        for doc in self.documents.values():
            if query_lower in doc.content.lower():
                results.append(doc)
                if len(results) >= limit:
                    break
        return results
    
    def get_document(self, doc_id: str) -> Document:
        """Retrieve a document by ID"""
        return self.documents.get(doc_id)
