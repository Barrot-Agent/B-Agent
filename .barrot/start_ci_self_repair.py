from pathlib import Path
import json
import subprocess
import sys

ROOT = Path.cwd()

task = {
    "objective": "Diagnose and repair the failing GitHub CI for Barrot-Agent/B-Agent",
    "execution_mode": "AUTONOMOUS_SELF_DROP",
    "requirements": [
        "Establish current repository truth using the repository state manifest.",
        "Corroborate repository paths before relying on them.",
        "Inspect .github/workflows/ci.yml and its referenced tests.",
        "Retrieve and analyze actual GitHub CI failure evidence when available.",
        "Reproduce the failure locally where practical.",
        "Separate observed evidence from hypotheses.",
        "Determine the smallest justified repair.",
        "Generate the repair bundle yourself.",
        "Use DELIVER_BUNDLE to drop the generated bundle into the approved workspace.",
        "Verify delivery with SHA-256 evidence.",
        "Execute the delivered bundle.",
        "Run affected tests and appropriate regression tests.",
        "Never use git reset, git clean, git stash, destructive overwrite, or unrelated rollback.",
        "Commit and push only a validated repair.",
        "Re-check GitHub CI after the repair is pushed.",
        "Record evidence for every major state transition.",
        "Never claim success without execution evidence.",
    ],
}

task_path = ROOT / ".barrot" / "barrot_ci_self_drop_task.json"
task_path.parent.mkdir(parents=True, exist_ok=True)
task_path.write_text(json.dumps(task, indent=2) + "\n", encoding="utf-8")

print("=== BARRETT SELF-DROP BOOTSTRAP ===")
print(f"TASK={task_path}")
print("=== REPOSITORY ===")
print("HEAD:", subprocess.check_output(
    ["git", "rev-parse", "HEAD"], text=True
).strip())
print("BRANCH:", subprocess.check_output(
    ["git", "branch", "--show-current"], text=True
).strip())

print("=== ENTRYPOINT DISCOVERY ===")

candidates = [
    [sys.executable, "-m", "scripts.barrot_agent", "--help"],
    [sys.executable, "b_agent.py", "--help"],
]

for command in candidates:
    print("TRY:", " ".join(command))
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=30,
        )
    except Exception as exc:
        print("ERROR:", repr(exc))
        continue

    print("RETURN_CODE:", result.returncode)

    if result.stdout:
        print("--- STDOUT ---")
        print(result.stdout[-6000:])

    if result.stderr:
        print("--- STDERR ---")
        print(result.stderr[-6000:])

print("=== TASK CREATED ===")
print("TASK_PAYLOAD_CREATED=TRUE")
print("The next integration step is to invoke Barrett with this task through its real autonomous action path.")
