from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"

MISSION_PACKAGE_FLOORS = {
    "barrot_agent/agi/*": 63,
    "barrot_agent/analysis/*": 20,
    "barrot_agent/ingestion/*": 26,
    "barrot_agent/orchestration/*": 69,
    "barrot_agent/evolution/*": 82,
    "barrot_agent/creative/*": 90,
}


def test_full_suite_enforces_package_floors_for_all_three_missions() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    full_suite_start = workflow.index("  full-suite:")
    next_job = workflow.index("  xrp-historical-backfill-replay:", full_suite_start)
    full_suite = workflow[full_suite_start:next_job]

    for package_glob, floor in MISSION_PACKAGE_FLOORS.items():
        command = (
            "python -m coverage report "
            f"--include='{package_glob}' --fail-under={floor}"
        )
        assert command in full_suite, f"missing full-suite coverage gate: {command}"


def test_coverage_floor_commands_are_not_confused_with_core_subset() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    core_start = workflow.index("  tests:")
    full_suite_start = workflow.index("  full-suite:")
    core_job = workflow[core_start:full_suite_start]
    assert "coverage report --include=" not in core_job
    assert re.search(r"grep -E '\\(\^\|/\)test_", workflow)
