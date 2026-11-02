from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = ROOT / "self_hosted_brain" / "start.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "sync-self-hosted-brain.yml"


def test_self_hosted_brain_refuses_missing_shared_secret_before_download():
    env = os.environ.copy()
    env.pop("BRAIN_SHARED_SECRET", None)
    result = subprocess.run(
        ["bash", str(START)],
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    assert result.returncode != 0
    assert "BRAIN_SHARED_SECRET must be set before starting the brain API" in result.stderr
    assert "Downloading model" not in result.stdout


def test_self_hosted_brain_never_uses_a_known_default_api_key():
    script = START.read_text(encoding="utf-8")
    assert "${BRAIN_SHARED_SECRET:-changeme}" not in script
    assert ': "${BRAIN_SHARED_SECRET:?BRAIN_SHARED_SECRET must be set before starting the brain API}"' in script
    assert '--api-key "$BRAIN_SHARED_SECRET"' in script


def test_self_hosted_brain_deployment_is_disabled_in_security_proposal():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    lowered = workflow.lower()
    assert "permissions: {}" in workflow
    assert "workflow_dispatch:" in workflow
    assert "push:" not in lowered
    assert "api.upload_folder" not in workflow
    assert "secrets.hf_token" not in lowered
    assert "api.add_space_secret" not in workflow
