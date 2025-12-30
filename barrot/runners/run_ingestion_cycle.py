#!/usr/bin/env python3
# barrot/runners/run_ingestion_cycle.py
"""
Run an ingestion cycle - fetch and process new research
"""
from barrot.config import config
from barrot.ingestion.arxiv_client import ArxivClient
from barrot.ingestion.doi_resolver import DOIResolver
from barrot.tools.search_index import SearchIndex, Document

def run_ingestion_cycle(topics: list = None) -> dict:
    """
    Execute one cycle of ingestion:
    1. Fetch from arXiv and other sources
    2. Process and index documents
    3. Update search index
    """
    print("Starting ingestion cycle...")
    
    if topics is None:
        topics = [
            "Riemann Hypothesis",
            "P vs NP",
            "Navier-Stokes",
        ]
    
    # Initialize clients
    arxiv_client = ArxivClient(config.ingestion.arxiv_api_url)
    search_index = SearchIndex()
    
    total_docs = 0
    
    for topic in topics:
        print(f"Fetching papers on: {topic}")
        try:
            # Search arXiv
            results = arxiv_client.search(topic, max_results=5)
            
            # Add to search index
            for i, result in enumerate(results):
                doc = Document(
                    id=f"{topic}_{i}",
                    content=str(result),
                    metadata={"topic": topic, "source": "arxiv"}
                )
                search_index.add_document(doc)
                total_docs += 1
        except Exception as e:
            print(f"Error fetching {topic}: {e}")
    
    return {
        "topics_processed": len(topics),
        "documents_indexed": total_docs,
        "index_size": len(search_index.documents)
    }

def main():
    """Main entry point"""
    results = run_ingestion_cycle()
    print("\nIngestion cycle complete:")
    for key, value in results.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
