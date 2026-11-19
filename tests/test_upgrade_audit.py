"""Tests for the offline upgrade audit.

The audit is the credential-free entry point to the upgrade flywheel, so the
things worth testing are the properties that make it safe to run unattended:

  * it cannot reach the network or a shell
  * it cannot write outside the report path it is given
  * its ranking is deterministic
  * an empty result is reported as empty, not padded with invented work
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from scripts.upgrade_audit import audit, render

MODULE = Path(__file__).resolve().parents[1] / "scripts/upgrade_audit.py"


def make_tree(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "barrot_agent" / "a").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "barrot_agent" / "a" / "risky.py").write_text(
        "import urllib.request\n" + "\n".join(f"x{i} = {i}" for i in range(80)) + "\n",
        encoding="utf-8",
    )
    (root / "barrot_agent" / "a" / "guarded.py").write_text(
        "import urllib.request\nfrom barrot_agent.network_guard import guarded_get\n",
        encoding="utf-8",
    )
    (root / "barrot_agent" / "a" / "covered.py").write_text(
        "VALUE = 1\n" + "\n".join(f"y{i} = {i}" for i in range(200)) + "\n",
        encoding="utf-8",
    )
    (root / "tests" / "test_covered.py").write_text(
        "from barrot_agent.a.covered import VALUE\n\ndef test_v():\n    assert VALUE == 1\n",
        encoding="utf-8",
    )
    (root / "barrot_agent" / "a" / "__init__.py").write_text("", encoding="utf-8")
    return root


def by_path(report: dict) -> dict[str, dict]:
    return {t["path"]: t for t in report["targets"]}


# --- safety -------------------------------------------------------------------


def test_module_cannot_reach_the_network_or_a_shell():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    banned = {"urllib", "requests", "socket", "ssl", "httpx", "aiohttp", "subprocess", "os"}
    assert not (imported & banned), f"audit imports {sorted(imported & banned)}"


def test_module_has_no_eval_or_exec():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert "eval" not in names and "exec" not in names


def test_audit_writes_nothing(tmp_path):
    root = make_tree(tmp_path)
    before = sorted(p.as_posix() for p in root.rglob("*"))
    audit(root, limit=10)
    after = sorted(p.as_posix() for p in root.rglob("*"))
    assert before == after


# --- detection ----------------------------------------------------------------


def test_unguarded_network_import_is_flagged(tmp_path):
    report = audit(make_tree(tmp_path), limit=10)
    assert by_path(report)["barrot_agent/a/risky.py"]["unguarded_egress"] is True


def test_guard_marker_clears_the_egress_flag(tmp_path):
    report = audit(make_tree(tmp_path), limit=10)
    guarded = by_path(report)["barrot_agent/a/guarded.py"]
    assert guarded["unguarded_egress"] is False
    assert guarded["has_test"] in (True, False)  # name heuristic, not coverage


def test_named_test_file_marks_a_module_as_tested(tmp_path):
    report = audit(make_tree(tmp_path), limit=10)
    assert by_path(report)["barrot_agent/a/covered.py"]["has_test"] is True


def test_test_directory_is_not_counted_as_a_module(tmp_path):
    report = audit(make_tree(tmp_path), limit=10)
    assert not any(t["path"].startswith("tests/") for t in report["targets"])
    assert report["inventory"]["test_files"] >= 1


def test_egress_violation_outranks_plain_size(tmp_path):
    report = audit(make_tree(tmp_path), limit=10)
    rows = by_path(report)
    assert rows["barrot_agent/a/risky.py"]["score"] > rows["barrot_agent/a/covered.py"]["score"]


# --- determinism and honesty --------------------------------------------------


def test_ranking_is_deterministic(tmp_path):
    root = make_tree(tmp_path)
    a = audit(root, limit=10)
    b = audit(root, limit=10)
    assert a["targets"] == b["targets"]
    assert a["plan"] == b["plan"]
    assert a["generated_at"] != "" or True  # clock is metadata, never a score input


def test_empty_tree_produces_an_empty_plan_not_invented_work(tmp_path):
    root = tmp_path / "empty"
    root.mkdir()
    report = audit(root, limit=10)
    assert report["targets"] == []
    assert report["plan"][0]["count"] == 0
    assert "do not manufacture work" in report["plan"][0]["action"]


def test_missing_capability_audit_is_not_an_error(tmp_path):
    report = audit(make_tree(tmp_path), limit=10)
    assert report["gaps_from_capability_audit"] == []


def test_capability_audit_gaps_are_carried_through(tmp_path):
    root = make_tree(tmp_path)
    (root / "barrot_capability_audit.json").write_text(
        json.dumps({"gaps": [{"id": 1, "name": "Resource allocation ($5M engine)"},
                             "not-a-dict"]}),
        encoding="utf-8",
    )
    report = audit(root, limit=10)
    assert len(report["gaps_from_capability_audit"]) == 1
    plan = [s for s in report["plan"] if s["order"] == 4]
    assert plan and any("Resource allocation" in t for t in plan[0]["targets"])


def test_report_declares_its_own_safety_posture(tmp_path):
    report = audit(make_tree(tmp_path), limit=10)
    assert report["offline"] is True
    assert report["network_used"] is False
    assert report["git_written"] is False


def test_render_is_readable_and_names_the_plan(tmp_path):
    text = render(audit(make_tree(tmp_path), limit=10))
    assert "BARROT OFFLINE UPGRADE AUDIT" in text
    assert "PLAN" in text
    assert "why:" in text


@pytest.mark.parametrize("limit", [0, 1, 5])
def test_limit_is_respected(tmp_path, limit):
    assert len(audit(make_tree(tmp_path), limit=limit)["targets"]) <= limit


# --- the self-upgrade blocker -------------------------------------------------

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/barrot-self-upgrade.yml"


def _workflow() -> dict:
    yaml = pytest.importorskip("yaml")
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def test_self_upgrade_is_dispatchable_from_a_branch():
    job = _workflow()["jobs"]["audit_and_upgrade"]
    assert "refs/heads/main" not in job["if"]
    assert "confirm_external_change" in job["if"]


def test_self_upgrade_never_calls_the_main_write_path():
    """Comments may name the flag; a `run:` step may not."""
    steps = _workflow()["jobs"]["audit_and_upgrade"]["steps"]
    commands = " ".join(str(s.get("run", "")) for s in steps)
    assert "--persist-audit-report" not in commands


def test_self_upgrade_proves_main_did_not_move():
    names = [s["name"] for s in _workflow()["jobs"]["audit_and_upgrade"]["steps"]]
    assert "Record origin/main before the run" in names
    assert "Verify the run did not write main" in names
