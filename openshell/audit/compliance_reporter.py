"""Compliance reporter — aggregates audit records into human-readable reports."""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from openshell.audit.audit_engine import AuditEngine


class ComplianceReporter:
    """Generate compliance summaries and exportable reports from audit data.

    Example::

        engine  = AuditEngine("/audit")
        reporter = ComplianceReporter(engine)
        report   = reporter.generate_report("2024-01-01", "2024-12-31")
    """

    _BASIC_REQUIRED_ACTIONS = frozenset(
        {"inference", "network_request", "filesystem_access"}
    )

    def __init__(self, audit_engine: AuditEngine) -> None:
        self._engine = audit_engine

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------

    def generate_report(
        self,
        start_date: str,
        end_date: str,
        format: str = "json",
    ) -> str:
        """Generate a compliance report covering *start_date* to *end_date*.

        Args:
            start_date: ISO date string ``"YYYY-MM-DD"`` (inclusive).
            end_date:   ISO date string ``"YYYY-MM-DD"`` (inclusive).
            format:     ``"json"`` or ``"csv"``.

        Returns:
            A string-serialised report in the requested format.
        """
        start_dt = _parse_date(start_date)
        end_dt = _parse_date(end_date, end_of_day=True)
        trail = self._engine.get_audit_trail(start_time=start_dt, end_time=end_dt)

        report: Dict[str, Any] = {
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
            "period": {"start": start_date, "end": end_date},
            "total_events": len(trail),
            "action_summary": self._summarise_actions(trail),
            "violation_summary": self._summarise_violations(trail),
            "agents": self._summarise_agents(trail),
        }

        if format == "csv":
            return _report_to_csv(trail)
        return json.dumps(report, indent=2, default=str)

    def get_violation_summary(self) -> Dict[str, int]:
        """Return a count of violations grouped by ``violation_type``.

        Returns:
            Dict mapping violation type → count.
        """
        trail = self._engine.get_audit_trail()
        return self._summarise_violations(trail)

    def get_action_summary(self) -> Dict[str, int]:
        """Return a count of actions grouped by ``action_type``.

        Returns:
            Dict mapping action type → count.
        """
        trail = self._engine.get_audit_trail()
        return self._summarise_actions(trail)

    def export_to_csv(self, path: str) -> None:
        """Write the full audit trail to a CSV file at *path*.

        Args:
            path: File path where the CSV will be written.
        """
        trail = self._engine.get_audit_trail()
        csv_str = _report_to_csv(trail)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(csv_str)

    def check_compliance(self, standard: str = "basic") -> Dict[str, Any]:
        """Run a compliance check against *standard*.

        Currently supports ``"basic"`` which verifies that all required action
        types appear in the audit trail.

        Args:
            standard: Compliance standard name.

        Returns:
            Dict with keys ``compliant`` (bool), ``standard``, ``findings`` (list).
        """
        trail = self._engine.get_audit_trail()
        findings: List[str] = []

        if standard == "basic":
            present_actions = {
                r.get("action_type", "") for r in trail if r.get("event_kind") == "action"
            }
            for required in self._BASIC_REQUIRED_ACTIONS:
                if required not in present_actions:
                    findings.append(
                        f"Required action type '{required}' not found in audit trail"
                    )
            violations = [r for r in trail if r.get("event_kind") == "violation"]
            if violations:
                findings.append(
                    f"{len(violations)} policy violation(s) recorded in audit trail"
                )

        return {
            "compliant": len(findings) == 0,
            "standard": standard,
            "findings": findings,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _summarise_actions(
        self, trail: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for rec in trail:
            if rec.get("event_kind") == "action":
                action_type = rec.get("action_type", "unknown")
                counts[action_type] = counts.get(action_type, 0) + 1
        return counts

    def _summarise_violations(
        self, trail: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for rec in trail:
            if rec.get("event_kind") == "violation":
                vtype = rec.get("violation_type", "unknown")
                counts[vtype] = counts.get(vtype, 0) + 1
        return counts

    def _summarise_agents(
        self, trail: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, int]]:
        summary: Dict[str, Dict[str, int]] = {}
        for rec in trail:
            agent = rec.get("agent_id", "unknown")
            entry = summary.setdefault(agent, {"actions": 0, "violations": 0})
            if rec.get("event_kind") == "action":
                entry["actions"] += 1
            elif rec.get("event_kind") == "violation":
                entry["violations"] += 1
        return summary


def _parse_date(
    date_str: str, end_of_day: bool = False
) -> datetime:
    dt = datetime.fromisoformat(date_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if end_of_day:
        dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    return dt


def _report_to_csv(trail: List[Dict[str, Any]]) -> str:
    if not trail:
        return ""
    fieldnames = ["event_id", "event_kind", "agent_id", "action_type",
                  "violation_type", "outcome", "timestamp"]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for rec in trail:
        writer.writerow({f: rec.get(f, "") for f in fieldnames})
    return buf.getvalue()
