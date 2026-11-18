"""Tests for the sandbox fuzzer and the integer-overflow target.

The fuzzer must find the planted bug, the plant must be reproducible, and the
repair must survive both the original crashing inputs and a fresh fuzz run.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FUZZ = ROOT / "sandbox/chrome/fuzz"
VULN_SRC = FUZZ / "target_overflow.c"
FIXED_SRC = FUZZ / "target_overflow_fixed.c"
FUZZER = FUZZ / "mutational_fuzzer.py"

pytestmark = pytest.mark.skipif(shutil.which("gcc") is None, reason="gcc unavailable")


def build(source: Path, out: Path) -> Path:
    result = subprocess.run(
        ["gcc", "-O0", "-g", "-fstack-protector-strong", "-o", str(out), str(source)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return out


@pytest.fixture(scope="module")
def binaries(tmp_path_factory):
    path = tmp_path_factory.mktemp("fuzz")
    return build(VULN_SRC, path / "vuln"), build(FIXED_SRC, path / "fixed")


@pytest.fixture(scope="module")
def crash_dir(tmp_path_factory, binaries):
    """Fuzz the planted bug once; every assertion reuses the corpus."""
    vuln, _ = binaries
    path = tmp_path_factory.mktemp("crashdir") / "crashes"
    result = fuzz(vuln, 500, path)
    assert result.returncode == 0, result.stdout + result.stderr
    return path


def fuzz(target: Path, runs: int, crashes: Path, seed: int = 1337):
    return subprocess.run(
        [
            sys.executable, str(FUZZER),
            "--target", str(target),
            "--runs", str(runs),
            "--seed", str(seed),
            "--crashes", str(crashes),
        ],
        capture_output=True,
        text=True,
    )


def test_fuzzer_finds_the_planted_overflow(crash_dir):
    assert len(list(crash_dir.glob("*.bin"))) >= 1


def test_found_crash_is_reproducible(crash_dir, binaries):
    vuln, _ = binaries
    crash = sorted(crash_dir.glob("*.bin"))[0]
    again = subprocess.run([str(vuln), str(crash)], capture_output=True, text=True)
    assert again.returncode != 0


def test_triage_identifies_a_length_overflow(crash_dir, binaries):
    vuln, _ = binaries
    for crash in sorted(crash_dir.glob("*.bin")):
        data = crash.read_bytes()
        assert data[:4] == b"FUZZ"
        declared = int.from_bytes(data[4:6], "little")
        assert declared > 16, "the crashing input must declare more than the destination"
        rc = subprocess.run([str(vuln), str(crash)], capture_output=True).returncode
        assert rc != 0


def test_repair_survives_the_original_crash_inputs(crash_dir, binaries):
    _, fixed = binaries
    for crash in sorted(crash_dir.glob("*.bin")):
        rc = subprocess.run([str(fixed), str(crash)], capture_output=True).returncode
        assert rc == 0


def test_repair_survives_a_fresh_fuzz_run(tmp_path, binaries):
    _, fixed = binaries
    result = fuzz(fixed, 300, tmp_path / "crashes")
    assert "unique crashes 0" in result.stdout
    assert result.returncode == 1  # no crashes found is a failure for the target


def test_fuzzer_refuses_a_missing_target(tmp_path):
    result = subprocess.run(
        [sys.executable, str(FUZZER), "--target", str(tmp_path / "nope"), "--runs", "1"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "not found" in result.stdout


def test_target_rejects_input_without_magic(tmp_path, binaries):
    _, fixed = binaries
    sample = tmp_path / "sample.bin"
    sample.write_bytes(b"NOPE" + b"\xff\xff" + b"A" * 32)
    rc = subprocess.run([str(fixed), str(sample)], capture_output=True).returncode
    assert rc == 0
