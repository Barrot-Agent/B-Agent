from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def read_workflow(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def test_agent_manual_dispatch_is_repository_owner_only():
    workflow = read_workflow("barrot-agent.yml")
    assert "github.event_name == 'workflow_dispatch' && github.actor == github.repository_owner" in workflow


def test_scheduled_agent_queue_only_claims_owner_authored_issues():
    workflow = read_workflow("barrot-agent.yml")
    assert "REPO_OWNER: ${{ github.repository_owner }}" in workflow
    assert "--json number,title,body,labels,author" in workflow
    assert "select(.author.login == $owner)" in workflow


def test_issue_label_agent_route_requires_trusted_sender():
    workflow = read_workflow("barrot-agent.yml")
    assert "github.event.sender.login == 'Barrot-Agent' || github.event.sender.login == github.repository_owner" in workflow


def test_controlled_approval_marker_is_disabled_without_protected_human_review():
    workflow = read_workflow("barrot-approve-pr.yml")
    assert "permissions: {}" in workflow
    assert "if: ${{ false }}" in workflow
    assert "APPROVAL_NOT_PERFORMED" in workflow
    assert "pull-requests: write" not in workflow
    assert "github.actor == github.repository_owner" not in workflow
    assert "gh pr merge" not in workflow


def test_auto_pr_validation_has_no_write_permissions():
    workflow = read_workflow("barrot-auto-pr.yml")
    assert "permissions: {}" in workflow
    assert "pull-requests: write" not in workflow


def test_huggingface_publish_workflows_are_inert_pending_protected_environment():
    for name in ("barrot-merge.yml", "barrot-merge-manual.yml"):
        workflow = read_workflow(name)
        assert "workflow_dispatch:" in workflow
        assert "permissions: {}" in workflow
        assert "if: ${{ false }}" in workflow
        assert "secrets." not in workflow
        assert "HF_TOKEN" not in workflow
        assert "api.upload_folder" not in workflow

def test_huggingface_space_restart_is_inert_pending_protected_environment():
    workflow = read_workflow("barrot-restart-space.yml")
    assert "workflow_dispatch:" in workflow
    assert "permissions: {}" in workflow
    assert "if: ${{ false }}" in workflow
    assert "secrets." not in workflow
    assert "HF_TOKEN" not in workflow
    assert "api.restart_space" not in workflow

def test_self_upgrade_is_inert_pending_protected_environment():
    workflow = read_workflow("barrot-self-upgrade.yml")
    assert "workflow_dispatch:" in workflow
    assert "permissions: {}" in workflow
    assert "if: ${{ false }}" in workflow
    assert "secrets." not in workflow
    assert "git push" not in workflow
    assert "scripts/barrot_self_upgrade.py" not in workflow

def test_engineering_pull_requests_are_created_as_drafts():
    script = (ROOT / "scripts" / "barrot_agent.py").read_text(encoding="utf-8")
    start = script.index("def create_pull_request")
    end = script.index("def persist_scientific_discovery", start)
    section = script[start:end]
    assert '"--draft"' in section
    assert '"pr", "merge"' not in section
