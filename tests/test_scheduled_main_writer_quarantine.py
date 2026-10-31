from pathlib import Path


AUTO_TELEMETRY = Path(".github/workflows/autonomous_self_deployment.yml").read_text(encoding="utf-8")
COGNITIVE = Path(".github/workflows/Barrot.Cognitive.PingPong.Engine.yml").read_text(encoding="utf-8")


def test_autonomous_telemetry_is_artifact_only_and_does_not_claim_operational_health():
    assert "permissions:\n  contents: read" in AUTO_TELEMETRY
    assert "persist-credentials: false" in AUTO_TELEMETRY
    assert "TELEMETRY_ONLY_NOT_OPERATIONAL_VERIFICATION" in AUTO_TELEMETRY
    assert "Deployment verification:** NOT_PERFORMED" in AUTO_TELEMETRY
    assert "upload-artifact@v7" in AUTO_TELEMETRY
    assert "contents: write" not in AUTO_TELEMETRY
    assert "git commit" not in AUTO_TELEMETRY
    assert "git push" not in AUTO_TELEMETRY


def test_cognitive_heartbeat_does_not_write_synthetic_quality_claims_to_main():
    assert "permissions:\n  contents: read" in COGNITIVE
    assert "persist-credentials: false" in COGNITIVE
    assert "push:" not in COGNITIVE
    assert "schedule:" in COGNITIVE
    assert "workflow_dispatch:" in COGNITIVE
    assert "SIMULATED_HEARTBEAT_ONLY" in COGNITIVE
    assert "NOT_EXECUTED" in COGNITIVE
    assert "NOT_MEASURED" in COGNITIVE
    assert "Optimal" not in COGNITIVE
    assert "Signal strength: High" not in COGNITIVE
    assert "contents: write" not in COGNITIVE
    assert "issues: write" not in COGNITIVE
    assert "pull-requests: write" not in COGNITIVE
    assert "git commit" not in COGNITIVE
    assert "git push" not in COGNITIVE
    assert "upload-artifact@v7" in COGNITIVE
