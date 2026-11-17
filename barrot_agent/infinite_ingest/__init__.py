"""Infinite ingestion + transmutation pipeline.

Modules:
    ingestor       fetch, hype-gate, dedupe, store raw, prune
    transmuter     raw source -> extractive Barrot memory records
    cross_analyzer shared-term graph at ``data/connections.json``
    refiner        test -> gap -> ingest -> transmute -> patch -> re-test

Hard limits: 10 ingests per run, 1 refinement per capability per run, stop on
rate limit, 500 MB raw cap with oldest-first pruning.
"""

from .cross_analyzer import CrossAnalyzer
from .ingestor import DEFAULT_MAX_INGESTS, IngestReport, Ingestor
from .models import (
    Document,
    IngestItem,
    MemoryRecord,
    RawRecord,
    RateLimitStop,
    utc_now,
)
from .refiner import RefinementResult, Refiner, ScoreResult, score_capability
from .sources import SourceFetcher
from .storage import DEFAULT_RAW_CAP_BYTES, Store
from .transmuter import Transmuter

__all__ = [
    "CrossAnalyzer",
    "DEFAULT_MAX_INGESTS",
    "DEFAULT_RAW_CAP_BYTES",
    "Document",
    "IngestItem",
    "IngestReport",
    "Ingestor",
    "MemoryRecord",
    "RawRecord",
    "RateLimitStop",
    "RefinementResult",
    "Refiner",
    "ScoreResult",
    "SourceFetcher",
    "Store",
    "Transmuter",
    "score_capability",
    "utc_now",
]
