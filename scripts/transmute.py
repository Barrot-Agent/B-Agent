"""Barrot Transmute Engine - variants, test, keep winner, rollback if worse."""
import subprocess, json, time, sys, os, shutil
from pathlib import Path

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    return r.returncode == 0, r.stdout + r.stderr

def score_file(path):
    ok, out = run(f"python3 -m py_compile {path}")
    lines = len(Path(path).read_text(errors='ignore').splitlines()) if Path(path).exists() else 9999
    return {"compiles": ok, "lines": lines, "output": out[:500]}

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "barrot_integration.py"
    print(f"TRANSMUTE TARGET: {target}")
    print("1. Checkpoint first: git add -A && git commit -m 'checkpoint before transmute'")
    print("2. Create 2-3 variants manually in Barrot, then run this to score.")
    print("3. Score:", score_file(target))
    Path("results").mkdir(exist_ok=True)
    Path("results/transmute_log.json").write_text(json.dumps({"target": target, "score": score_file(target), "ts": time.time()}, indent=2))
    print("Logged to results/transmute_log.json")
