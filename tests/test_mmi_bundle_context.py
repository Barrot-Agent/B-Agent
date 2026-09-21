import hashlib
import json
from pathlib import Path

from barrot_agent.orchestration.mmi_bundle_context import (
    load_mmi_bundle_context,
)


def test_mmi_context_binds_record_hash(tmp_path):
    record = tmp_path / "MMI_LEARNING_RECORD.json"
    payload = {
        "protocol": "MMI",
        "generated_at": "2026-09-21T00:00:00Z",
        "observations": [{"id": "OBS-001", "stage": "observed"}],
        "unresolved_gaps": [{"id": "GAP-001", "status": "unresolved"}],
        "source_manifest": {"source_count": 3},
    }

    record.write_text(json.dumps(payload))

    expected = hashlib.sha256(record.read_bytes()).hexdigest()
    result = load_mmi_bundle_context(record)

    assert result["available"] is True
    assert result["protocol"] == "MMI"
    assert result["record_sha256"] == expected
    assert result["observations"]
    assert result["unresolved_gaps"]


def test_missing_mmi_record_is_explicit(tmp_path):
    result = load_mmi_bundle_context(
        tmp_path / "missing.json"
    )

    assert result == {
        "available": False,
        "reason": "MMI_LEARNING_RECORD_MISSING",
    }


def test_mmi_context_preserves_unresolved_gaps(tmp_path):
    record = tmp_path / "MMI_LEARNING_RECORD.json"
    payload = {
        "protocol": "MMI",
        "unresolved_gaps": [
            {
                "id": "GAP-TEST",
                "status": "unresolved",
                "statement": "Unknown remains unknown",
            }
        ],
    }

    record.write_text(json.dumps(payload))

    result = load_mmi_bundle_context(record)

    assert result["unresolved_gaps"][0]["id"] == "GAP-TEST"
    assert result["unresolved_gaps"][0]["status"] == "unresolved"
