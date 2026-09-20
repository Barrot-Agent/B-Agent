from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path("scripts/barrot_self_drop_bridge.py")


def run_bridge(request):
    return subprocess.run(
        [sys.executable, str(SCRIPT), json.dumps(request)],
        text=True,
        capture_output=True,
    )


def test_allowlisted_self_drop():
    result = run_bridge(
        {
            "task_id": "bridge_probe",
            "action": "SELF_DROP_PROBE",
        }
    )

    assert result.returncode == 0
    assert "REQUEST_ACCEPTED=PASS" in result.stdout
    assert "AUTONOMOUS_BUNDLE_GENERATION=PASS" in result.stdout
    assert "TERMUX_EXECUTION=PASS" in result.stdout
    assert "AUTONOMOUS_MARKER=PASS" in result.stdout
    assert "COMPLETION_MARKER=PASS" in result.stdout


def test_arbitrary_action_is_rejected():
    result = run_bridge(
        {
            "task_id": "rejection_probe",
            "action": "RUN_ARBITRARY_COMMAND",
        }
    )

    assert result.returncode != 0
    assert "SELF_DROP_BRIDGE=FAIL" in result.stdout
    assert "not allowlisted" in result.stdout


def test_shell_code_cannot_be_supplied_as_action():
    result = run_bridge(
        {
            "task_id": "shell_injection_probe",
            "action": "SELF_DROP_PROBE",
            "command": "rm -rf /",
            "shell": "echo SHOULD_NOT_RUN",
        }
    )

    assert result.returncode == 0
    assert "SHOULD_NOT_RUN" not in result.stdout
    assert "TERMUX_EXECUTION=PASS" in result.stdout
