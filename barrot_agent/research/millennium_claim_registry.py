"""Evidence-graded registry for claims about the seven Clay Millennium Problems.

Claims are research leads until their exact statement and evidence are assessed.
A source/model announcement alone never establishes a solution.
"""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class EvidenceGrade(str, Enum):
    CLAIMED = "CLAIMED"
    PREPRINT_AVAILABLE = "PREPRINT_AVAILABLE"
    COMPUTATIONALLY_CHECKED = "COMPUTATIONALLY_CHECKED"
    FORMALIZED = "FORMALIZED"
    INDEPENDENTLY_REVIEWED = "INDEPENDENTLY_REVIEWED"
    ACCEPTED_RECOGNIZED = "ACCEPTED_RECOGNIZED"
    CHALLENGED = "CHALLENGED"
    REFUTED = "REFUTED"
    UNRESOLVED = "UNRESOLVED"


# Official Clay statement pages. Poincare is the historical solved baseline.
MILLENNIUM_PROBLEMS: dict[str, dict[str, str]] = {
    "birch_swinnerton_dyer": {
        "name": "Birch and Swinnerton-Dyer Conjecture",
        "baseline_status": "OPEN",
        "official_source": "https://www.claymath.org/millennium-problems/birch-and-swinnerton-dyer-conjecture/",
    },
    "hodge_conjecture": {
        "name": "Hodge Conjecture",
        "baseline_status": "OPEN",
        "official_source": "https://www.claymath.org/millennium-problems/hodge-conjecture/",
    },
    "navier_stokes": {
        "name": "Navier–Stokes Equation",
        "baseline_status": "ACTIVE_UNDER_REVIEW",
        "official_source": "https://www.claymath.org/millennium/Navier-Stokes-Equation/",
    },
    "p_vs_np": {
        "name": "P vs NP Problem",
        "baseline_status": "OPEN",
        "official_source": "https://www.claymath.org/millennium-problems/p-vs-np-problem/",
    },
    "riemann_hypothesis": {
        "name": "Riemann Hypothesis",
        "baseline_status": "OPEN",
        "official_source": "https://www.claymath.org/millennium-problems/riemann-hypothesis/",
    },
    "yang_mills_mass_gap": {
        "name": "Yang–Mills Existence and Mass Gap",
        "baseline_status": "OPEN",
        "official_source": "https://www.claymath.org/millennium-problems/yang-mills-and-mass-gap/",
    },
    "poincare_conjecture": {
        "name": "Poincaré Conjecture",
        "baseline_status": "SOLVED_HISTORICAL",
        "official_source": "https://www.claymath.org/millennium-problems/poincare-conjecture/",
    },
}


@dataclass
class ClaimRecord:
    claim_id: str
    problem_id: str
    statement: str
    source_url: str
    source_title: str
    source_publisher: str
    publication_date: str = ""
    source_version_or_commit: str = ""
    assumptions: list[str] = field(default_factory=list)
    theorem_scope: str = ""
    evidence_grade: str = EvidenceGrade.CLAIMED.value
    formalization_scope: str = ""
    independent_review: list[str] = field(default_factory=list)
    counterevidence: list[str] = field(default_factory=list)
    unresolved_obligations: list[str] = field(default_factory=list)
    status_history: list[dict[str, str]] = field(default_factory=list)
    last_reviewed_utc: str = ""
    notes: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.claim_id.strip() or not self.statement.strip():
            raise ValueError("claim_id and statement are required")
        if self.problem_id not in MILLENNIUM_PROBLEMS:
            raise ValueError(f"unknown Millennium problem: {self.problem_id}")
        if not self.source_url.startswith(("https://", "http://")):
            raise ValueError("source_url must be an explicit HTTP(S) URL")
        if not self.source_title.strip() or not self.source_publisher.strip():
            raise ValueError("source title and publisher are required")
        if self.evidence_grade not in {grade.value for grade in EvidenceGrade}:
            raise ValueError(f"invalid evidence grade: {self.evidence_grade}")
        if self.evidence_grade == EvidenceGrade.ACCEPTED_RECOGNIZED.value and not self.independent_review:
            raise ValueError("accepted/recognized status requires recorded independent review")
        if self.problem_id == "poincare_conjecture" and self.evidence_grade == EvidenceGrade.CLAIMED.value:
            # New claims may concern historical proof details, but cannot reset the baseline.
            if not any("historical" in note.lower() for note in self.notes):
                raise ValueError("Poincare is solved historically; new claim must state its scope")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


class ClaimLedger:
    """Atomic JSONL ledger that survives object/process recreation in a shared workspace.

    Cross-run persistence across ephemeral CI workers requires the caller to preserve
    this ledger artifact (for example as a repository commit or workflow artifact).
    This class does not silently commit or publish research records.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def list_claims(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records: list[dict[str, Any]] = []
        for line_no, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid ledger JSON on line {line_no}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"ledger line {line_no} must be an object")
            records.append(record)
        return records

    def record(self, claim: ClaimRecord) -> None:
        item = claim.to_dict()
        records = self.list_claims()
        existing = [r for r in records if r.get("claim_id") == claim.claim_id]
        if existing and existing[-1].get("problem_id") != claim.problem_id:
            raise ValueError("claim_id cannot be reassigned to a different problem")
        now = datetime.now(timezone.utc).isoformat()
        if not item["last_reviewed_utc"]:
            item["last_reviewed_utc"] = now
        item["status_history"] = list(item["status_history"]) + [{
            "grade": item["evidence_grade"],
            "timestamp_utc": now,
            "source_url": item["source_url"],
        }]
        records.append(item)
        rendered = "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in records)
        fd, temporary = tempfile.mkstemp(prefix=self.path.name + ".", dir=str(self.path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(rendered)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
