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
)


def test_security_containment_workflows_are_valid_yaml():
    for relative_path in WORKFLOWS:
        parsed = yaml.safe_load((ROOT / relative_path).read_text(encoding="utf-8"))
        assert isinstance(parsed, dict), relative_path
        assert isinstance(parsed.get("jobs"), dict), relative_path
