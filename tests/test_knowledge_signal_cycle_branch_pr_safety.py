from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/knowledge-signal-cycle.yml").read_text(encoding="utf-8")
CI_WORKFLOW = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")


def test_knowledge_cycle_is_manual_only_and_serialized():
    assert "workflow_dispatch:" in WORKFLOW
    assert "schedule:" not in WORKFLOW
    assert "concurrency:" in WORKFLOW
    assert "cancel-in-progress: false" in WORKFLOW


def test_knowledge_cycle_has_only_branch_and_pr_write_permissions():
    assert "permissions:\n  contents: write\n  pull-requests: write" in WORKFLOW
    assert "issues: write" not in WORKFLOW
    assert "actions: write" not in WORKFLOW


def test_knowledge_cycle_pushes_unique_run_branch_not_main():
    assert 'BRANCH="barrot/knowledge-cycle-${GITHUB_RUN_ID}"' in WORKFLOW
    assert 'git checkout -b "$BRANCH"' in WORKFLOW
    assert 'git push --set-upstream origin "$BRANCH"' in WORKFLOW
    lowered = WORKFLOW.lower()
    assert "git push origin main" not in lowered
    assert "git push --force" not in lowered
    assert "git push -f" not in lowered
    assert "git pull --no-rebase --no-edit origin main" not in lowered


def test_knowledge_cycle_opens_draft_review_pr_without_merging():
    assert "gh pr create --draft --base main --head \"$BRANCH\"" in WORKFLOW
    assert "No main-branch write or automatic merge" in WORKFLOW
    assert "gh pr merge" not in WORKFLOW


def test_knowledge_cycle_uploads_generated_outputs_for_audit():
    assert "actions/upload-artifact@v4" in WORKFLOW
    assert "knowledge-cycle-${{ github.run_id }}" in WORKFLOW
    for path in (
        "ping-pongings/knowledge-base/log.jsonl",
        "ping-pongings/knowledge-base/config.json",
        "web/latest_signal.json",
        "web/signal_history.jsonl",
    ):
        assert path in WORKFLOW


def test_knowledge_cycle_safety_tests_are_registered_in_core_ci():
    assert "tests/test_knowledge_signal_cycle_branch_pr_safety.py" in CI_WORKFLOW



def test_knowledge_cycle_runs_safety_checks_before_creating_branch():
    assert "python -m compileall -q scripts" in WORKFLOW
    assert "python -m pytest --noconftest -o addopts=" in WORKFLOW
    assert WORKFLOW.index("python -m pytest") < WORKFLOW.index('git checkout -b "$BRANCH"')
