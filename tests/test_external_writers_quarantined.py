from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ".github/workflows/barrot-hf-admin.yml",
    ".github/workflows/barrot-merge-manual.yml",
    ".github/workflows/barrot-merge.yml",
    ".github/workflows/barrot-restart-space.yml",
    ".github/workflows/barrot-self-upgrade.yml",
    ".github/workflows/capability-9-data-resolver.yml",
    ".github/workflows/deploy-a2a-worker.yml",
    ".github/workflows/force-deploy-space.yml",
    ".github/workflows/rotate-databricks-token.yml",
    ".github/workflows/sync-self-hosted-brain.yml",
    ".github/workflows/barrot-ops.yml",
    ".github/workflows/deploy-databricks.yml",
    ".github/workflows/sync-huggingface.yml",
    ".github/workflows/databricks-bundle.yml",
    ".github/workflows/autonomous_self_deployment.yml",
    ".github/workflows/subscriber_sync.yml",
)


def test_external_mutation_and_public_data_writer_workflows_are_quarantined():
    for relative in WORKFLOWS:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "workflow_dispatch: {}" in text, relative
        assert "permissions: {}" in text, relative
        assert "if: false" in text, relative
        assert "secrets." not in text, relative
        assert "schedule:" not in text, relative
        assert "push:" not in text, relative
        assert "No credentials are read" in text, relative


def test_subscriber_sync_cannot_publish_customer_hashes_without_review():
    workflow = (ROOT / ".github/workflows/subscriber_sync.yml").read_text(encoding="utf-8")
    assert "GUMROAD_ACCESS_TOKEN" not in workflow
    assert "requests.get(" not in workflow
    assert "write_text(" not in workflow
    assert "git push" not in workflow
    assert "permissions: {}" in workflow
    assert "if: false" in workflow


def test_autonomous_self_deployment_no_longer_writes_main():
    workflow = (ROOT / ".github/workflows/autonomous_self_deployment.yml").read_text(encoding="utf-8")
    assert "schedule:" not in workflow
    assert "git push" not in workflow
    assert "permissions: {}" in workflow
    assert "if: false" in workflow
