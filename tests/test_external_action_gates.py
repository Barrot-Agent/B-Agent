import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def _read(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def test_destructive_or_secret_input_workflows_are_disabled() -> None:
    disabled = (
        "force-deploy-space.yml",
        "barrot-hf-admin.yml",
        "rotate-databricks-token.yml",
        "gumroad-metrics.yml",
        "barrot-merge-manual.yml",
        "task-allocator.yml",
        "ask-barrot.yml",
        "write-lyrics.yml",
        "pingpong.yml",
        "make-track.yml",
        "audio-ingest.yml",
        "barrot-speak.yml",
        "free-image-gen.yml",
        "knowledge-signal-cycle-btc.yml",
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
        assert "gh secret list" not in content


def test_databricks_pat_is_not_a_workflow_dispatch_input() -> None:
    content = _read("rotate-databricks-token.yml")
    assert "new_token" not in content
    assert "DATABRICKS_TOKEN" not in content
    assert "gh workflow run" not in content


def test_model_upload_requires_approval_and_validated_destination() -> None:
    content = _read("barrot-merge.yml")
    assert "confirm_external_change" in content
    assert "default: NO" in content
    assert "inputs.confirm_external_change == 'YES'" in content
    assert "MODEL_NAME: ${{ inputs.model_name }}" in content
    assert '[[ ! "$MODEL_NAME" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ ]]' in content
    assert "${{ github.event.inputs.model_name }}" not in content
    assert "--trust-remote-code" not in content


def test_pr_generating_automation_is_quarantined_until_integration_dedup_is_verified() -> None:
    for name in ("barrot-agent.yml", "barrot-self-upgrade.yml"):
        content = _read(name)
        assert "workflow_dispatch: {}" in content, name
        assert "permissions: {}" in content, name
        assert "if: ${{ false }}" in content, name
        assert "issues:" not in content, name
        assert "schedule:" not in content, name
        assert "push:" not in content, name
        assert "contents: write" not in content, name
        assert "pull-requests: write" not in content, name
        assert "gh pr create" not in content, name


def test_factory_restart_requires_explicit_approval() -> None:
    content = _read("barrot-restart-space.yml")
    assert "confirm_external_change" in content
    assert "default: NO" in content
    assert "inputs.confirm_external_change == 'YES'" in content
    assert "restart?factory=true" in content


def test_self_hosted_brain_fails_closed_without_secret_and_private_space() -> None:
    start_script = (ROOT / "self_hosted_brain" / "start.sh").read_text(encoding="utf-8")
    workflow = _read("sync-self-hosted-brain.yml")
    assert 'if [[ -z "${BRAIN_SHARED_SECRET:-}" ]]' in start_script
    assert '--api-key "$BRAIN_SHARED_SECRET"' in start_script
    assert "changeme" not in start_script
    assert 'if not secret.strip()' in workflow
    assert 'if not bool(getattr(space_info, "private", False))' in workflow
    assert workflow.index('api.add_space_secret') < workflow.index('api.upload_folder')


def test_barrot_ops_requires_explicit_approval_and_exact_current_main_sha() -> None:
    content = _read("barrot-ops.yml")
    assert "confirm_external_change" in content
    assert "default: NO" in content
    assert "expected_source_sha" in content
    assert "inputs.confirm_external_change == 'YES' && github.ref == 'refs/heads/main'" in content
    assert "EXPECTED_SOURCE_SHA" in content
    assert "git rev-parse FETCH_HEAD" in content
    assert "persist-credentials: false" in content
    assert "contents: read" in content
    assert "contents: write" not in content
    assert "kaggle datasets download" in content
    assert "kaggle competitions submit" not in content


def test_existing_safe_external_deploys_keep_per_run_confirmation() -> None:
    for name in ("deploy-databricks.yml", "barrot-ops.yml"):
        content = _read(name)
        assert "confirm_external_change" in content
        assert "default: NO" in content
        assert "inputs.confirm_external_change == 'YES'" in content


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
        assert "upload-artifact@v7" in content, name
        assert "git push" not in content, name
        assert "contents: write" not in content, name


def test_webmcp_live_sandbox_is_quarantined_until_per_tool_allowlisting() -> None:
    content = _read("webmcp-live-sandbox.yml")
    assert "workflow_dispatch: {}" in content
    assert "permissions: {}" in content
    assert "if: ${{ false }}" in content
    assert "playwright" not in content.lower()
    assert "registertool" not in content.lower()
    assert "No browser is launched" in content


def test_hover_bike_simulation_uses_read_only_repository_access() -> None:
    content = _read("hover_bike_updates.yml")
    assert "contents: read" in content
    assert "contents: write" not in content
    assert "persist-credentials: false" in content
    assert "git push" not in content
    assert "upload-artifact@v7" in content


def test_pillars_check_uses_read_only_github_installation_lookup() -> None:
    workflow = _read("pillars-check.yml")
    script = (ROOT / "scripts" / "pillars_check.py").read_text(encoding="utf-8")
    assert "contents: read" in workflow
    assert "persist-credentials: false" in workflow
    assert 'requests.get(f"https://api.github.com/app/installations/{inst}"' in script
    assert 'requests.post(f"https://api.github.com/app/installations/{inst}/access_tokens"' not in script


def test_no_active_scheduled_workflow_can_write_or_merge() -> None:
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
        assert "contents: read" in content, name
        assert "contents: write" not in content, name
        assert "persist-credentials: false" in content, name
        assert "upload-artifact@v7" in content, name
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
    names = (
        "webmcp-trend-digest.yml",
        "self-benchmark.yml",
        "financial-data-refresh.yml",
        "research-topics.yml",
        "frontier-digest.yml",
    )
    for name in names:
        content = _read(name)
        assert "confirm_external_research" in content, name
        assert "default: NO" in content, name
        assert "inputs.confirm_external_research == 'YES'" in content, name
        assert "contents: read" in content, name
        assert "contents: write" not in content, name
        assert "persist-credentials: false" in content, name
        assert "upload-artifact@v7" in content, name
        assert "git push" not in content, name


def test_webmcp_monetization_enrichment_consumes_upstream_artifact_read_only() -> None:
    content = _read("webmcp-monetization-enrich.yml")
    trend = _read("webmcp-trend-digest.yml")
    assert 'workflows: ["WebMCP Trend Digest"]' in content
    assert "github.event.workflow_run.conclusion == 'success'" in content
    assert "actions: read" in content
    assert "contents: read" in content
    download_ref = re.search(r"uses:\s*actions/download-artifact@v(\d+)", content)
    assert download_ref and int(download_ref.group(1)) >= 8
    assert "github.event.workflow_run.id" in content
    assert "github.event.workflow_run.run_number" in content
    assert "webmcp-trend-digest-${{ github.run_number }}" in trend
    assert "webmcp-trend-digest-${{ github.event.workflow_run.run_number }}" in content
    assert "contents: write" not in content
    assert "git push" not in content
    assert "schedule:" not in content

def test_external_side_effects_are_bound_to_exact_approved_main_commit() -> None:
    names = (
        "barrot-merge.yml",
        "deploy-databricks.yml",
        "kaggle-competitions.yml",
        "barrot-restart-space.yml",
    )
    for name in names:
        content = _read(name)
        assert "expected_source_sha" in content, name
        assert "github.ref == 'refs/heads/main'" in content, name
        assert "EXPECTED_SOURCE_SHA" in content, name
        assert "git rev-parse HEAD" in content, name
        assert "ref: main" in content, name
        assert "persist-credentials: false" in content, name

    approval = _read("barrot-approve-pr.yml")
    assert "github.ref == 'refs/heads/main'" in approval

def test_dependency_audit_covers_all_declared_manifests_and_runtime_imports() -> None:
    workflow = _read("dependency-audit.yml")
    for manifest in (
        "requirements.txt",
        "requirements-dev.txt",
        "requirements.tx",
        "pyproject.toml",
        "hf_space/requirements.txt",
        "legacy/requirements_legacy.txt",
    ):
        assert f'"{manifest}"' in workflow
    assert "pip-audit -r requirements.txt --strict" in workflow
    assert "pip-audit -r requirements-dev.txt --strict" in workflow
    assert "ROOT_RUNTIME: ${{ steps.root_runtime.outcome }}" in workflow
    assert "DEV: ${{ steps.dev.outcome }}" in workflow
    assert "root_runtime=%s dev=%s" in workflow
    assert '"$ROOT_RUNTIME" != "success"' in workflow
    assert '"$DEV" != "success"' in workflow
    assert "pip-audit -r requirements.tx --strict" in workflow
    assert "tomllib.loads" in workflow
    assert 'pip-audit -r "$RUNNER_TEMP/pyproject-requirements.txt" --strict' in workflow
    assert 'target.write_text("\\n".join(dependencies) + "\\n", encoding="utf-8")' in workflow
    assert "pyproject=%s" in workflow
    assert "PYPROJECT: ${{ steps.pyproject.outcome }}" in workflow
    assert '"$PYPROJECT" != "success"' in workflow
    assert "--ignore-vuln PYSEC-2024-232" not in workflow
    active_ci = _read("ci.yml")
    assert "--ignore-vuln PYSEC-2024-232" not in active_ci
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "temporarily ignored in CI" not in security
    assert "archived backup" in security

    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    for dependency in ("numpy", "PyJWT", "cryptography", "websockets"):
        assert dependency in requirements
        assert dependency in pyproject


 
def test_shared_workflows_use_supported_checkout_and_artifact_action_majors() -> None:
    checkout_workflows = (
        "barrot-bundle-operational-smoke.yml",
        "barrot-controlled-feature-validation.yml",
        "ci.yml",
        "dependency-audit.yml",
        "formal-verification-benchmarks.yml",
    )
    for name in checkout_workflows:
        content = _read(name)
        match = re.search(r"uses:\s*actions/checkout@v(\d+)", content)
        assert match and int(match.group(1)) >= 7, name

    upload_workflows = (
        "barrot-controlled-feature-validation.yml",
        "cross-analysis.yml",
        "formal-verification-benchmarks.yml",
        "signal-summary.yml",
    )
    for name in upload_workflows:
        content = _read(name)
        match = re.search(r"uses:\s*actions/upload-artifact@v(\d+)", content)
        assert match and int(match.group(1)) >= 7, name

    webmcp = _read("webmcp-monetization-enrich.yml")
    match = re.search(r"uses:\s*actions/download-artifact@v(\d+)", webmcp)
    assert match and int(match.group(1)) >= 8




def test_worker_and_self_hosted_brain_deployments_require_manual_exact_sha_and_secret_rotation() -> None:
    for name in ("deploy-a2a-worker.yml", "sync-self-hosted-brain.yml"):
        content = _read(name)
        assert "on:\\n  workflow_dispatch:" in content, name
        assert "push:" not in content, name
        assert "permissions:\\n  contents: read" in content, name
        assert "persist-credentials: false" in content, name
        assert "inputs.confirm == 'YES'" in content, name
        assert "inputs.confirm_secret_rotation == 'YES'" in content, name
        assert "confirm_secret_rotation" in content, name
        assert "expected_main_sha" in content, name
        assert "EXPECTED_MAIN_SHA" in content, name
        assert "github.ref == 'refs/heads/main'" in content, name
        assert "git rev-parse origin/main" in content, name


def test_ibm_bob_audit_remains_quarantined_without_repository_transfer() -> None:
    content = _read("ibm-bob-barrot-audit.yml")
    assert "workflow_dispatch: {}" in content
    assert "permissions: {}" in content
    assert "if: ${{ false }}" in content
    assert "actions/checkout@" not in content
    assert "actions/upload-artifact@" not in content
    assert "secrets." not in content
    assert "No repository content may be transferred" in content
