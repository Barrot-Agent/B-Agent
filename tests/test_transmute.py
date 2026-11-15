from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))
import transmute  # noqa: E402


def _create_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    target = tmp_path / "target_module.py"
    variant = tmp_path / "variant_candidate.py"
    log_path = tmp_path / "transmute_log.json"
    target.write_text("VALUE = 'original target'\n", encoding="utf-8")
    variant.write_text("VALUE = 'candidate variant'\n", encoding="utf-8")
    return target, variant, log_path


def test_transmute_is_quarantined_and_preserves_every_input(tmp_path: Path) -> None:
    target, variant, log_path = _create_inputs(tmp_path)
    original_target = target.read_bytes()
    original_variant = variant.read_bytes()

    with pytest.raises(RuntimeError, match="TRANSMUTE QUARANTINED"):
        transmute.transmute(
            target=target,
            variants=[variant],
            tests=[],
            runner="pytest",
            log_path=log_path,
            keep_losers=False,
            interactive=False,
            cwd=tmp_path,
            repeats=1,
        )

    assert target.read_bytes() == original_target
    assert variant.read_bytes() == original_variant
    assert not log_path.exists()


def test_transmute_cli_is_disabled_without_mutating_files(tmp_path: Path) -> None:
    target, variant, log_path = _create_inputs(tmp_path)
    original_target = target.read_bytes()
    original_variant = variant.read_bytes()
    script = REPOSITORY_ROOT / "scripts" / "transmute.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--target",
            str(target),
            "--variants",
            str(variant),
            "--log",
            str(log_path),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "TRANSMUTE QUARANTINED" in result.stderr
    assert target.read_bytes() == original_target
    assert variant.read_bytes() == original_variant
    assert not log_path.exists()
