from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


PLANNER_VERSION = "1.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass
class AcquisitionNeed:
    need_id: str
    category: str
    description: str
    priority: str = "NORMAL"
    rationale: Optional[str] = None
    related_source_ids: list[str] = field(default_factory=list)
    related_gap_ids: list[str] = field(default_factory=list)
    required_evidence: list[str] = field(default_factory=list)


@dataclass
class AcquisitionTarget:
    target_id: str
    need_id: str
    source_type: str
    name: str
    purpose: str
    discovery_uri: Optional[str] = None
    acquisition_uri: Optional[str] = None
    publisher: Optional[str] = None
    provenance_requirements: list[str] = field(default_factory=list)
    verification_requirements: list[str] = field(default_factory=list)
    mmi_required: bool = True
    independent_corroboration_required: bool = True
    status: str = "PROPOSED"
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def content_hash(self) -> str:
        return stable_hash(
            {
                "need_id": self.need_id,
                "source_type": self.source_type,
                "name": self.name,
                "purpose": self.purpose,
                "discovery_uri": self.discovery_uri,
                "acquisition_uri": self.acquisition_uri,
                "publisher": self.publisher,
                "provenance_requirements": self.provenance_requirements,
                "verification_requirements": self.verification_requirements,
                "mmi_required": self.mmi_required,
                "independent_corroboration_required": (
                    self.independent_corroboration_required
                ),
            }
        )


@dataclass
class AcquisitionPlan:
    plan_id: str
    needs: list[AcquisitionNeed] = field(default_factory=list)
    targets: list[AcquisitionTarget] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SourceAcquisitionPlanner:
    """
    Converts identified knowledge/capability gaps into explicit acquisition
    targets.

    Discovery and acquisition are deliberately separate. The planner does
    not download, execute, install, or ingest external material.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._plan = self._load()

    def _load(self) -> AcquisitionPlan:
        if not self.path.exists():
            return AcquisitionPlan(
                plan_id="barrot-source-acquisition",
            )

        raw = json.loads(self.path.read_text(encoding="utf-8"))

        needs = [
            AcquisitionNeed(**item)
            for item in raw.get("needs", [])
        ]

        targets = [
            AcquisitionTarget(**item)
            for item in raw.get("targets", [])
        ]

        return AcquisitionPlan(
            plan_id=raw.get(
                "plan_id",
                "barrot-source-acquisition",
            ),
            needs=needs,
            targets=targets,
            created_at=raw.get("created_at", utc_now()),
            updated_at=raw.get("updated_at", utc_now()),
        )

    def _save(self) -> None:
        payload = {
            "planner_version": PLANNER_VERSION,
            **self._plan.to_dict(),
        }

        temporary = self.path.with_suffix(
            self.path.suffix + ".tmp"
        )

        temporary.write_text(
            json.dumps(
                payload,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        temporary.replace(self.path)

    def add_need(
        self,
        need: AcquisitionNeed,
    ) -> AcquisitionNeed:
        existing = next(
            (
                item
                for item in self._plan.needs
                if item.need_id == need.need_id
            ),
            None,
        )

        if existing is not None:
            return existing

        self._plan.needs.append(need)
        self._plan.updated_at = utc_now()
        self._save()
        return need

    def add_target(
        self,
        target: AcquisitionTarget,
    ) -> AcquisitionTarget:
        existing = next(
            (
                item
                for item in self._plan.targets
                if item.target_id == target.target_id
            ),
            None,
        )

        if existing is not None:
            if existing.content_hash() == target.content_hash():
                return existing

            raise ValueError(
                f"Acquisition target already exists with different "
                f"content: {target.target_id}"
            )

        if not any(
            need.need_id == target.need_id
            for need in self._plan.needs
        ):
            raise KeyError(
                f"Unknown acquisition need: {target.need_id}"
            )

        self._plan.targets.append(target)
        self._plan.updated_at = utc_now()
        self._save()
        return target

    def get_need(
        self,
        need_id: str,
    ) -> Optional[AcquisitionNeed]:
        return next(
            (
                item
                for item in self._plan.needs
                if item.need_id == need_id
            ),
            None,
        )

    def get_target(
        self,
        target_id: str,
    ) -> Optional[AcquisitionTarget]:
        return next(
            (
                item
                for item in self._plan.targets
                if item.target_id == target_id
            ),
            None,
        )

    def list_needs(self) -> list[AcquisitionNeed]:
        return sorted(
            self._plan.needs,
            key=lambda item: item.need_id,
        )

    def list_targets(
        self,
        *,
        status: Optional[str] = None,
        need_id: Optional[str] = None,
    ) -> list[AcquisitionTarget]:
        targets = self._plan.targets

        if status is not None:
            targets = [
                item
                for item in targets
                if item.status == status
            ]

        if need_id is not None:
            targets = [
                item
                for item in targets
                if item.need_id == need_id
            ]

        return sorted(
            targets,
            key=lambda item: item.target_id,
        )

    def update_target_status(
        self,
        target_id: str,
        status: str,
    ) -> AcquisitionTarget:
        target = self.get_target(target_id)

        if target is None:
            raise KeyError(
                f"Unknown acquisition target: {target_id}"
            )

        target.status = status
        target.updated_at = utc_now()
        self._plan.updated_at = utc_now()
        self._save()
        return target

    def gaps(self) -> list[dict[str, Any]]:
        return [
            {
                "need_id": need.need_id,
                "category": need.category,
                "description": need.description,
                "priority": need.priority,
                "target_count": len(
                    self.list_targets(
                        need_id=need.need_id
                    )
                ),
            }
            for need in self.list_needs()
        ]

    def summary(self) -> dict[str, Any]:
        status_counts: dict[str, int] = {}

        for target in self._plan.targets:
            status_counts[target.status] = (
                status_counts.get(target.status, 0) + 1
            )

        return {
            "planner_version": PLANNER_VERSION,
            "plan_id": self._plan.plan_id,
            "need_count": len(self._plan.needs),
            "target_count": len(self._plan.targets),
            "status_counts": dict(sorted(status_counts.items())),
        }
