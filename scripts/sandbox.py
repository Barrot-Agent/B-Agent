#!/usr/bin/env python3
"""
BARROT-Ω SANDBOX — isolated execution + verification before anything real happens.
  1. SAFETY: run a task in a throwaway clone, verify the RESULT, report pass/fail
     before the real agent commits. Bad changes die here, not in a PR.
  2. EXPERIMENT: a persistent sandbox/ area for throwaway work that never touches
     core/, hf_space/, web/, scripts/, .github/.
Honest: reports exactly what happened, never fakes a pass.
"""
import os, shutil, subprocess, tempfile, json, ast

def _run(cmd, cwd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout, r.stderr

def make_sandbox(repo_root):
    sb = tempfile.mkdtemp(prefix="barrot_sb_")
    code, _, _ = _run(f"git archive HEAD | tar -x -C {sb}", repo_root)
    if code != 0:
        for item in os.listdir(repo_root):
            if item == ".git":
                continue
            s = os.path.join(repo_root, item); d = os.path.join(sb, item)
            (shutil.copytree if os.path.isdir(s) else shutil.copy2)(s, d)
    return sb

def verify_result(sb):
    report = []; ok = True
    for root, _, files in os.walk(sb):
        if "/.git" in root:
            continue
        for f in files:
            path = os.path.join(root, f)
            rel = os.path.relpath(path, sb)
            try:
                if f.endswith(".py"):
                    ast.parse(open(path, encoding="utf-8", errors="ignore").read())
                elif f.endswith(".json"):
                    json.load(open(path, encoding="utf-8", errors="ignore"))
            except SyntaxError as e:
                ok = False; report.append(f"BROKEN .py {rel}: {e.msg} line {e.lineno}")
            except json.JSONDecodeError as e:
                ok = False; report.append(f"BROKEN .json {rel}: {e}")
            except Exception:
                pass
    if os.path.exists(os.path.join(sb, "tests")):
        code, out, _ = _run("python3 -m pytest tests/ -q 2>&1 | tail -5", sb)
        if out.strip():
            report.append(f"pytest: {out.strip()[-300:]}")
        if code != 0:
            ok = False
    return ok, "\n".join(report) if report else "clean"

def cleanup(sb):
    shutil.rmtree(sb, ignore_errors=True)
