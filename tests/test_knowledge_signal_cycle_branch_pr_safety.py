from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/knowledge-signal-cycle.yml").read_text(encoding="utf-8")
CI_WORKFLOW = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
CYCLE = WORKFLOW.split("  cycle:\n", 1)[1].split("\n  publish:\n", 1)[0]
PUBLISH = WORKFLOW.split("\n  publish:\n", 1)[1]


def test_knowledge_cycle_is_manual_only_and_serialized():
    assert "workflow_dispatch:" in WORKFLOW
    assert "schedule:" not in WORKFLOW
    assert "concurrency:" in WORKFLOW
    assert "cancel-in-progress: false" in WORKFLOW


def test_workflow_defaults_to_no_token_permissions():
    assert "permissions: {}" in WORKFLOW


def test_untrusted_ingestion_and_model_steps_have_read_only_permissions():
    assert "permissions:\n      contents: read" in CYCLE
    assert "contents: write" not in CYCLE
    assert "pull-requests: write" not in CYCLE
    assert "persist-credentials: false" in CYCLE
    assert "persist-credentials: true" not in CYCLE
    assert "GH_TOKEN:" not in CYCLE


def test_write_permissions_are_isolated_to_the_publish_job():
    assert "needs: cycle" in PUBLISH
    assert "permissions:\n      contents: write\n      pull-requests: write" in PUBLISH
    assert "persist-credentials: false" in PUBLISH
    assert "actions/download-artifact@v4" in PUBLISH
    assert "GH_TOKEN: ${{ github.token }}" in PUBLISH
    assert "gh auth setup-git" in PUBLISH
    assert "python3 scripts/" not in PUBLISH
    assert "pip install" not in PUBLISH
    assert "GROQ_API_KEY" not in PUBLISH


def test_publish_job_uses_exact_dispatch_commit_and_unique_review_branch():
    assert "ref: ${{ github.sha }}" in PUBLISH
    assert 'BRANCH="barrot/knowledge-cycle-${GITHUB_RUN_ID}"' in PUBLISH
    assert 'git checkout -b "$BRANCH"' in PUBLISH
    assert 'git push --set-upstream origin "$BRANCH"' in PUBLISH
    lowered = PUBLISH.lower()
    assert "git push origin main" not in lowered
    assert "git push --force" not in lowered
    assert "git push -f" not in lowered
    assert "git pull --no-rebase --no-edit origin main" not in lowered
    assert "gh pr create --draft --base main --head \"$BRANCH\"" in PUBLISH
    assert "gh pr merge" not in PUBLISH


def test_cycle_artifact_transfers_only_expected_generated_outputs():
    for path in (
        "ping-pongings/knowledge-base/log.jsonl",
        "ping-pongings/knowledge-base/config.json",
        "web/latest_signal.json",
        "web/signal_history.jsonl",
    ):
        assert path in CYCLE
    assert "actions/upload-artifact@v4" in CYCLE
    assert "retention-days: 30" in CYCLE
    assert "knowledge-cycle-${{ github.run_id }}" in CYCLE
    assert "knowledge-cycle-${{ github.run_id }}" in PUBLISH


def test_knowledge_cycle_runs_safety_checks_before_upload():
    assert "python -m compileall -q scripts" in CYCLE
    assert "python -m pytest --noconftest -o addopts=" in CYCLE
    assert CYCLE.index("python -m pytest") < CYCLE.index("actions/upload-artifact@v4")


def test_knowledge_cycle_safety_tests_are_registered_in_core_ci():
    assert "tests/test_knowledge_signal_cycle_branch_pr_safety.py" in CI_WORKFLOW
