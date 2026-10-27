#!/usr/bin/env python3
"""
BARROT-Omega SELF-BENCHMARK HARNESS - real, small, honest.

Not a claim of SWE-Bench or FrontierCode parity - those require full
repo-context tasks with human review. This is a small, fixed set of
self-contained coding tasks with real, deterministic test functions.
Barrot's own model attempts each one; the generated code is executed in
a subprocess and checked against the real test. Pass/fail is recorded,
never inferred or assumed.
"""

import ast
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone

KB_DIR = "ping-pongings/knowledge-base"
LOG_PATH = os.path.join(KB_DIR, "benchmark_log.jsonl")
KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = os.environ.get("BRAIN_MODEL", "").strip() or "openai/gpt-oss-120b"

TASKS = [
    {
        "name": "reverse_linked_list",
        "prompt": (
            "Write a Python function `reverse_list(head)` that reverses a "
            "singly linked list. Each node is an object with `.val` and "
            "`.next` attributes. Return the new head. Also define a "
            "`Node` class with `__init__(self, val, next=None)`. "
            "Return ONLY a Python code block, no prose."
        ),
        "test": (
            "def run_test(ns):\n"
            "    Node = ns['Node']\n"
            "    reverse_list = ns['reverse_list']\n"
            "    n3 = Node(3)\n"
            "    n2 = Node(2, n3)\n"
            "    n1 = Node(1, n2)\n"
            "    new_head = reverse_list(n1)\n"
            "    vals = []\n"
            "    node = new_head\n"
            "    while node:\n"
            "        vals.append(node.val)\n"
            "        node = node.next\n"
            "    assert vals == [3, 2, 1], f'expected [3,2,1], got {vals}'\n"
        ),
    },
    {
        "name": "off_by_one_fix",
        "prompt": (
            "This function should return the sum of all integers from "
            "1 to n inclusive, but has an off-by-one bug:\n\n"
            "def sum_to_n(n):\n"
            "    total = 0\n"
            "    for i in range(1, n):\n"
            "        total += i\n"
            "    return total\n\n"
            "Fix the bug. Return ONLY the corrected function as a Python "
            "code block, no prose."
        ),
        "test": (
            "def run_test(ns):\n"
            "    f = ns['sum_to_n']\n"
            "    assert f(5) == 15, f'expected 15, got {f(5)}'\n"
            "    assert f(1) == 1, f'expected 1, got {f(1)}'\n"
        ),
    },
    {
        "name": "dedupe_preserve_order",
        "prompt": (
            "Write a Python function `dedupe(items)` that removes "
            "duplicate elements from a list while preserving the original "
            "order of first occurrence. Return ONLY a Python code block, "
            "no prose."
        ),
        "test": (
            "def run_test(ns):\n"
            "    f = ns['dedupe']\n"
            "    assert f([1,2,2,3,1,4]) == [1,2,3,4], f'got {f([1,2,2,3,1,4])}'\n"
            "    assert f([]) == [], f'got {f([])}'\n"
        ),
    },
]


def ask(prompt):
    body = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.0,
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def extract_code(raw):
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            body = part[6:] if part.startswith("python") else part
            if not body.strip():
                continue
            try:
                ast.parse(body)
                return body
            except SyntaxError:
                continue
    try:
        ast.parse(raw)
        return raw
    except SyntaxError:
        return raw


def run_task_in_subprocess(code, test_code, timeout=10):
    harness = (
        code
        + "\n\n"
        + test_code
        + "\n\n"
        + "ns = dict(globals())\n"
        "try:\n"
        "    run_test(ns)\n"
        "    print('PASS')\n"
        "except Exception as e:\n"
        "    print(f'FAIL: {type(e).__name__}: {e}')\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(harness)
        path = f.name
    try:
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, "timeout"
    finally:
        os.unlink(path)

    out = (result.stdout or "").strip()
    err = (result.stderr or "").strip()
    last_line = out.splitlines()[-1] if out else ""
    if last_line == "PASS":
        return True, "PASS" if out == "PASS" else f"PASS (extra stdout: {out[:150]})"
    if last_line.startswith("FAIL:"):
        return False, last_line
    return False, f"no clean PASS/FAIL output. stdout={out[:200]} stderr={err[:200]}"


def main():
    if not KEY:
        sys.exit("GROQ_API_KEY not set")
    os.makedirs(KB_DIR, exist_ok=True)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results = []
    for task in TASKS:
        raw = ""
        code = ""
        try:
            raw = ask(task["prompt"])
            code = extract_code(raw)
            passed, detail = run_task_in_subprocess(code, task["test"])
        except Exception as ex:
            passed, detail = False, f"harness_error: {ex}"
        results.append(
            {
                "task": task["name"],
                "passed": passed,
                "detail": detail[:300],
                "raw_response_preview": None if passed else raw[:500],
                "extracted_code_preview": None if passed else code[:500],
            }
        )
        print(f"  [{'PASS' if passed else 'FAIL'}] {task['name']}: {detail[:100]}")

    record = {
        "run_id": run_id,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "tasks_total": len(TASKS),
        "tasks_passed": sum(1 for r in results if r["passed"]),
        "results": results,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")
    print(f"\n{record['tasks_passed']}/{record['tasks_total']} passed. Logged as {run_id}.")


if __name__ == "__main__":
    main()
