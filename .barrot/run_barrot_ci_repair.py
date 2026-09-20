
from pathlib import Path
from datetime import datetime
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / ".barrot" / "ci_remote_evidence"
EVIDENCE.mkdir(parents=True, exist_ok=True)

def run(cmd, check=False):
    print("$", " ".join(cmd))
    p = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(p.stdout)
    if check and p.returncode != 0:
        raise SystemExit(p.returncode)
    return p

def save(name, text):
    p = EVIDENCE / name
    p.write_text(text, encoding="utf-8")
    return p

print("=== BARROT REAL CI INVESTIGATION ===")
print("TIME:", datetime.now().isoformat())

# Never destroy existing work.
run(["git", "status", "--short", "--branch"])

if shutil.which("gh") is None:
    print("BLOCKED: GitHub CLI (gh) is not installed.")
    print("Barrot was NOT launched because remote CI evidence cannot be obtained.")
    raise SystemExit(20)

auth = run(["gh", "auth", "status"])
if auth.returncode != 0:
    print("BLOCKED: GitHub CLI is not authenticated.")
    raise SystemExit(21)

repo = "Barrot-Agent/B-Agent"
workflow = "ci.yml"

# Capture the exact current branch and commit before dispatch.
branch = run(["git", "branch", "--show-current"]).stdout.strip()
sha = run(["git", "rev-parse", "HEAD"]).stdout.strip()

save("dispatch_context.txt",
     f"repository={repo}\nbranch={branch}\nsha={sha}\n"
     f"started={datetime.now().isoformat()}\n")

print("DISPATCHING REAL GITHUB ACTIONS RUN")
dispatch = run([
    "gh", "workflow", "run", workflow,
    "--repo", repo,
    "--ref", branch,
])

if dispatch.returncode != 0:
    print("WORKFLOW_DISPATCH=FAILED")
    raise SystemExit(22)

print("WORKFLOW_DISPATCH=PASS")

# Give GitHub time to register the run.
time.sleep(8)

run_info = None
for attempt in range(30):
    q = run([
        "gh", "run", "list",
        "--repo", repo,
        "--workflow", workflow,
        "--branch", branch,
        "--limit", "10",
        "--json", "databaseId,status,conclusion,headSha,headBranch,url,createdAt,updatedAt",
    ])

    if q.returncode == 0:
        try:
            runs = json.loads(q.stdout)
        except Exception:
            runs = []

        candidates = [
            x for x in runs
            if x.get("headSha") == sha
        ]

        if candidates:
            run_info = candidates[0]
            break

    time.sleep(5)

if not run_info:
    save("run_lookup.txt", "No matching workflow run found.\n")
    print("BLOCKED: GitHub did not expose a matching run for the current commit.")
    raise SystemExit(23)

save("run.json", json.dumps(run_info, indent=2))

run_id = str(run_info["databaseId"])
print("RUN_ID=", run_id)
print("RUN_URL=", run_info.get("url"))

# Wait for the actual remote job to finish.
for attempt in range(90):
    q = run([
        "gh", "run", "view", run_id,
        "--repo", repo,
        "--json", "databaseId,status,conclusion,headSha,headBranch,url,createdAt,updatedAt,jobs",
    ])

    if q.returncode == 0:
        save("run_status.json", q.stdout)
        try:
            state = json.loads(q.stdout)
        except Exception:
            state = {}

        status = state.get("status")
        conclusion = state.get("conclusion")

        print(f"REMOTE_STATUS={status}")
        print(f"REMOTE_CONCLUSION={conclusion}")

        if status == "completed":
            break

    time.sleep(10)

# Capture complete GitHub run information and logs.
final = run([
    "gh", "run", "view", run_id,
    "--repo", repo,
    "--json", "databaseId,status,conclusion,headSha,headBranch,url,createdAt,updatedAt,jobs",
])

save("final_run.json", final.stdout)

logs = run([
    "gh", "run", "view", run_id,
    "--repo", repo,
    "--log",
])

save("ci_run.log", logs.stdout)

summary = {
    "repository": repo,
    "branch": branch,
    "commit": sha,
    "run_id": run_id,
    "url": run_info.get("url"),
    "captured_at": datetime.now().isoformat(),
    "logs_file": str(EVIDENCE / "ci_run.log"),
}

save("evidence_manifest.json", json.dumps(summary, indent=2))

print()
print("=== REMOTE CI EVIDENCE SAVED ===")
print(EVIDENCE / "final_run.json")
print(EVIDENCE / "ci_run.log")
print("RUN_URL=", run_info.get("url"))

# Now launch the existing autonomous repair worker.
# It must inspect the persisted remote evidence rather than inventing a failure.
print()
print("=== LAUNCHING BARROT REPAIR WORKER ===")

env = os.environ.copy()
env["REPO"] = repo
env["BRANCH"] = branch
env["TASK_TITLE"] = (
    "Analyze and repair failing CI using the real GitHub Actions evidence "
    "in .barrot/ci_remote_evidence"
)

worker = subprocess.Popen(
    [sys.executable, "scripts/barrot_agent.py"],
    cwd=ROOT,
    env=env,
)

print("BARROT_PID=", worker.pid)
print("BARROT_LAUNCHED=PASS")

raise SystemExit(0)
