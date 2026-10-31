from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional


REGISTRY_VERSION = "1.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class SourceIdentity:
    source_id: str
    source_type: str
    name: str
    origin: str
    uri: Optional[str] = None
    publisher: Optional[str] = None


@dataclass
class SourceVersion:
    version: Optional[str] = None
    retrieved_at: str = field(default_factory=utc_now)
    content_hash: Optional[str] = None
    supersedes: Optional[str] = None


@dataclass
class SourceScope:
    total_scope: Optional[str] = None
    parsed_scope: Optional[str] = None
    unavailable_scope: list[str] = field(default_factory=list)
    boundaries: list[str] = field(default_factory=list)


@dataclass
class SourceIngestion:
    mmi_status: str = "NOT_STARTED"
    ingestion_state: str = "RECEIVED"
    parsed_scope: Optional[str] = None
    unparsed_scope: Optional[str] = None
    component_count: int = 0


@dataclass
class SourceProvenance:
    source_lineage: list[str] = field(default_factory=list)
    component_lineage: list[str] = field(default_factory=list)
    transformations: list[str] = field(default_factory=list)


@dataclass
class SourceEvidence:
    claims: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    corroboration: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class SourceKnowledge:
    concepts: list[str] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    identified_gaps: list[str] = field(default_factory=list)


@dataclass
class SourceLifecycle:
    state: str = "ACTIVE"
    superseded_by: Optional[str] = None
    revalidation_required: bool = False
    inaccessible: bool = False


@dataclass
class SourceRecord:
    identity: SourceIdentity
    version: SourceVersion = field(default_factory=SourceVersion)
    scope: SourceScope = field(default_factory=SourceScope)
    ingestion: SourceIngestion = field(default_factory=SourceIngestion)
    provenance: SourceProvenance = field(default_factory=SourceProvenance)
    evidence: SourceEvidence = field(default_factory=SourceEvidence)
    knowledge: SourceKnowledge = field(default_factory=SourceKnowledge)
    lifecycle: SourceLifecycle = field(default_factory=SourceLifecycle)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SourceRecord":
        return cls(
            identity=SourceIdentity(**data["identity"]),
            version=SourceVersion(**data.get("version", {})),
            scope=SourceScope(**data.get("scope", {})),
            ingestion=SourceIngestion(**data.get("ingestion", {})),
            provenance=SourceProvenance(**data.get("provenance", {})),
            evidence=SourceEvidence(**data.get("evidence", {})),
            knowledge=SourceKnowledge(**data.get("knowledge", {})),
            lifecycle=SourceLifecycle(**data.get("lifecycle", {})),
            created_at=data.get("created_at", utc_now()),
            updated_at=data.get("updated_at", utc_now()),
        )


class SourceRegistry:
    """
    Durable registry for Barrot source identity, provenance, ingestion,
    evidence, knowledge, and lifecycle.

    Registry mutation is append-safe at the record level: updating a source
    preserves the source identity and writes the new complete state.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._records: dict[str, SourceRecord] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return

        raw = json.loads(self.path.read_text(encoding="utf-8"))
        records = raw.get("records", {})
        self._records = {
            source_id: SourceRecord.from_dict(record)
            for source_id, record in records.items()
        }

    def _save(self) -> None:
        payload = {
            "registry_version": REGISTRY_VERSION,
            "updated_at": utc_now(),
            "records": {
                source_id: record.to_dict()
                for source_id, record in sorted(self._records.items())
            },
        }

        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temporary.replace(self.path)

    def register(self, record: SourceRecord) -> SourceRecord:
        existing = self._records.get(record.identity.source_id)

        if existing is not None:
            if existing.version.content_hash == record.version.content_hash:
                return existing

            record.version.supersedes = existing.identity.source_id
            record.lifecycle.revalidation_required = True

        record.updated_at = utc_now()
        self._records[record.identity.source_id] = record
        self._save()
        return record

    def get(self, source_id: str) -> Optional[SourceRecord]:
        return self._records.get(source_id)

    def require(self, source_id: str) -> SourceRecord:
        record = self.get(source_id)
        if record is None:
            raise KeyError(f"Unknown source_id: {source_id}")
        return record

    def remove(self, source_id: str) -> None:
        """
        Deliberately unsupported.

        Source history must remain available for provenance and audit.
        """
        raise RuntimeError(
            "Source deletion is not supported by the Barrot Source Registry"
        )

    def update(
        self,
        source_id: str,
        *,
        ingestion: Optional[SourceIngestion] = None,
        provenance: Optional[SourceProvenance] = None,
        evidence: Optional[SourceEvidence] = None,
        knowledge: Optional[SourceKnowledge] = None,
        lifecycle: Optional[SourceLifecycle] = None,
        scope: Optional[SourceScope] = None,
    ) -> SourceRecord:
        record = self.require(source_id)

        if ingestion is not None:
            record.ingestion = ingestion
        if provenance is not None:
            record.provenance = provenance
        if evidence is not None:
            record.evidence = evidence
        if knowledge is not None:
            record.knowledge = knowledge
        if lifecycle is not None:
            record.lifecycle = lifecycle
        if scope is not None:
            record.scope = scope

        record.updated_at = utc_now()
        self._save()
        return record

    def list_sources(self) -> list[SourceRecord]:
        return [
            self._records[source_id]
            for source_id in sorted(self._records)
        ]

    def find_by_type(self, source_type: str) -> list[SourceRecord]:
        return [
            record
            for record in self._records.values()
            if record.identity.source_type == source_type
        ]

    def find_gaps(self) -> dict[str, list[str]]:
        return {
            record.identity.source_id: list(record.knowledge.identified_gaps)
            for record in self._records.values()
            if record.knowledge.identified_gaps
        }

    def summary(self) -> dict[str, Any]:
        records = self.list_sources()

        return {
            "registry_version": REGISTRY_VERSION,
            "source_count": len(records),
            "active_count": sum(
                r.lifecycle.state == "ACTIVE" for r in records
            ),
            "revalidation_required": sum(
                r.lifecycle.revalidation_required for r in records
            ),
            "inaccessible_count": sum(
                r.lifecycle.inaccessible for r in records
            ),
            "gap_count": sum(
                len(r.knowledge.identified_gaps) for r in records
            ),
            "types": sorted(
                {
                    r.identity.source_type
                    for r in records
                }
            ),
        }


def register_file_source(
    registry: SourceRegistry,
    *,
    source_id: str,
    source_type: str,
    name: str,
    origin: str,
    path: str | Path,
    publisher: Optional[str] = None,
) -> SourceRecord:
    file_path = Path(path)
    data = file_path.read_bytes()

    record = SourceRecord(
        identity=SourceIdentity(
            source_id=source_id,
            source_type=source_type,
            name=name,
            origin=origin,
            uri=str(file_path),
            publisher=publisher,
        ),
        version=SourceVersion(
            content_hash=sha256_bytes(data),
        ),
        scope=SourceScope(
            total_scope=f"{len(data)} bytes",
            parsed_scope=f"{len(data)} bytes",
        ),
        ingestion=SourceIngestion(
            mmi_status="REGISTERED",
            ingestion_state="RECEIVED",
            parsed_scope=f"{len(data)} bytes",
            component_count=1,
        ),
    )

    return registry.register(record)
