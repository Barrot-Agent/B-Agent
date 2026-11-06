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
    ".github/workflows/capability-9-data-resolver.yml",
    ".github/workflows/pingpong.yml",
    ".github/workflows/task-allocator.yml",
    ".github/workflows/ask-barrot.yml",
    ".github/workflows/barrot-agent.yml",
    ".github/workflows/signal_ledger.yml",
    ".github/workflows/knowledge-signal-cycle.yml",
    ".github/workflows/test-groq-chain.yml",
    ".github/workflows/webmcp-live-sandbox.yml",
    ".github/workflows/databricks-bundle.yml",
    ".github/workflows/sync-huggingface.yml",
    ".github/workflows/test-semantic-memory.yml",
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


ARTIFACT_ONLY_WORKFLOWS = (
    ".github/workflows/capability-discovery.yml",
    ".github/workflows/capability-10-design.yml",
    ".github/workflows/data-value-triage.yml",
    ".github/workflows/signal-summary.yml",
)


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



def test_capability_workflows_are_manual_exact_sha_and_artifact_only() -> None:
    for relative in ARTIFACT_ONLY_WORKFLOWS:
        workflow = (REPO_ROOT / relative).read_text(encoding="utf-8")
        lowered = workflow.lower()
        assert "workflow_dispatch:" in lowered, relative
        assert "permissions:\n  contents: read" in lowered, relative
        assert "contents: write" not in lowered, relative
        assert "actions: write" not in lowered, relative
        assert "inputs.confirm == 'yes'" in lowered, relative
        assert "inputs.expected_main_sha" in lowered, relative
        assert "persist-credentials: false" in lowered, relative
        assert "git ls-remote origin refs/heads/main" in lowered, relative
        assert "git push" not in lowered, relative
        assert "git commit" not in lowered, relative
        assert "actions/upload-artifact@v7" in lowered, relative
        assert "retention-days: 7" in lowered, relative
        assert "public/authorized" in lowered, relative
        assert "unverified" in lowered, relative


def test_contradiction_resolver_preserves_conflicts_without_llm_adjudication(
    tmp_path: Path,
) -> None:
    records = [
        {
            "id": "xrp_spot_midpoint",
            "value": "1.20658",
            "source_id": "kraken",
            "source_url": "https://example.invalid/kraken",
            "source_independence_group": "kraken_spot",
            "evidence_receipt_id": "receipt-kraken",
            "source_event_time_utc": "2026-11-06T00:00:00Z",
        },
        {
            "id": "xrp_spot_midpoint",
            "value": "1.20710",
            "source_id": "coinbase",
            "source_url": "https://example.invalid/coinbase",
            "source_independence_group": "coinbase_spot",
            "evidence_receipt_id": "receipt-coinbase",
            "source_event_time_utc": "2026-11-06T00:00:02Z",
        },
    ]
    env = os.environ.copy()
    env["TEST_DATA"] = json.dumps(records)
    env.pop("GROQ_API_KEY", None)
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "data_contradiction_resolver.py")],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    output = next(tmp_path.glob("contradiction_review_*.json"))
    report = json.loads(output.read_text(encoding="utf-8"))
    conflict = report["conflicts"][0]
    assert report["conflict_count"] == 1
    assert conflict["resolution_status"] == "UNRESOLVED_PRIMARY_EVIDENCE_REQUIRED"
    assert conflict["observations"] == records
    assert conflict["minority_objections"] == records
    assert conflict["winner"] is None
    assert conflict["adjudication"] is None
    assert report["model_eligible"] is False
    assert report["forecast_status"] == "NOT_ISSUED"


def test_contradiction_resolver_reports_provenance_gaps_without_dropping_records(
    tmp_path: Path,
) -> None:
    records = [
        {"id": "xrp_flow", "value": 10, "source_id": "source-a"},
        {"value": 12, "source_id": "source-b"},
    ]
    env = os.environ.copy()
    env["TEST_DATA"] = json.dumps(records)
    env.pop("GROQ_API_KEY", None)
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "data_contradiction_resolver.py")],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(next(tmp_path.glob("contradiction_review_*.json")).read_text(encoding="utf-8"))
    assert report["source_record_count"] == 2
    assert report["provenance_gap_count"] == 2
    assert report["unresolved_record_count"] == 1
    assert report["unresolved_records"][0]["record"] == records[1]
    assert report["provenance_gaps"][0]["record"] == records[0]
    assert report["model_eligible"] is False
