from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ".github/workflows/cross-analysis.yml",
    ".github/workflows/dump-brain-corpus.yml",
    ".github/workflows/kaggle-competitions.yml",
    ".github/workflows/merge-queue.yml",
    ".github/workflows/scheduler-tick.yml",
    ".github/workflows/task-allocator.yml",
    ".github/workflows/Barrot.Cognitive.PingPong.Engine.yml",
    ".github/workflows/autonomous_self_deployment.yml",
    ".github/workflows/barrot-hf-admin.yml",
    ".github/workflows/barrot-merge-manual.yml",
    ".github/workflows/barrot-merge.yml",
    ".github/workflows/barrot-ops.yml",
    ".github/workflows/barrot-restart-space.yml",
    ".github/workflows/barrot-self-upgrade.yml",
    ".github/workflows/capability-9-data-resolver.yml",
    ".github/workflows/databricks-bundle.yml",
    ".github/workflows/deploy-a2a-worker.yml",
    ".github/workflows/deploy-databricks.yml",
    ".github/workflows/force-deploy-space.yml",
    ".github/workflows/gumroad-metrics.yml",
    ".github/workflows/riemann-harvest.yml",
    ".github/workflows/rotate-databricks-token.yml",
    ".github/workflows/sync-huggingface.yml",
    ".github/workflows/sync-self-hosted-brain.yml",
    ".github/workflows/webmcp-monetization-enrich.yml",
)


def test_security_containment_workflows_are_valid_yaml():
    for relative_path in WORKFLOWS:
        parsed = yaml.safe_load((ROOT / relative_path).read_text(encoding="utf-8"))
        assert isinstance(parsed, dict), relative_path
        assert isinstance(parsed.get("jobs"), dict), relative_path
