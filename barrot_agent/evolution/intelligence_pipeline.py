"""Evidence-based recursive intelligence acquisition for Barrot.

This module expands Barrot's knowledge graph without autonomously modifying
production code. Every acquired item retains source provenance and a score.
"""

from __future__ import annotations

from barrot_agent.trust import TrustEngine

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from barrot_agent.evolution.event_bus import CognitiveEvent, CognitiveEventBus
from barrot_agent.evolution.evidence_normalization import EvidenceNormalizationEngine
from barrot_agent.evolution.evidence_store import EvidenceStore

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "evolution"
CORPUS_FILE = DATA_DIR / "intelligence_corpus.json"

SOURCES = [
    {
        "name": "arXiv AI research",
        "url": "https://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.MA&start=0&max_results=25&sortBy=submittedDate&sortOrder=descending",
        "type": "research",
    },
]


class IntelligencePipeline:
    trust_engine = TrustEngine()
    """Acquire, preserve, score, and recursively prioritize knowledge."""

    def __init__(self, event_bus: CognitiveEventBus | None = None) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.event_bus = event_bus or CognitiveEventBus()
        self.normalizer = EvidenceNormalizationEngine()
        self.evidence_store = EvidenceStore()

    def acquire(self) -> list[dict[str, Any]]:
        items = []

        for source in SOURCES:
            try:
                response = requests.get(source["url"], timeout=30)
                response.raise_for_status()

                content = response.text
                digest = hashlib.sha256(content.encode()).hexdigest()

                items.append(
                    {
                        "source": source["name"],
                        "source_url": source["url"],
                        "type": source["type"],
                        "content_hash": digest,
                        "retrieved_at": datetime.now(timezone.utc).isoformat(),
                        "content": content[:50000],
                    }
                )
            except requests.RequestException as error:
                print(f"Acquisition failed for {source['name']}: {error}")

        return items

    @staticmethod
    def score(item: dict[str, Any]) -> dict[str, Any]:
        """Apply transparent initial scoring."""
        text = item.get("content", "").lower()

        keywords = [
            "agent",
            "reasoning",
            "orchestration",
            "planning",
            "memory",
            "reinforcement",
            "multi-agent",
            "tool use",
        ]

        relevance = sum(keyword in text for keyword in keywords)
        item["impact_score"] = relevance / len(keywords)
        item["scored_at"] = datetime.now(timezone.utc).isoformat()
        return item

    def load_corpus(self) -> list[dict[str, Any]]:
        if not CORPUS_FILE.exists():
            return []

        return json.loads(CORPUS_FILE.read_text())

    def synthesize(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        corpus = self.load_corpus()
        known_hashes = {item.get("content_hash") for item in corpus}

        new_items = []
        for item in items:
            if item["content_hash"] not in known_hashes:
                new_items.append(self.score(item))

        corpus.extend(new_items)
        CORPUS_FILE.write_text(
            json.dumps(corpus, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        for item in new_items:
            self.event_bus.publish(
                CognitiveEvent(
                    event_type="research_acquired",
                    payload={
                        "claim": item["content"][:1000],
                        "content_hash": item["content_hash"],
                        "source_url": item["source_url"],
                        "type": item["type"],
                        "impact_score": item.get("impact_score", 0.0),
                    },
                    source=item["source"],
                )
            )

            evidence_records = self.normalizer.normalize(
                content=item["content"],
                source=item["source"],
                source_url=item.get("source_url", ""),
                content_hash=item["content_hash"],
            )

            for evidence in evidence_records:
                evidence["trust"] = {
                    "authoritative": trust_verification["authoritative"],
                    "state_verified": trust_verification["verification"]["passed"],
                    "confidence": trust_verification["confidence"],
                    "syndromes": trust_verification["syndromes"],
                    "certificate": trust_verification["certificate"],
                }

                stored = self.evidence_store.add(evidence)

                # Publish only newly stored evidence. Duplicate evidence is
                # already represented in the persistent evidence store.
                if stored["status"] != "stored":
                    continue

                self.event_bus.publish(
                    CognitiveEvent(
                        event_type="claim_submitted",
                        payload=evidence,
                        source=item["source"],
                    )
                )

        priorities = sorted(
            corpus,
            key=lambda item: item.get("impact_score", 0),
            reverse=True,
        )[:10]

        return {
            "new_items": len(new_items),
            "total_items": len(corpus),
            "priority_research": [
                {
                    "source": item["source"],
                    "impact_score": item.get("impact_score", 0),
                    "retrieved_at": item["retrieved_at"],
                }
                for item in priorities
            ],
        }

    def run_cycle(self) -> dict[str, Any]:
        """Run one evidence-acquisition cycle with trust verification."""
        acquired = self.acquire()

        trust_verification = self.trust_engine.execute(
            task="intelligence_acquisition_cycle",
            expected_state={
                "acquisition_completed": True,
                "items_available": True,
            },
            observed_state={
                "acquisition_completed": True,
                "items_available": bool(acquired),
            },
            validators=[
                lambda state: state["acquisition_completed"] is True,
                lambda state: state["items_available"] is True,
            ],
            risk="medium",
            transport_success=True,
            provenance=["IntelligencePipeline.acquire"],
        )
        if not trust_verification["authoritative"]:
            return {
                "new_items": 0,
                "total_items": len(self.load_corpus()),
                "priority_research": [],
                "trust": {
                    "authoritative": False,
                    "state_verified": trust_verification["verification"]["passed"],
                    "confidence": trust_verification["confidence"],
                    "syndromes": trust_verification["syndromes"],
                    "certificate": trust_verification["certificate"],
                },
            }

        result = self.synthesize(acquired)
        result["trust"] = {
            "authoritative": trust_verification["authoritative"],
            "state_verified": trust_verification["verification"]["passed"],
            "confidence": trust_verification["confidence"],
            "syndromes": trust_verification["syndromes"],
            "certificate": trust_verification["certificate"],
        }
        return result


if __name__ == "__main__":
    pipeline = IntelligencePipeline()
    print(json.dumps(pipeline.run_cycle(), indent=2))
