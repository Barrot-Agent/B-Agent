from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEPLOYMENT_WORKFLOWS = (
    ROOT / ".github" / "workflows" / "deploy-a2a-worker.yml",
    ROOT / ".github" / "workflows" / "sync-self-hosted-brain.yml",
)


def test_push_triggered_external_deployments_require_manual_main_approval():
    required_guard = (
        "if: github.event_name == 'workflow_dispatch' && "
        "github.ref == 'refs/heads/main' && inputs.confirm == 'YES'"
    )
    for workflow in DEPLOYMENT_WORKFLOWS:
        content = workflow.read_text(encoding="utf-8")
        assert "\n  push:" not in content
        assert "workflow_dispatch:" in content
        assert "expected_main_sha:" in content
        assert required_guard in content
        assert '[[ "$GITHUB_REF" == "refs/heads/main" ]]' in content
        assert '[[ "$(git rev-parse origin/main)" == "$EXPECTED_MAIN_SHA" ]]' in content
        assert "permissions:\n  contents: read" in content
        assert "persist-credentials: false" in content


def test_self_hosted_brain_secret_is_only_mapped_in_confirmed_deploy_step():
    content = DEPLOYMENT_WORKFLOWS[1].read_text(encoding="utf-8")
    deploy_marker = "      - name: Deploy self_hosted_brain/"
    assert deploy_marker in content
    pre_deploy, deploy_tail = content.split(deploy_marker, 1)
    secret_mapping = "BRAIN_SHARED_SECRET: ${{ secrets.BRAIN_SHARED_SECRET }}"
    assert secret_mapping not in pre_deploy
    assert secret_mapping in deploy_tail
    assert content.count(secret_mapping) == 1
    assert "persist-credentials: false" in content
    deploy = deploy_tail
    assert 'secret = os.environ.get("BRAIN_SHARED_SECRET", "")' in deploy
    assert 'if not secret.strip():' in deploy
    assert deploy.index("if not secret.strip():") < deploy.index("api.create_repo")
    assert deploy.index("if not secret.strip():") < deploy.index("api.upload_folder")
    assert deploy.index("api.create_repo") < deploy.index('api.add_space_secret(repo_id, "BRAIN_SHARED_SECRET", secret)')
    assert 'api.create_repo(repo_id, repo_type="space", space_sdk="docker", private=True, exist_ok=True)' in deploy
    assert 'space_info = api.repo_info(repo_id, repo_type="space")' in deploy
    assert 'if not bool(getattr(space_info, "private", False)):' in deploy
    assert deploy.index("api.create_repo") < deploy.index("api.repo_info") < deploy.index("if not bool(getattr(space_info, \"private\", False)):")
    assert deploy.index('api.add_space_secret(repo_id, "BRAIN_SHARED_SECRET", secret)') < deploy.index("api.upload_folder")
    assert content.index("Verify explicit approval and exact main revision") < content.index("Deploy self_hosted_brain/")
