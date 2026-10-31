"""
Barrot Evidence Normalization Engine.

Converts acquired textual material into bounded, traceable evidence records.
This module does not determine truth. It extracts candidate claims and
preserves their source context for later corroboration.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any


class EvidenceNormalizationEngine:
    """Extract simple candidate claims while preserving provenance."""

    @staticmethod
    def _sentences(content: str) -> list[str]:
        """Split text into bounded candidate statements."""
        sentences = re.split(r"(?<=[.!?])\s+", content.strip())
        return [sentence.strip() for sentence in sentences if len(sentence.strip()) >= 20]

    def normalize(
        self,
        content: str,
        source: str,
        source_url: str = "",
        content_hash: str = "",
    ) -> list[dict[str, Any]]:
        """Return individually identifiable candidate evidence records."""
        records = []

        for sentence in self._sentences(content):
            claim_id = hashlib.sha256(f"{source}:{sentence}".encode("utf-8")).hexdigest()

            records.append(
                {
                    "claim_id": claim_id,
                    "claim": sentence,
                    "source": source,
                    "source_url": source_url,
                    "content_hash": content_hash,
                    "candidate": True,
                }
            )

        return records
