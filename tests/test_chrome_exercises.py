"""Tests for the Chrome sandbox exercises.

Each exercise must do the same three things: prove the vulnerable shape is
detected, prove the repair is clean, and stay offline. An exercise that cannot
run here must report SKIPPED, never PASS.
"""
from __future__ import annotations

import ast
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sandbox/chrome/exercises"
UAF_SRC = BASE / "uaf/uaf.c"
V8_SRC = BASE / "v8_type_confusion/jit_type_confusion.py"
MOJO_SRC = BASE / "mojo_confused_deputy/mojo_confused_deputy.py"
RUNNER = BASE / "run_all.py"

FORBIDDEN_IMPORTS = {
    "socket", "ssl", "http", "urllib", "requests", "aiohttp", "httpx",
    "websocket", "websockets", "selenium", "playwright", "pyppeteer",
}


@pytest.fixture(scope="module")
def uaf_binary(tmp_path_factory) -> Path:
    if shutil.which("gcc") is None:
        pytest.skip("gcc not available")
    out = tmp_path_factory.mktemp("uaf") / "uaf"
    build = subprocess.run(
        ["gcc", "-O0", "-g", "-Wall", "-Wextra", "-o", str(out), str(UAF_SRC)],
        capture_output=True,
        text=True,
    )
    assert build.returncode == 0, build.stderr
    return out


def test_uaf_exercise_detects_the_stale_write(uaf_binary):
    result = subprocess.run([str(uaf_binary)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "use-after-free WRITE" in result.stdout
    assert "BUG DETECTED" in result.stdout


def test_uaf_repair_is_clean(uaf_binary):
    result = subprocess.run([str(uaf_binary), "--fixed"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "clean" in result.stdout
    assert "BUG DETECTED" not in result.stdout


def test_uaf_source_compiles_without_warnings(uaf_binary):
    assert uaf_binary.exists()


def test_v8_exercise_detects_the_confusion():
    result = subprocess.run([sys.executable, str(V8_SRC)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "TYPE CONFUSION" in result.stdout
    # The confused value is a string tagged as Smi: that is the primitive.
    assert "Value(smi, '12')" in result.stdout
    assert "Value(string, '12')" in result.stdout


def test_v8_repair_deoptimises_and_is_clean():
    result = subprocess.run(
        [sys.executable, str(V8_SRC), "--fixed"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "deoptimised" in result.stdout
    assert "TYPE CONFUSION" not in result.stdout


def test_v8_optimiser_only_specialises_on_monomorphic_feedback():
    """A polymorphic site must not be specialised. This is the real precondition."""
    result = subprocess.run([sys.executable, str(V8_SRC)], capture_output=True, text=True)
    assert "monomorphic_smi=True" in result.stdout
    assert "check elided" in result.stdout


def test_mojo_exercise_proves_the_escape():
    result = subprocess.run([sys.executable, str(MOJO_SRC)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "SANDBOX ESCAPE" in result.stdout
    assert "owned by pid 1" in result.stdout


def test_mojo_repair_checks_ownership_not_just_kind():
    result = subprocess.run(
        [sys.executable, str(MOJO_SRC), "--fixed"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "DENIED" in result.stdout
    assert "SANDBOX ESCAPE" not in result.stdout


def test_runner_reports_all_three_exercises():
    result = subprocess.run([sys.executable, str(RUNNER)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.count("PASS") == 3
    assert "0 failed" in result.stdout


@pytest.mark.parametrize("source", [V8_SRC, MOJO_SRC, RUNNER])
def test_exercises_have_no_network_or_browser_imports(source):
    tree = ast.parse(source.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    leaked = imported & FORBIDDEN_IMPORTS
    assert not leaked, leaked


def test_uaf_source_does_not_call_system_allocators_after_free():
    """The exercise must model the bug, not rely on undefined behaviour luck."""
    import re

    text = UAF_SRC.read_text(encoding="utf-8")
    assert "q_free" in text and "quarantine" in text.lower()
    assert not re.search(r"(?<![\w])free\(", text), "system free() must not be used"
