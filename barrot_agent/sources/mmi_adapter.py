from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from barrot_agent.ingestion.mmi_contract import MMI_MAX_DEPTH
from barrot_agent.sources.source_acquisition import (
    AcquisitionTarget,
    SourceAcquisitionPlanner,
)


ADAPTER_VERSION = "1.2"


@dataclass(frozen=True)
class MMIIngestionRequest:
    target_id: str
    need_id: str
    source_uri: str
    source_type: str
    name: str
    purpose: str
    requested_version: str
    publisher: str | None
    mmi_required: bool
    independent_corroboration_required: bool
    max_component_depth: int
    max_provenance_depth: int
    provenance_requirements: list[str]
    verification_requirements: list[str]

    def canonical(self) -> dict[str, Any]:
        return asdict(self)

    def content_hash(self) -> str:
        payload = json.dumps(
            self.canonical(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        return sha256(payload).hexdigest()


class PlannerMMIAdapter:
    """
    Deterministically maps an AcquisitionTarget into an MMI request.

    The adapter does not acquire, download, execute, install, or ingest.
    AcquisitionTarget remains authoritative.

    A planner instance is only required for target lookup by ID.
    Direct target-to-request conversion does not instantiate a planner.
    """

    def __init__(
        self,
        planner: SourceAcquisitionPlanner | None = None,
    ):
        self.planner = planner

    def build_request(
        self,
        target: AcquisitionTarget,
    ) -> MMIIngestionRequest:
        if not isinstance(target, AcquisitionTarget):
            raise TypeError(
                "PlannerMMIAdapter requires an AcquisitionTarget"
            )

        if not target.target_id:
            raise ValueError(
                "acquisition target requires target_id"
            )

        if not target.need_id:
            raise ValueError(
                f"{target.target_id}: acquisition target requires need_id"
            )

        source_uri = (
            target.acquisition_uri
            or target.discovery_uri
            or f"acquisition-target://{target.target_id}"
        )

        return MMIIngestionRequest(
            target_id=target.target_id,
            need_id=target.need_id,
            source_uri=source_uri,
            source_type=target.source_type,
            name=target.name,
            purpose=target.purpose,
            requested_version="unspecified",
            publisher=target.publisher,
            mmi_required=target.mmi_required,
            independent_corroboration_required=(
                target.independent_corroboration_required
            ),
            max_component_depth=MMI_MAX_DEPTH,
            max_provenance_depth=MMI_MAX_DEPTH,
            provenance_requirements=list(
                target.provenance_requirements
            ),
            verification_requirements=list(
                target.verification_requirements
            ),
        )

    def build_request_by_id(
        self,
        target_id: str,
    ) -> MMIIngestionRequest:
        if self.planner is None:
            raise RuntimeError(
                "build_request_by_id requires an explicit "
                "SourceAcquisitionPlanner instance"
            )

        for target in self.planner.list_targets():
            if target.target_id == target_id:
                return self.build_request(target)

        raise KeyError(
            f"acquisition target not found: {target_id}"
        )

    def export_request(
        self,
        request: MMIIngestionRequest,
        directory: str | Path = ".barrot/mmi/requests",
    ) -> Path:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        path = directory / f"{request.target_id}.json"
        temporary = path.with_suffix(".tmp")

        temporary.write_text(
            json.dumps(
                {
                    "adapter_version": ADAPTER_VERSION,
                    "request_hash": request.content_hash(),
                    "request": request.canonical(),
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        temporary.replace(path)
        return path
