import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

QUARANTINED_WORKFLOWS = (
    ".github/workflows/scheduler-tick.yml",
    ".github/workflows/subscriber_sync.yml",
    ".github/workflows/merge-queue.yml",
    ".github/workflows/dump-brain-corpus.yml",
    ".github/workflows/daily-digest.yml",
    ".github/workflows/self-schedule.yml",
    ".github/workflows/auto-resolve-issues.yml",
    ".github/workflows/barrot-autonomous-resolver.yml",
    ".github/workflows/check-signal-accuracy.yml",
    ".github/workflows/Barrot.Cognitive.PingPong.Engine.yml",
    ".github/workflows/autonomous_self_deployment.yml",
    ".github/workflows/subagent-spawn.yml",
)


def test_high_risk_automation_workflows_are_quarantined() -> None:
    forbidden = (
        "schedule:",
        "workflow_run:",
        "push:",
        "secrets.",
        "uses:",
        "git push",
        "git commit",
        "gh issue create",
        "gh issue edit",
        "gh pr merge",
        "contents: write",
        "actions: write",
        "issues: write",
        "pull-requests: write",
    )
    for relative in QUARANTINED_WORKFLOWS:
        workflow = (REPO_ROOT / relative).read_text(encoding="utf-8")
        lowered = workflow.lower()
        assert "workflow_dispatch:" in lowered, relative
        assert "permissions: {}" in lowered, relative
        assert (
            "if: false" in lowered or ("if: $" + "{{ false }}") in lowered
        ), relative
        for token in forbidden:
            assert token not in lowered, f"{relative} still contains {token!r}"


def test_cross_analysis_remains_available_but_is_read_only() -> None:
    workflow = (
        REPO_ROOT / ".github" / "workflows" / "cross-analysis.yml"
    ).read_text(encoding="utf-8")
    lowered = workflow.lower()

    assert "contents: read" in lowered
    assert "persist-credentials: false" in lowered
    upload_ref = re.search(r"uses:\s*actions/upload-artifact@v(\d+)", lowered)
    assert upload_ref and int(upload_ref.group(1)) >= 7
    assert "retention-days: 30" in lowered
    assert "if-no-files-found: error" in lowered
    assert "conclusion == 'success'" in lowered

    for token in (
        "contents: write",
        "git add",
        "git commit",
        "git push",
        "persist-credentials: true",
        "secrets.",
    ):
        assert token not in lowered, token


def test_public_brain_corpus_exporter_is_inert() -> None:
    script = (
        REPO_ROOT / "scripts" / "dump_brain_corpus.py"
    ).read_text(encoding="utf-8")

    assert "DISABLED: public brain-corpus export is not authorized." in script
    assert "def main() -> int:" in script
    assert "return 2" in script
    assert "requests.post(" not in script
    assert "os.environ[" not in script
