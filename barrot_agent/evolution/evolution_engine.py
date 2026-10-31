"""
Barrot Evolution Engine.

Pipeline:
    Acquire -> Validate -> Score -> Synthesize -> Evaluate -> Propose

The engine never silently rewrites production code. Improvements become
structured proposals that can be tested before adoption.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "evolution"
CORPUS_FILE = DATA_DIR / "knowledge_corpus.json"


class EvolutionEngine:
    """Build and improve Barrot's structured knowledge corpus."""

    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def load_corpus(self) -> list[dict[str, Any]]:
        if not CORPUS_FILE.exists():
            return []
        return json.loads(CORPUS_FILE.read_text(encoding="utf-8"))

    def ingest(
        self,
        source: str,
        content: str,
        domain: str,
        confidence: float = 0.5,
    ) -> dict[str, Any]:
        """Add validated knowledge with provenance and deduplication."""
        digest = hashlib.sha256(content.encode()).hexdigest()
        corpus = self.load_corpus()

        if any(item["id"] == digest for item in corpus):
            return {"status": "duplicate", "id": digest}

        item = {
            "id": digest,
            "source": source,
            "domain": domain,
            "content": content,
            "confidence": max(0.0, min(1.0, confidence)),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }

        corpus.append(item)
        CORPUS_FILE.write_text(
            json.dumps(corpus, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return {"status": "ingested", "id": digest}

    def synthesize(self) -> dict[str, Any]:
        """Produce a high-level map of accumulated knowledge."""
        corpus = self.load_corpus()
        domains: dict[str, int] = {}

        for item in corpus:
            domain = item.get("domain", "general")
            domains[domain] = domains.get(domain, 0) + 1

        return {
            "knowledge_items": len(corpus),
            "domains": domains,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def improvement_targets(self) -> list[dict[str, str]]:
        """Identify capability gaps without autonomously modifying code."""
        corpus = self.load_corpus()
        domains = {item.get("domain") for item in corpus}

        priorities = [
            ("agent_orchestration", "Multi-agent planning and delegation"),
            ("software_engineering", "Code analysis, testing, and repair"),
            ("reasoning", "Verification and evidence-based reasoning"),
            ("security", "Credential isolation and safe tool execution"),
        ]

        return [
            {"domain": domain, "goal": goal} for domain, goal in priorities if domain not in domains
        ]
