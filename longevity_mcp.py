"""Read-only MCP facade for the longevity research modules.

The facade deliberately keeps ingestion in memory.  Callers receive
de-identified, provenance-rich envelopes and must explicitly approve any
future persistence or protocol-changing operation outside this service.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

from data.registry import (
    load_biomarker_tracking,
    load_longevity_unified,
    load_reprogramming_protocols,
)
from longevity_micro_ingestion import LongevityMicroIngestion
from trial_tracker import DiscoveryExtractor, EfficacyAnalyzer, ParticipantCohort, SafetyMonitor


def _load_ingestion_config() -> Dict[str, Any]:
    """Return the config text without exposing a caller-controlled path."""
    path = Path(__file__).with_name("longevity-ingestion-config.yaml")
    try:
        return {"raw": path.read_text(encoding="utf-8")}
    except FileNotFoundError:
        return {"raw": "", "error": "ingestion configuration unavailable"}


class LongevityMCPServer:
    """In-process, read-only MCP server for longevity research analysis."""

    server_id = "longevity-research"
    read_only = True
    _RESOURCES = {
        "longevity_unified": load_longevity_unified,
        "biomarker_tracking": load_biomarker_tracking,
        "reprogramming_protocols": load_reprogramming_protocols,
        "ingestion_config": _load_ingestion_config,
    }
    _TOOLS = frozenset(
        {
        "search_papers",
        "search_trials",
        "ingest_research",
        "compare_treatment_arms",
        "track_biomarker",
        "detect_signals",
        "generate_mmi_payload",
        }
    )
    _WRITE_TOOLS = {"apply_protocol", "write_dataset", "store_participant"}
    _PII_FIELDS = {"name", "email", "phone", "address", "contact", "dob", "ssn", "ip_address"}
    _BASE_CONFIDENCE = 0.35

    def __init__(
        self,
        *,
        ingestion: Optional[LongevityMicroIngestion] = None,
        source_citations: Optional[Iterable[str]] = None,
    ) -> None:
        self._ingestion = ingestion or LongevityMicroIngestion()
        self._source_citations = list(source_citations or [])

    def list_resources(self) -> List[str]:
        """Return logical resource names; no filesystem paths are exposed."""
        return sorted(self._RESOURCES)

    def read_resource(self, resource: str) -> Dict[str, Any]:
        """Read a canonical dataset through the central registry."""
        loader = self._RESOURCES.get(resource)
        if loader is None:
            raise KeyError(f"Unknown longevity resource: {resource}")
        data = loader()
        return self._envelope(
            data=self._redact(data),
            source_citations=[f"data/{resource}.json"],
            cohort_size=self._cohort_size(data),
        )

    def supported_tools(self) -> List[str]:
        return list(self._TOOLS)

    def call_tool(self, tool_name: str, **kwargs: Any) -> Dict[str, Any]:
        if tool_name not in self._TOOLS and tool_name not in self._WRITE_TOOLS:
            raise ValueError(f"Unknown longevity tool: {tool_name}")
        if tool_name in self._WRITE_TOOLS:
            raise PermissionError("Longevity MCP is read-only; human approval is required.")
        handler = getattr(self, f"_{tool_name}", None)
        if handler is None:
            raise ValueError(f"Tool handler is not implemented: {tool_name}")
        return handler(**kwargs)

    def _search_papers(self, query: str, papers: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
        return self._search_records(query, papers or [], "paper")

    def _search_trials(self, query: str, trials: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
        return self._search_records(query, trials or [], "trial")

    def _search_records(self, query: str, records: Iterable[Mapping[str, Any]], kind: str) -> Dict[str, Any]:
        terms = query.lower().split()
        matches = [
            self._redact(dict(record))
            for record in records
            if all(term in json.dumps(record, default=str).lower() for term in terms)
            and self._consented(record)
        ]
        return self._envelope(data={"kind": kind, "results": matches}, cohort_size=len(matches))

    def _ingest_research(
        self,
        paper_text: str,
        trial_records: Iterable[Mapping[str, Any]] = (),
        methylation_samples: Iterable[Mapping[str, float]] = (),
        biomarker_measurements: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        source_citations: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        safe_trials, dropped = self._filter_records(trial_records)
        payload = self._ingestion.build_unified_payload(
            paper_text,
            safe_trials,
            methylation_samples,
            biomarker_measurements or {},
        )
        return self._envelope(
            data=self._redact(payload),
            source_citations=list(source_citations or self._source_citations),
            cohort_size=len(safe_trials),
            confidence=self._confidence(payload),
            filtered_records=dropped,
        )

    def _generate_mmi_payload(self, **kwargs: Any) -> Dict[str, Any]:
        return self._ingest_research(**kwargs)

    def _compare_treatment_arms(self, trial_records: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
        records, dropped = self._filter_records(trial_records)
        cohort = ParticipantCohort(phase_number=0, total_participants=len(records))
        for row in records:
            baseline = float(row.get("baseline_epigenetic_age", 0))
            followup = float(row.get("followup_epigenetic_age", 0))
            age_reversal = float(row.get("age_reversal", baseline - followup))
            cohort.add_participant_outcome(
                row.get("participant_id", "unknown"),
                str(row.get("treatment_arm", "unassigned")),
                age_reversal,
            )
        return self._envelope(
            data={"by_arm": cohort.compare_treatment_arms()},
            cohort_size=len(records),
            filtered_records=dropped,
        )

    def _track_biomarker(
        self,
        participant_id: str,
        biomarker: str,
        measurements: Iterable[Dict[str, Any]],
        higher_is_better: bool = True,
        consented: bool = False,
    ) -> Dict[str, Any]:
        if not consented:
            raise PermissionError("Biomarker tracking requires explicit participant consent.")
        return self._envelope(
            data=self._ingestion.track_biomarker_progression(
                self._pseudonymize(participant_id), biomarker, measurements,
                higher_is_better=higher_is_better,
            ),
            cohort_size=1,
        )

    def _detect_signals(
        self,
        trial_records: Iterable[Mapping[str, Any]] = (),
        safety_events: Iterable[Mapping[str, Any]] = (),
    ) -> Dict[str, Any]:
        records, dropped = self._filter_records(trial_records)
        cohort = ParticipantCohort(phase_number=0, total_participants=len(records))
        for row in records:
            cohort.add_participant_outcome(
                row.get("participant_id", "unknown"),
                str(row.get("treatment_arm", "unassigned")),
                float(row.get("age_reversal", 0)),
            )
        monitor = SafetyMonitor()
        for event in safety_events:
            if self._consented(event):
                monitor.log_adverse_event(
                    self._pseudonymize(str(event.get("participant_id", "unknown"))),
                    str(event.get("treatment_arm", "unassigned")),
                    str(event.get("severity", "unknown")),
                    str(event.get("description", "redacted")),
                )
        discoveries = DiscoveryExtractor(cohort, monitor).surface_high_impact_discoveries()
        return self._envelope(
            data={"efficacy_probability": EfficacyAnalyzer(cohort).estimate_success_probability(), "discoveries": discoveries},
            cohort_size=len(records),
            filtered_records=dropped,
            safety_warnings=["Signals are research outputs, not clinical guidance."],
        )

    def _filter_records(
        self, records: Iterable[Mapping[str, Any]]
    ) -> tuple[List[Dict[str, Any]], int]:
        rows = list(records)
        safe = [self._redact(dict(row)) for row in rows if self._consented(row)]
        return safe, len(rows) - len(safe)

    @staticmethod
    def _consented(record: Mapping[str, Any]) -> bool:
        return bool(record.get("consented", False))

    @staticmethod
    def _pseudonymize(value: str) -> str:
        return "participant-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:32]

    def _redact(self, value: Any) -> Any:
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                if key.lower() in self._PII_FIELDS:
                    continue
                if key == "participant_id":
                    result[key] = self._pseudonymize(str(item))
                else:
                    result[key] = self._redact(item)
            return result
        if isinstance(value, list):
            return [self._redact(item) for item in value]
        return value

    @staticmethod
    def _cohort_size(data: Any) -> int:
        if isinstance(data, dict):
            for key in ("participants", "trial_outcomes", "measurements"):
                if isinstance(data.get(key), list):
                    return len(data[key])
        return 0

    @staticmethod
    def _confidence(payload: Mapping[str, Any]) -> float:
        mechanisms = len(payload.get("aging_mechanisms", []))
        outcomes = len(payload.get("trial_outcomes", []))
        # Conservative heuristic: mechanisms provide stronger evidence than rows.
        return round(min(1.0, LongevityMCPServer._BASE_CONFIDENCE + mechanisms * 0.1 + outcomes * 0.05), 2)

    def _envelope(
        self,
        *,
        data: Any,
        source_citations: Optional[Iterable[str]] = None,
        confidence: float = _BASE_CONFIDENCE,
        cohort_size: int = 0,
        filtered_records: int = 0,
        safety_warnings: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        return {
            "data": data,
            "metadata": {
                "source_citations": list(source_citations or self._source_citations),
                "confidence": confidence,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cohort_size": cohort_size,
                "filtered_records": filtered_records,
                "safety_warnings": list(safety_warnings or []),
                "read_only": True,
            },
        }


def create_longevity_server(**kwargs: Any) -> LongevityMCPServer:
    """Factory used by MCP hosts and tests."""
    return LongevityMCPServer(**kwargs)
