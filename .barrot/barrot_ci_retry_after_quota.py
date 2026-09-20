from pathlib import Path
from datetime import datetime
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
BARROT = ROOT / "barrot_agent"
EVIDENCE = ROOT / ".barrot" / "ci_remote_evidence"
LOG = ROOT / ".barrot" / "barrot_ci_retry.log"
PID = ROOT / ".barrot" / "barrot_ci_retry.pid"

def log(msg):
    line = f"[{datetime.now().isoformat()}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def run(cmd):
    log("$ " + " ".join(cmd))
    p = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    with LOG.open("a", encoding="utf-8") as f:
        f.write(p.stdout)
    print(p.stdout, flush=True)
    return p

PID.write_text(str(os.getpid()), encoding="utf-8")

log("=== BARROT CI AUTONOMOUS RETRY ===")

# Preserve the actual workspace. No reset/clean/stash.
run(["git", "status", "--short", "--branch"])

# Verify the successful remote CI evidence already captured.
final_run = EVIDENCE / "final_run.json"
if final_run.exists():
    try:
        data = json.loads(final_run.read_text(encoding="utf-8"))
        log(
            "CAPTURED_CI="
            + str(data.get("conclusion"))
            + " RUN="
            + str(data.get("databaseId"))
            + " SHA="
            + str(data.get("headSha"))
        )
    except Exception as exc:
        log(f"CI_EVIDENCE_READ_ERROR={exc}")

# The failed planner reported 36m25s remaining.
# Wait 40 minutes so the daily token window has time to reopen.
WAIT_SECONDS = 40 * 60

log(f"WAITING_FOR_LLM_QUOTA={WAIT_SECONDS}s")
for remaining in range(WAIT_SECONDS, 0, -30):
    if remaining % 300 == 0 or remaining <= 60:
        log(f"QUOTA_RETRY_IN={remaining}s")
    time.sleep(min(30, remaining))

log("QUOTA_WAIT_COMPLETE")

# Confirm GitHub is still reachable.
gh = run([
    "gh", "run", "view", "35251712943",
    "--repo", "Barrot-Agent/B-Agent",
    "--json", "databaseId,status,conclusion,headSha,headBranch,url"
])

# Rebuild the task explicitly around the real evidence.
task = ROOT / ".barrot" / "ci_repair_task.txt"
task.write_text(
    """Barrot V3 autonomous CI repair task.

Repository: Barrot-Agent/B-Agent
Current branch: barrot/tool-call-resilience

REAL REMOTE CI EVIDENCE:
The GitHub Actions workflow ci.yml was manually dispatched against the
current branch and commit. The run completed successfully:
- run_id: 35251712943
- conclusion: success
- commit: 82a0c59f7aea3f86d5873f8b7a0ffa28a6d38639
- 111 tests passed in the core CI suite
- complete logs are in:
  .barrot/ci_remote_evidence/ci_run.log
- structured result is in:
  .barrot/ci_remote_evidence/final_run.json

IMPORTANT:
Do not invent a CI failure.
Determine whether the red condition being investigated is actually on
main or is otherwise stale/different from the successful current-branch run.

Inspect:
1. .barrot/ci_remote_evidence/final_run.json
2. .barrot/ci_remote_evidence/ci_run.log
3. .github/workflows/ci.yml
4. current repository state
5. main branch / its latest CI state if available through the repository's
   existing controlled tooling.

If an actual failing main-branch condition exists, establish it with
evidence, reproduce it locally where possible, create an evidence-backed
repair, validate it, and use the existing controlled repair/delivery
infrastructure.

If no failure exists, record NO_REPAIR_REQUIRED with the successful
evidence and identify the exact remaining synchronization issue.

Never fabricate a failure, test result, commit, remote synchronization,
or completion state.
""",
    encoding="utf-8",
)

log(f"TASK_WRITTEN={task}")

# Launch the existing Barrot controller.
env = os.environ.copy()
env["REPO"] = "Barrot-Agent/B-Agent"
env["BRANCH"] = "barrot/tool-call-resilience"
env["TASK_TITLE"] = (
    "Investigate main CI state using verified GitHub evidence; "
    "repair only an actually reproduced failure"
)

log("LAUNCHING_BARROT")

worker = subprocess.Popen(
    [sys.executable, "scripts/barrot_agent.py"],
    cwd=ROOT,
    env=env,
)

log(f"BARROT_PID={worker.pid}")
log("BARROT_LAUNCH=PASS")

# Keep this supervisor alive and record the worker's actual exit.
rc = worker.wait()

log(f"BARROT_EXIT_CODE={rc}")

run(["git", "status", "--short", "--branch"])

try:
    PID.unlink()
except FileNotFoundError:
    pass

log("=== BARROT CI RETRY FINISHED ===")
