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


def test_controlled_approval_marker_is_repository_owner_only_and_never_merges():
    workflow = read_workflow("barrot-approve-pr.yml")
    assert "if: ${{ github.actor == github.repository_owner }}" in workflow
    assert "gh pr merge" not in workflow
    assert "MERGE_PERFORMED=FALSE" in workflow


def test_auto_pr_validation_has_no_write_permissions():
    workflow = read_workflow("barrot-auto-pr.yml")
    assert "permissions: {}" in workflow
    assert "pull-requests: write" not in workflow


def test_huggingface_publish_workflows_require_owner_and_explicit_yes():
    for name in ("barrot-merge.yml", "barrot-merge-manual.yml"):
        workflow = read_workflow(name)
        assert "inputs.confirm_external_change == 'YES'" in workflow
        assert "github.actor == github.repository_owner" in workflow


def test_huggingface_space_restart_requires_owner_and_explicit_yes():
    workflow = read_workflow("barrot-restart-space.yml")
    assert "inputs.confirm_external_change == 'YES'" in workflow
    assert "github.actor == github.repository_owner" in workflow


def test_self_upgrade_requires_owner_yes_and_non_main_branch():
    workflow = read_workflow("barrot-self-upgrade.yml")
    assert "inputs.confirm_repository_write == 'YES'" in workflow
    assert "github.actor == github.repository_owner" in workflow
    assert "github.ref != 'refs/heads/main'" in workflow


def test_engineering_pull_requests_are_created_as_drafts():
    script = (ROOT / "scripts" / "barrot_agent.py").read_text(encoding="utf-8")
    start = script.index("def create_pull_request")
    end = script.index("def persist_scientific_discovery", start)
    section = script[start:end]
    assert '"--draft"' in section
    assert '"pr", "merge"' not in section
