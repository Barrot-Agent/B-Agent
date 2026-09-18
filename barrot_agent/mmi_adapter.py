from __future__ import annotations

from hashlib import sha256
from typing import Any

from .mmi_v1 import (
    EvidenceRecord,
    MMIEngine,
    MMIRecord,
    ParseState,
    ProvenanceClass,
    SourceRecord,
)


class MMIExistingSystemsAdapter:
    """
    Thin adapter between the MMI protocol and Barrot's existing
    acquisition, normalization, corroboration, and independence engines.

    MMI owns protocol state and provenance boundaries.
    Existing Barrot systems remain authoritative for their specialties.
    """

    def __init__(
        self,
        *,
        acquisition=None,
        normalization=None,
        corroboration=None,
        independence=None,
    ):
        self.acquisition = acquisition
        self.normalization = normalization
        self.corroboration = corroboration
        self.independence = independence

        self.engine = MMIEngine(
            components={
                "acquisition": acquisition,
                "normalization": normalization,
                "corroboration": corroboration,
                "independence": independence,
            }
        )

    def acquire(self) -> list[dict[str, Any]]:
        if self.acquisition is None:
            raise RuntimeError("MMI acquisition component is not configured")

        return self.acquisition.acquire()

    def normalize(
        self,
        content: str,
        source: str,
        source_url: str = "",
        content_hash: str = "",
    ) -> list[dict[str, Any]]:
        if self.normalization is None:
            raise RuntimeError(
                "MMI normalization component is not configured"
            )

        return self.normalization.normalize(
            content,
            source,
            source_url,
            content_hash,
        )

    def corroborate(self, claim: Any, sources: list[str] | None = None):
        if self.corroboration is None:
            raise RuntimeError(
                "MMI corroboration component is not configured"
            )

        return self.corroboration.corroborate(
            claim,
            sources,
        )

    def independent_sources(self, evidence_records: list[dict]):
        if self.independence is None:
            raise RuntimeError(
                "MMI independence component is not configured"
            )

        return self.independence.independent_sources(
            evidence_records
        )

    @staticmethod
    def source_record(
        *,
        source_id: str,
        uri: str,
        provenance_class: ProvenanceClass,
        content: str = "",
        depth: int = 1,
        observed_at: str = "",
    ) -> SourceRecord:
        content_hash = ""
        if content:
            content_hash = (
                "sha256:"
                + sha256(content.encode("utf-8")).hexdigest()
            )

        return SourceRecord(
            source_id=source_id,
            uri=uri,
            provenance_class=provenance_class,
            depth=depth,
            content_hash=content_hash,
            observed_at=observed_at,
        )

    @staticmethod
    def evidence_record(
        *,
        evidence_id: str,
        claim: str,
        source_ids: list[str],
        state: ParseState = ParseState.OBSERVED,
        independent: bool = False,
        content: str = "",
        observed_at: str = "",
    ) -> EvidenceRecord:
        content_hash = ""
        if content:
            content_hash = (
                "sha256:"
                + sha256(content.encode("utf-8")).hexdigest()
            )

        return EvidenceRecord(
            evidence_id=evidence_id,
            claim=claim,
            state=state,
            source_ids=list(source_ids),
            independent=independent,
            content_hash=content_hash,
            observed_at=observed_at,
        )

    def create_record(
        self,
        ingestion_id: str,
        dataset: dict,
        provenance: dict,
    ) -> MMIRecord:
        return self.engine.create_record(
            ingestion_id,
            dataset,
            provenance,
        )
