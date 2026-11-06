import json
import os
import re
import subprocess
import sys
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
    ".github/workflows/subagent-matrix.yml",
    ".github/workflows/capability-1-market-analysis.yml",
    ".github/workflows/task-allocator.yml",
    ".github/workflows/ask-barrot.yml",
    ".github/workflows/barrot-agent.yml",
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



def test_coinbase_paper_trader_is_manual_exact_sha_and_artifact_only() -> None:
    workflow = (
        REPO_ROOT / ".github" / "workflows" / "coinbase-paper-trader.yml"
    ).read_text(encoding="utf-8")
    lowered = workflow.lower()

    assert "workflow_dispatch:" in lowered
    assert "schedule:" not in lowered
    assert "push:" not in lowered
    assert "workflow_run:" not in lowered
    assert "contents: read" in lowered
    assert "contents: write" not in lowered
    assert "inputs.confirm == 'yes'" in lowered
    assert "inputs.expected_main_sha" in lowered
    assert "expected_main_sha" in lowered
    assert "git fetch --no-tags --depth=1 origin main" in lowered
    assert "current_main" in lowered and "checked_out" in lowered
    assert "git push" not in lowered
    assert "git commit" not in lowered
    assert "actions/upload-artifact@" in lowered
    assert "retention-days: 7" in lowered



def test_legacy_market_analysis_is_permanently_retired_even_with_opt_in(
    tmp_path: Path,
) -> None:
    script = REPO_ROOT / "scripts" / "market_analysis_engine.py"
    env = os.environ.copy()
    env["BARROT_ENABLE_LEGACY_MARKET_ANALYSIS"] = "YES"
    env.pop("DATABRICKS_HOST", None)
    env.pop("DATABRICKS_TOKEN", None)
    env.pop("DATABRICKS_WAREHOUSE_ID", None)
    env.pop("GROQ_API_KEY", None)

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    status = json.loads(result.stdout)
    assert status["status"] == "NOT_ISSUED"
    assert status["forecast_issued"] is False
    assert status["reason_code"] == "LEGACY_SIGNAL_HISTORY_ANALYSIS_RETIRED"
    assert status["trade_recommendations"] == []
    assert not list(tmp_path.glob("market_analysis_*.json"))
