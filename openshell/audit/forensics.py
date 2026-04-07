"""Security forensics — post-incident investigation and anomaly detection."""

from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from openshell.audit.audit_engine import AuditEngine


class ForensicsAnalyzer:
    """Investigate security incidents and identify anomalous behaviour.

    Example::

        engine   = AuditEngine("/audit")
        analyzer = ForensicsAnalyzer(engine)
        report   = analyzer.investigate_incident("INC-001", time_range=3600)
    """

    def __init__(self, audit_engine: AuditEngine) -> None:
        self._engine = audit_engine

    # ------------------------------------------------------------------
    # Incident investigation
    # ------------------------------------------------------------------

    def investigate_incident(
        self,
        incident_id: str,
        time_range: int = 3600,
    ) -> Dict[str, Any]:
        """Collect all audit events around an incident.

        Searches the audit trail for events whose ``details`` contain
        *incident_id*, then widens the window by *time_range* seconds on
        either side to provide context.

        Args:
            incident_id: Arbitrary identifier used to tag the incident.
            time_range:  Seconds before/after the first matching event to include.

        Returns:
            A dict with keys ``incident_id``, ``events``, ``timeline``,
            ``involved_agents``, ``violations``.
        """
        full_trail = self._engine.get_audit_trail()

        # Find seed events that reference incident_id
        seed_events = [
            r for r in full_trail
            if incident_id in json.dumps(r.get("details", {}), default=str)
        ]

        if seed_events:
            pivot_ts = _parse_ts(seed_events[0].get("timestamp", ""))
            start = pivot_ts - timedelta(seconds=time_range)
            end = pivot_ts + timedelta(seconds=time_range)
            window_events = self._engine.get_audit_trail(
                start_time=start, end_time=end
            )
        else:
            window_events = []

        violations = [e for e in window_events if e.get("event_kind") == "violation"]
        involved = list({e.get("agent_id", "unknown") for e in window_events})

        return {
            "incident_id": incident_id,
            "events": window_events,
            "timeline": _build_timeline(window_events),
            "involved_agents": involved,
            "violations": violations,
        }

    def trace_action_chain(self, action_id: str) -> List[Dict[str, Any]]:
        """Return the ordered sequence of events related to *action_id*.

        Looks for records whose ``event_id`` or ``details`` contain
        *action_id*, then follows ``parent_event_id`` links.

        Args:
            action_id: UUID of the root action event.

        Returns:
            Ordered list of related records.
        """
        full_trail = self._engine.get_audit_trail()
        index: Dict[str, Dict[str, Any]] = {
            r["event_id"]: r for r in full_trail if "event_id" in r
        }

        chain: List[Dict[str, Any]] = []
        visited = set()
        current_id: Optional[str] = action_id
        while current_id and current_id not in visited:
            visited.add(current_id)
            record = index.get(current_id)
            if record is None:
                break
            chain.append(record)
            current_id = record.get("details", {}).get("parent_event_id")

        # Also collect events that explicitly reference action_id
        related = [
            r for r in full_trail
            if action_id in json.dumps(r.get("details", {}), default=str)
            and r.get("event_id") not in visited
        ]
        chain.extend(related)
        return sorted(chain, key=lambda r: r.get("timestamp", ""))

    def identify_anomalies(
        self,
        baseline_period: Tuple[datetime, datetime],
        analysis_period: Tuple[datetime, datetime],
    ) -> List[Dict[str, Any]]:
        """Detect anomalous event rates by comparing two time windows.

        Computes per-agent, per-action-type event rates in *baseline_period*
        and flags combinations whose rate in *analysis_period* deviates by
        more than 2 standard deviations (or is entirely new).

        Args:
            baseline_period: (start, end) of the reference window.
            analysis_period: (start, end) of the window to analyse.

        Returns:
            A list of anomaly dicts, each with ``agent_id``, ``action_type``,
            ``baseline_rate``, ``analysis_rate``, ``severity``.
        """
        baseline = self._engine.get_audit_trail(
            start_time=baseline_period[0], end_time=baseline_period[1]
        )
        analysis = self._engine.get_audit_trail(
            start_time=analysis_period[0], end_time=analysis_period[1]
        )

        def rate(events: List[Dict[str, Any]], window: Tuple[datetime, datetime]) -> float:
            duration = max((window[1] - window[0]).total_seconds(), 1)
            return len(events) / duration * 3600  # events per hour

        # Build counts keyed by (agent_id, action_type)
        def bucket(
            events: List[Dict[str, Any]],
        ) -> Dict[Tuple[str, str], int]:
            counts: Dict[Tuple[str, str], int] = defaultdict(int)
            for e in events:
                agent = e.get("agent_id", "unknown")
                atype = e.get("action_type", e.get("violation_type", "unknown"))
                counts[(agent, atype)] += 1
            return dict(counts)

        b_counts = bucket(baseline)
        a_counts = bucket(analysis)

        b_dur = max((baseline_period[1] - baseline_period[0]).total_seconds(), 1)
        a_dur = max((analysis_period[1] - analysis_period[0]).total_seconds(), 1)

        anomalies: List[Dict[str, Any]] = []
        all_keys = set(b_counts) | set(a_counts)
        baseline_rates = [c / b_dur * 3600 for c in b_counts.values()]
        mean_rate = statistics.mean(baseline_rates) if baseline_rates else 0
        std_rate = statistics.stdev(baseline_rates) if len(baseline_rates) > 1 else 0

        # Flag rates exceeding mean + 2σ (95th-percentile threshold) in the
        # analysis window that also represent at least a 1.5× increase vs
        # baseline (guards against false positives on very low baselines).
        _SIGMA_THRESHOLD = 2
        _MINIMUM_RATE_MULTIPLIER = 1.5

        for agent_id, action_type in all_keys:
            b_rate = b_counts.get((agent_id, action_type), 0) / b_dur * 3600
            a_rate = a_counts.get((agent_id, action_type), 0) / a_dur * 3600
            if (a_rate > mean_rate + _SIGMA_THRESHOLD * std_rate
                    and a_rate > b_rate * _MINIMUM_RATE_MULTIPLIER):
                anomalies.append(
                    {
                        "agent_id": agent_id,
                        "action_type": action_type,
                        "baseline_rate": round(b_rate, 4),
                        "analysis_rate": round(a_rate, 4),
                        "severity": "high" if a_rate > b_rate * 3 else "medium",
                    }
                )

        return anomalies

    def generate_forensics_report(self, incident_id: str) -> str:
        """Produce a JSON-serialised forensics report for *incident_id*.

        Args:
            incident_id: The incident identifier to investigate.

        Returns:
            Pretty-printed JSON string.
        """
        investigation = self.investigate_incident(incident_id)
        report: Dict[str, Any] = {
            "report_type": "forensics",
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
            "incident_id": incident_id,
            "summary": {
                "total_events_in_window": len(investigation["events"]),
                "involved_agents": investigation["involved_agents"],
                "violation_count": len(investigation["violations"]),
            },
            "timeline": investigation["timeline"],
            "violations": investigation["violations"],
        }
        return json.dumps(report, indent=2, default=str)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_ts(ts_str: str) -> datetime:
    try:
        dt = datetime.fromisoformat(ts_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return datetime.now(tz=timezone.utc)


def _build_timeline(
    events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    return [
        {
            "timestamp": e.get("timestamp"),
            "agent_id": e.get("agent_id"),
            "event_kind": e.get("event_kind"),
            "type": e.get("action_type", e.get("violation_type", "unknown")),
        }
        for e in sorted(events, key=lambda r: r.get("timestamp", ""))
    ]
