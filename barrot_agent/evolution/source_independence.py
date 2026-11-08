"""
Barrot Source Independence Engine.

Groups evidence by source identity so repeated evidence from the same source
does not count as independent corroboration.
"""

from __future__ import annotations

from urllib.parse import urlparse


class SourceIndependenceEngine:
    """Determine whether evidence sources are meaningfully independent."""

    @staticmethod
    def source_identity(source: str, source_url: str = "") -> str:
        """Return a stable identity, preferring the source URL domain."""
        if source_url:
            domain = urlparse(source_url).netloc.lower()
            if domain:
                return domain.removeprefix("www.")
        return source.strip().lower()

    def independent_sources(
        self,
        evidence_records: list[dict],
    ) -> dict[str, list[dict]]:
        """Group evidence records by independent source identity."""
        groups: dict[str, list[dict]] = {}

        for record in evidence_records:
            identity = self.source_identity(
                record.get("source", ""),
                record.get("source_url", ""),
            )
            groups.setdefault(identity, []).append(record)

        return groups
