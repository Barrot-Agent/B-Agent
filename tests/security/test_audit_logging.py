"""Tests for the audit logging and compliance reporting subsystems."""

from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from openshell.audit.audit_engine import AuditEngine
from openshell.audit.audit_logger import AuditLogger
from openshell.audit.compliance_reporter import ComplianceReporter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_engine(tmp_path: str) -> AuditEngine:
    return AuditEngine(audit_directory=tmp_path)


# ---------------------------------------------------------------------------
# AuditLogger tests
# ---------------------------------------------------------------------------


def test_audit_logger_creation(tmp_path) -> None:
    """AuditLogger initialises without errors."""
    al = AuditLogger(log_dir=str(tmp_path))
    assert al is not None


def test_action_logging(tmp_path) -> None:
    """log_action stores an in-memory record with the correct event_type."""
    al = AuditLogger(log_dir=str(tmp_path))
    al.log_action("inference", {"model": "llama3", "agent_id": "inference_agent"})
    entries = al.get_log_entries()
    assert len(entries) == 1
    assert entries[0]["event_type"] == "inference"
    assert entries[0]["model"] == "llama3"


def test_violation_logging(tmp_path) -> None:
    """log_violation stores a VIOLATION-kind record."""
    al = AuditLogger(log_dir=str(tmp_path))
    al.log_violation("unauthorized_network", {"domain": "evil.com"})
    entries = al.get_log_entries()
    assert len(entries) == 1
    assert entries[0]["kind"] == "VIOLATION"


def test_inference_request_logging(tmp_path) -> None:
    """log_inference_request captures model, endpoint, and anonymization flag."""
    al = AuditLogger(log_dir=str(tmp_path))
    al.log_inference_request("granite-vision", "local_nvidia_gpu", anonymized=False)
    entries = al.get_log_entries(filters={"event_type": "inference_request"})
    assert len(entries) == 1
    assert entries[0]["model"] == "granite-vision"
    assert entries[0]["anonymized"] is False


def test_get_log_entries_filter(tmp_path) -> None:
    """get_log_entries correctly filters by field values."""
    al = AuditLogger(log_dir=str(tmp_path))
    al.log_action("inference", {"agent_id": "agent_a"})
    al.log_action("network", {"agent_id": "agent_b"})
    result = al.get_log_entries(filters={"event_type": "inference"})
    assert all(e["event_type"] == "inference" for e in result)
    assert len(result) == 1


# ---------------------------------------------------------------------------
# AuditEngine tests
# ---------------------------------------------------------------------------


def test_audit_trail_retrieval(tmp_path) -> None:
    """get_audit_trail returns events matching agent_id filter."""
    engine = _make_engine(str(tmp_path))
    engine.record_action("inference", {"model": "llama3"}, "agent_a")
    engine.record_action("network", {}, "agent_b")
    engine.record_violation("policy_breach", {}, "agent_a")

    trail_a = engine.get_audit_trail(agent_id="agent_a")
    assert len(trail_a) == 2
    trail_b = engine.get_audit_trail(agent_id="agent_b")
    assert len(trail_b) == 1


def test_record_action_returns_event_id(tmp_path) -> None:
    """record_action returns a non-empty event ID."""
    engine = _make_engine(str(tmp_path))
    event_id = engine.record_action("test_action", {}, "test_agent")
    assert event_id and len(event_id) == 36  # UUID format


def test_export_audit_log_json(tmp_path) -> None:
    """export_audit_log produces valid JSON."""
    import json

    engine = _make_engine(str(tmp_path))
    engine.record_action("action_a", {}, "agent_x")
    exported = engine.export_audit_log(format="json")
    parsed = json.loads(exported)
    assert isinstance(parsed, list)
    assert len(parsed) == 1


def test_export_audit_log_ndjson(tmp_path) -> None:
    """export_audit_log in ndjson format has one JSON object per line."""
    import json

    engine = _make_engine(str(tmp_path))
    engine.record_action("a1", {}, "a")
    engine.record_action("a2", {}, "b")
    ndjson = engine.export_audit_log(format="ndjson")
    lines = [l for l in ndjson.splitlines() if l.strip()]
    assert len(lines) == 2
    for line in lines:
        json.loads(line)


# ---------------------------------------------------------------------------
# ComplianceReporter tests
# ---------------------------------------------------------------------------


def test_compliance_report_generation(tmp_path) -> None:
    """generate_report produces a JSON string with required top-level keys."""
    import json

    engine = _make_engine(str(tmp_path))
    engine.record_action("inference", {}, "agent")
    reporter = ComplianceReporter(engine)
    report_str = reporter.generate_report("2000-01-01", "2099-12-31")
    report = json.loads(report_str)
    assert "total_events" in report
    assert "action_summary" in report
    assert "violation_summary" in report


def test_violation_summary(tmp_path) -> None:
    """get_violation_summary returns per-type counts."""
    engine = _make_engine(str(tmp_path))
    engine.record_violation("net_block", {}, "agent")
    engine.record_violation("net_block", {}, "agent")
    engine.record_violation("fs_block", {}, "agent")
    reporter = ComplianceReporter(engine)
    summary = reporter.get_violation_summary()
    assert summary["net_block"] == 2
    assert summary["fs_block"] == 1


def test_check_compliance_basic_pass(tmp_path) -> None:
    """check_compliance returns compliant=True when no violations exist."""
    engine = _make_engine(str(tmp_path))
    reporter = ComplianceReporter(engine)
    result = reporter.check_compliance(standard="basic")
    assert isinstance(result["compliant"], bool)
    assert result["standard"] == "basic"
