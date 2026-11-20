from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def _read(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")



def _assert_quarantined(name: str) -> str:
    content = _read(name)
    lowered = content.lower()
    assert "workflow_dispatch:" in lowered, name
    assert "permissions: {}" in lowered, name
    assert ("if: $" + "{{ false }}") in lowered, name
    assert "secrets." not in lowered, name
    assert "uses:" not in lowered, name
    assert "git push" not in lowered, name
    assert "contents: write" not in lowered, name
    return content


def _assert_pinned_action(content: str, action: str, version: int) -> None:
    pattern = rf"uses:\s+{re.escape(action)}@[0-9a-f]{{40}}\s+#\s+v{version}\b"
    assert re.search(pattern, content), action

def test_destructive_or_secret_input_workflows_are_disabled() -> None:
    disabled = (
        "force-deploy-space.yml",
        "barrot-hf-admin.yml",
        "rotate-databricks-token.yml",
        "gumroad-metrics.yml",
        "barrot-merge-manual.yml",
        "barrot-sync.yml",
        "coinbase-paper-trader.yml",
        "deploy-databricks.yml",
    )
    for name in disabled:
        content = _read(name)
        assert "permissions: {}" in content
        assert "if: ${{ false }}" in content
        assert "secrets." not in content
        assert "schedule:" not in content
        assert "git push" not in content
        assert "curl " not in content
        assert "gh secret set" not in content


def test_databricks_pat_is_not_a_workflow_dispatch_input() -> None:
    content = _read("rotate-databricks-token.yml")
    assert "new_token" not in content
    assert "DATABRICKS_TOKEN" not in content
    assert "gh workflow run" not in content


def test_model_upload_workflow_remains_quarantined_until_reviewed_configuration_exists() -> None:
    content = _assert_quarantined("barrot-merge.yml")
    assert "merges/barrot-superior/config.yaml is absent" in content
    assert "No model merge, credential read, repository write, or Hugging Face upload is permitted." in content

def test_self_upgrade_remains_quarantined_until_integration_first_authorization_is_ready() -> None:
    content = _assert_quarantined("barrot-self-upgrade.yml")
    assert "Autonomous branch/PR generation is disabled" in content

def test_factory_restart_requires_explicit_approval() -> None:
    content = _read("barrot-restart-space.yml")
    assert "confirm_external_change" in content
    assert "default: NO" in content
    assert "inputs.confirm_external_change == 'YES'" in content
    assert "restart?factory=true" in content


def test_existing_external_operations_are_gated_or_quarantined() -> None:
    ops = _read("barrot-ops.yml")
    assert "workflow_dispatch:" in ops
    assert "default: NO" in ops
    assert "inputs.confirm_databricks_workspace_create == 'YES'" in ops
    assert "inputs.confirm_kaggle_dataset_download == 'YES'" in ops
    assert "github.ref == 'refs/heads/main'" in ops
    assert "--overwrite" not in ops
    assert "kaggle datasets submit" not in ops
    _assert_quarantined("sync-huggingface.yml")
    _assert_quarantined("deploy-databricks.yml")

def test_controlled_pr_approval_is_not_a_merge_action() -> None:
    content = _read("barrot-approve-pr.yml")
    assert "expected_head_sha" in content
    assert "APPROVAL_REASON" in content
    assert "MERGE_PERFORMED=FALSE" in content
    assert "gh pr merge" not in content


def test_kaggle_submissions_require_per_run_approval_and_exact_allowlist() -> None:
    content = _read("kaggle-competitions.yml")
    script = (ROOT / "scripts" / "kaggle_competitions_automation.py").read_text(encoding="utf-8")
    assert "schedule:" not in content
    assert "confirm_external_submission" in content
    assert "default: NO" in content
    assert "inputs.confirm_external_submission == 'YES'" in content
    assert "competition_allowlist" in content
    assert "KAGGLE_SUBMISSION_ALLOWLIST" in content
    assert "python scripts/kaggle_competitions_automation.py" in content
    assert "python kaggle_competitions_automation.py" not in content
    assert "contents: read" in content
    assert "contents: write" not in content
    assert "SUBMISSION_ALLOWLIST" in script
    assert "if not SUBMISSION_ALLOWLIST" in script
    assert "in SUBMISSION_ALLOWLIST" in script
    assert script.index("if not SUBMISSION_ALLOWLIST") < script.index("api = _build_api()")
    duplicate = (ROOT / "barrot_agent" / "tools" / "kaggle_competitions_automation.py").read_text(encoding="utf-8")
    assert "SUBMISSION_ALLOWLIST" in duplicate
    assert "if not SUBMISSION_ALLOWLIST" in duplicate
    assert duplicate.index("if not SUBMISSION_ALLOWLIST") < duplicate.index("api = _build_api()")


def test_scheduled_research_jobs_write_artifacts_not_main() -> None:
    for name in (
        "riemann-harvest.yml",
        "barrot-transparency-audit.yml",
        "webmcp-monetization-enrich.yml",
    ):
        content = _read(name)
        assert "contents: read" in content, name
        assert "persist-credentials: false" in content, name
        _assert_pinned_action(content, "actions/upload-artifact", 7)
        assert "git push" not in content, name
        assert "contents: write" not in content, name

def test_webmcp_live_sandbox_remains_quarantined_pending_per_tool_authorization() -> None:
    content = _assert_quarantined("webmcp-live-sandbox.yml")
    assert "per-tool allowlist" in content
    assert "No browser is launched" in content

def test_hover_bike_simulation_uses_read_only_repository_access() -> None:
    content = _read("hover_bike_updates.yml")
    assert "contents: read" in content
    assert "contents: write" not in content
    assert "persist-credentials: false" in content
    assert "git push" not in content
    _assert_pinned_action(content, "actions/upload-artifact", 7)

def test_pillars_check_uses_read_only_github_installation_lookup() -> None:
    workflow = _read("pillars-check.yml")
    script = (ROOT / "scripts" / "pillars_check.py").read_text(encoding="utf-8")
    assert "contents: read" in workflow
    assert "persist-credentials: false" in workflow
    assert 'requests.get(f"https://api.github.com/app/installations/{inst}"' in script
    assert 'requests.post(f"https://api.github.com/app/installations/{inst}/access_tokens"' not in script


def test_no_active_scheduled_workflow_can_write_or_merge() -> None:
    import re

    for path in WORKFLOWS.glob("*.yml"):
        content = path.read_text(encoding="utf-8")
        if not re.search(r"^\s{2}schedule:", content, flags=re.MULTILINE):
            continue
        assert not re.search(
            r"^\s+(?:contents|actions|issues|pull-requests):\s*write\b",
            content,
            flags=re.MULTILINE,
        ), path.name
        assert "git push" not in content.lower(), path.name
        assert "gh pr merge" not in content.lower(), path.name


def test_content_and_entity_workflows_require_confirmation_and_preserve_artifacts() -> None:
    for name in ("content-pipeline.yml", "entity-relations.yml"):
        content = _read(name)
        assert "confirm_external_change" in content, name
        assert "default: NO" in content, name
        assert "inputs.confirm_external_change == 'YES'" in content, name
        assert "github.ref == 'refs/heads/main'" in content, name
        assert "contents: read" in content, name
        assert "contents: write" not in content, name
        assert "persist-credentials: false" in content, name
        _assert_pinned_action(content, "actions/upload-artifact", 7)
        assert "git push" not in content, name

def test_controlled_pr_approval_requires_yes_and_never_merges() -> None:
    content = _read("barrot-approve-pr.yml")
    assert "confirm_approval" in content
    assert "default: NO" in content
    assert "inputs.confirm_approval == 'YES'" in content
    assert "expected_head_sha" in content
    assert "APPROVAL_REASON" in content
    assert "Target PR must be open and non-draft." in content
    assert "mergeable_state" in content
    assert 'if [[ "$mergeable_state" != "clean" ]]' in content
    assert "gh pr merge" not in content
    assert "MERGE_PERFORMED=FALSE" in content


def test_barrot_auto_pr_has_no_unnecessary_pull_request_write_permission() -> None:
    content = _read("barrot-auto-pr.yml")
    assert "contents: read" in content
    assert "pull-requests: write" not in content
    assert "gh pr create" not in content
    assert "gh pr merge" not in content


def test_groq_research_pipelines_require_yes_and_upload_artifacts() -> None:
    for name in ("self-benchmark.yml", "knowledge-signal-cycle.yml"):
        _assert_quarantined(name)

    names = (
        "webmcp-trend-digest.yml",
        "financial-data-refresh.yml",
        "research-topics.yml",
        "frontier-digest.yml",
    )
    for name in names:
        content = _read(name)
        assert "confirm_external_research" in content, name
        assert "default: NO" in content, name
        assert "inputs.confirm_external_research == 'YES'" in content, name
        assert "github.ref == 'refs/heads/main'" in content, name
        assert "contents: read" in content, name
        assert "contents: write" not in content, name
        assert "persist-credentials: false" in content, name
        _assert_pinned_action(content, "actions/upload-artifact", 7)
        assert "git push" not in content, name

def test_webmcp_monetization_enrichment_consumes_upstream_artifact_read_only() -> None:
    content = _read("webmcp-monetization-enrich.yml")
    trend = _read("webmcp-trend-digest.yml")
    assert 'workflows: ["WebMCP Trend Digest"]' in content
    assert "github.event.workflow_run.conclusion == 'success'" in content
    assert "actions: read" in content
    assert "contents: read" in content
    _assert_pinned_action(content, "actions/download-artifact", 8)
    _assert_pinned_action(content, "actions/upload-artifact", 7)
    assert "github.event.workflow_run.id" in content
    assert "github.event.workflow_run.run_number" in content
    assert "webmcp-trend-digest-$" + "{{ github.run_number }}" in trend
    assert "webmcp-trend-digest-$" + "{{ github.event.workflow_run.run_number }}" in content
    assert "contents: write" not in content
    assert "git push" not in content
    assert "schedule:" not in content

def test_external_side_effects_are_bound_to_exact_approved_main_commit() -> None:
    for name in ("barrot-merge.yml", "sync-huggingface.yml", "webmcp-live-sandbox.yml"):
        _assert_quarantined(name)

    for name in ("kaggle-competitions.yml", "barrot-restart-space.yml"):
        content = _read(name)
        assert "expected_source_sha" in content, name
        assert "github.ref == 'refs/heads/main'" in content, name
        assert "EXPECTED_SOURCE_SHA" in content, name
        assert "git rev-parse HEAD" in content, name
        assert "ref: main" in content, name
        assert "persist-credentials: false" in content, name

    ops = _read("barrot-ops.yml")
    assert "expected_main_sha" in ops
    assert "EXPECTED_MAIN_SHA" in ops
    assert "ref: ${{ inputs.expected_main_sha }}" in ops
    assert "git rev-parse HEAD" in ops
    assert "git ls-remote origin refs/heads/main" in ops
    assert "dbc-82d64fee-1c2e.cloud.databricks.com" in ops

    approval = _read("barrot-approve-pr.yml")
    assert "github.ref == 'refs/heads/main'" in approval

def test_dependency_audit_covers_all_declared_manifests_and_runtime_imports() -> None:
    workflow = _read("dependency-audit.yml")
    for manifest in (
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-integrations.txt",
        "pyproject.toml",
        "hf_space/requirements.txt",
        "legacy/requirements_legacy.txt",
    ):
        assert manifest in workflow
    for manifest in (
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-integrations.txt",
        "hf_space/requirements.txt",
        "legacy/requirements_legacy.txt",
    ):
        assert f"pip-audit -r {manifest} --strict" in workflow
    assert 'Path("pyproject.toml")' in workflow

    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    for dependency in ("numpy", "PyJWT", "cryptography", "websockets"):
        assert dependency in requirements
        assert dependency in pyproject

def test_a2a_worker_deployment_uploads_only_its_required_authentication_secret() -> None:
    content = _read("deploy-a2a-worker.yml")
    assert "workflow_dispatch:" in content
    assert "push:" not in content
    assert "confirm_secret_rotation" in content
    assert "inputs.confirm == 'YES'" in content
    assert "inputs.confirm_secret_rotation == 'YES'" in content
    assert "expected_main_sha" in content
    assert "EXPECTED_MAIN_SHA" in content
    assert "git rev-parse origin/main" in content
    assert "persist-credentials: false" in content
    assert "github.ref == 'refs/heads/main'" in content
    assert "contents: read" in content
    assert "contents: write" not in content
    assert "GROQ_API_KEY" not in content
    assert "secrets: |\n            BRAIN_SHARED_SECRET\n" in content
    assert "BRAIN_SHARED_SECRET: ${{ secrets.BRAIN_SHARED_SECRET }}" in content
