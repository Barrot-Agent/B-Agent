from __future__ import annotations

import json
import subprocess
import sys

from scripts.barrot_self_drop_controller_adapter import (
    SelfDropControllerAdapter,
)


def test_adapter_registers_self_drop_probe():
    adapter = SelfDropControllerAdapter()

    assert adapter.name == "self_drop"
    assert adapter.can_handle("SELF_DROP_PROBE")
    assert not adapter.can_handle("RUN_ARBITRARY_COMMAND")


def test_adapter_dispatches_to_bridge():
    adapter = SelfDropControllerAdapter()

    result = adapter.dispatch(
        "controller_integration_probe",
        "SELF_DROP_PROBE",
    )

    assert result["success"] is True
    assert result["returncode"] == 0

    # The bridge stdout is its controller-facing summary.
    # The executed bundle stdout is authoritative in execution_stdout.
    assert "BARROT_AUTONOMOUS_SELF_DROP=TRUE" in result["execution_stdout"]
    assert (
        "BARROT_AUTONOMOUS_SELF_DROP_COMPLETE=TRUE"
        in result["execution_stdout"]
    )

    assert result["evidence_path"]
    assert len(result["bundle_sha256"]) == 64
    assert result["repository_mutation"] is False
    assert result["arbitrary_shell_input"] is False


def test_adapter_rejects_unsupported_action():
    adapter = SelfDropControllerAdapter()

    try:
        adapter.dispatch(
            "rejection_probe",
            "RUN_ARBITRARY_COMMAND",
        )
    except ValueError as exc:
        assert "unsupported" in str(exc)
    else:
        raise AssertionError("unsupported action was not rejected")
