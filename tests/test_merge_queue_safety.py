from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github" / "workflows" / "merge-queue.yml").read_text(encoding="utf-8")
CI = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")


def _input_default(name: str) -> str:
    lines = WORKFLOW.splitlines()
    start = lines.index(f"      {name}:")
    for line in lines[start + 1 :]:
        if line.startswith("      ") and not line.startswith("        "):
            break
        stripped = line.strip()
        if stripped.startswith("default:"):
            return stripped.split(":", 1)[1].strip().strip('"')
    raise AssertionError(f"missing default for {name}")


def test_merge_queue_is_dry_run_and_bounded_by_default():
    assert _input_default("dry_run") == "true"
    assert _input_default("confirm_merge") == "false"
    assert _input_default("max_prs") == "5"


def test_live_mutations_fail_closed_without_explicit_confirmation():
    guard = 'if [ "$DRY_RUN" != "true" ] && [ "$CONFIRM_MERGE" != "true" ]; then'
    assert guard in WORKFLOW
    guard_index = WORKFLOW.index(guard)
    update_index = WORKFLOW.index("UPDATE_OUTPUT=$(gh api")
    merge_index = WORKFLOW.index("MERGE_OUTPUT=$(gh pr merge")
    assert guard_index < update_index
    assert guard_index < merge_index
    assert "CONFIRM_MERGE: ${{ inputs.confirm_merge }}" in WORKFLOW


def test_merge_queue_safety_test_is_registered_in_ci():
    assert "tests/test_merge_queue_safety.py" in CI
