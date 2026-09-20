import os

os.environ.setdefault("REPO", "Barrot-Agent/B-Agent")

from scripts.barrot_agent import ScriptBrain


def test_controller_registers_and_dispatches_self_drop():
    brain = ScriptBrain()

    assert "self_drop" in brain.tool_funcs
    assert callable(brain.tool_funcs["self_drop"])

    result = brain.tool_funcs["self_drop"]({
        "task_id": "controller_integration_test",
        "action": "SELF_DROP_PROBE",
    })

    assert result["success"] is True
    assert result["returncode"] == 0
    assert result["repository_mutation"] is False
    assert result["arbitrary_shell_input"] is False
    assert result["bundle_sha256"]
    assert result["evidence_path"]
