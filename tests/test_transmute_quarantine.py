from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts import transmute


def test_transmute_fails_closed_without_mutating_any_candidate(tmp_path: Path) -> None:
    target = tmp_path / "target.py"
    variant = tmp_path / "variant.py"
    test_file = tmp_path / "test_target.py"
    log_file = tmp_path / "transmute.json"
    target.write_text("VALUE = 'baseline'\n", encoding="utf-8")
    variant.write_text("VALUE = 'candidate'\n", encoding="utf-8")
    test_file.write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")
    before = {path: path.read_bytes() for path in (target, variant, test_file)}

    with pytest.raises(RuntimeError, match="TRANSMUTE QUARANTINED"):
        transmute.transmute(
            target=target,
            variants=[variant],
            tests=[test_file],
            runner="pytest",
            log_path=log_file,
            keep_losers=True,
            interactive=False,
            cwd=tmp_path,
        )

    assert {path: path.read_bytes() for path in before} == before
    assert not log_file.exists()


def test_transmute_cli_exits_without_touching_the_workspace(tmp_path: Path) -> None:
    target = tmp_path / "target.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")
    before = target.read_bytes()
    script = Path(__file__).resolve().parents[1] / "scripts" / "transmute.py"
    result = subprocess.run(
        [sys.executable, str(script), str(target), "--variant", str(tmp_path / "candidate.py")],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    assert result.returncode == 2
    assert "TRANSMUTE QUARANTINED" in result.stderr
    assert target.read_bytes() == before
