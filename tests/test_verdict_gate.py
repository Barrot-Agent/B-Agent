"""The verdict gate must pass real verdicts and fail structurally incomplete ones."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.verdict_gate import check_text

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "verdict_gate.py"
FIXTURES = ROOT / "tests" / "fixtures" / "verdicts"
VERDICT_DOC = ROOT / "docs" / "research" / "CONSCIOUSNESS-BRIDGE.md"


def test_real_verdict_document_passes_clean():
    assert check_text(VERDICT_DOC.read_text(encoding="utf-8")) == []


def test_cli_exits_zero_on_the_real_document():
    completed = subprocess.run(
        [sys.executable, str(GATE), str(VERDICT_DOC)], capture_output=True, text=True, timeout=30
    )
    assert completed.returncode == 0
    assert "PASS" in completed.stdout


def test_missing_upgrade_condition_is_caught():
    problems = check_text((FIXTURES / "missing_upgrade.md").read_text(encoding="utf-8"))
    assert any("upgrade condition" in problem for problem in problems)


def test_missing_falsifier_is_caught():
    problems = check_text((FIXTURES / "missing_falsifier.md").read_text(encoding="utf-8"))
    assert any("falsifier" in problem for problem in problems)


def test_two_declarations_are_caught():
    problems = check_text((FIXTURES / "two_letters.md").read_text(encoding="utf-8"))
    assert any("multiple verdict declarations" in problem for problem in problems)


def test_self_upgrade_is_caught():
    text = "**C: Unsupported.**\n\nA falsifier exists. This would become C if the quote failed. This does not claim more.\n"
    problems = check_text(text)
    assert any("cannot upgrade to itself" in problem for problem in problems)


def test_cli_exits_one_on_fixtures():
    completed = subprocess.run(
        [sys.executable, str(GATE), str(FIXTURES / "missing_upgrade.md")],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 1
    assert completed.stdout.startswith("FAIL")


def test_every_verdict_document_in_docs_passes_the_gate():
    """Any document that declares a verdict must satisfy the gate."""
    import re

    declaration = re.compile(r"^\s*\*\*[ABCD]:", re.MULTILINE)
    declared = [path for path in (ROOT / "docs").rglob("*.md") if declaration.search(path.read_text(encoding="utf-8", errors="ignore"))]
    assert declared, "expected at least the consciousness verdict"
    for path in declared:
        assert check_text(path.read_text(encoding="utf-8")) == [], path
