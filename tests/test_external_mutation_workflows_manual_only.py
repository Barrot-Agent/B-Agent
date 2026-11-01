from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_merge_queue_is_read_only_and_cannot_merge_or_mutate_prs():
    workflow = (ROOT / ".github" / "workflows" / "merge-queue.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "contents: read" in workflow
    assert "pull-requests: read" in workflow
    assert "contents: write" not in workflow
    assert "pull-requests: write" not in workflow
    for forbidden in ("gh pr merge", "gh pr comment", "gh pr edit", "gh api --method put", "update-branch", "--delete-branch"):
        assert forbidden not in workflow.lower()


def test_cloudflare_worker_deployment_is_disabled_pending_approval():
    workflow = (ROOT / ".github" / "workflows" / "deploy-a2a-worker.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "permissions: {}" in workflow
    for forbidden in ("CLOUDFLARE_API_TOKEN", "secrets.", "cloudflare/wrangler-action", "command: deploy"):
        assert forbidden not in workflow
    assert "DEPLOYMENT_NOT_PERFORMED" in workflow


def test_self_hosted_brain_deployment_is_disabled_pending_approval():
    workflow = (ROOT / ".github" / "workflows" / "sync-self-hosted-brain.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "permissions: {}" in workflow
    for forbidden in ("HF_TOKEN", "secrets.", "api.upload_folder", "api.create_repo", "add_space_secret"):
        assert forbidden not in workflow
    assert "DEPLOYMENT_NOT_PERFORMED" in workflow


def test_disabled_legacy_workflows_handle_safety_branch_pushes_with_read_only_notice_jobs():
    task_allocator = (ROOT / ".github" / "workflows" / "task-allocator.yml").read_text(encoding="utf-8")
    force_deploy = (ROOT / ".github" / "workflows" / "force-deploy-space.yml").read_text(encoding="utf-8")
    for workflow in (task_allocator, force_deploy):
        assert 'push:\n    branches: ["safety/**"]' in workflow
        assert "permissions: {}" in workflow
        assert "secrets." not in workflow
        assert "actions/checkout" not in workflow
        assert "git push" not in workflow.lower()
    assert "TASK_ALLOCATION_NOT_PERFORMED" in task_allocator
    assert "DEPLOYMENT_NOT_PERFORMED" in force_deploy
