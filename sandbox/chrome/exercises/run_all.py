#!/usr/bin/env python3
"""Run the three sandbox exercises and report what each one proves.

    python3 sandbox/chrome/exercises/run_all.py

Compiles the C exercise with gcc. If gcc is missing the C exercise is reported
as SKIPPED, not as passed. Nothing here touches a network, a browser, or a live
site.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SCRIPTS = {
    "v8_type_confusion": BASE / "v8_type_confusion" / "jit_type_confusion.py",
    "mojo_confused_deputy": BASE / "mojo_confused_deputy" / "mojo_confused_deputy.py",
}
EXERCISES = (
    ("uaf", "use-after-free", "BUG DETECTED"),
    ("v8_type_confusion", "jit type confusion", "TYPE CONFUSION"),
    ("mojo_confused_deputy", "mojo confused deputy", "SANDBOX ESCAPE"),
)


def run_uaf() -> tuple[str, str]:
    source = BASE / "uaf" / "uaf.c"
    binary = BASE / "uaf" / "uaf"
    build = subprocess.run(
        ["gcc", "-O0", "-g", "-Wall", "-Wextra", "-o", str(binary), str(source)],
        capture_output=True,
        text=True,
    )
    if build.returncode != 0:
        return "SKIPPED", f"gcc failed: {build.stderr.strip().splitlines()[:1]}"
    vuln = subprocess.run([str(binary)], capture_output=True, text=True)
    fixed = subprocess.run([str(binary), "--fixed"], capture_output=True, text=True)
    return _verdict(vuln, fixed, "BUG DETECTED")


def run_python(name: str, marker: str) -> tuple[str, str]:
    script = SCRIPTS[name]
    vuln = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    fixed = subprocess.run(
        [sys.executable, str(script), "--fixed"], capture_output=True, text=True
    )
    return _verdict(vuln, fixed, marker)


def _verdict(vuln, fixed, marker: str) -> tuple[str, str]:
    if vuln.returncode != 1:
        return "FAIL", f"vulnerable mode returned {vuln.returncode}, expected 1"
    if marker not in vuln.stdout:
        return "FAIL", f"vulnerable mode did not report {marker!r}"
    if fixed.returncode != 0:
        return "FAIL", f"fixed mode returned {fixed.returncode}, expected 0"
    if marker in fixed.stdout:
        return "FAIL", "fixed mode still reports the bug"
    return "PASS", f"vulnerable detected, repaired clean ({marker})"


def main() -> int:
    print(f"{'exercise':<34}{'result':<10}detail")
    print("-" * 90)
    failures = 0
    for name, label, marker in EXERCISES:
        if name == "uaf":
            status, detail = run_uaf()
        else:
            status, detail = run_python(name, marker)
        if status == "FAIL":
            failures += 1
        print(f"{label:<34}{status:<10}{detail}")
    print("-" * 90)
    print(f"{len(EXERCISES)} exercises, {failures} failed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
