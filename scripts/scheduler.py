#!/usr/bin/env python3
"""
BARROT-Ω SELF-SCHEDULING — queue a task to run at an arbitrary future
time, not just on fixed hourly/weekly crons.

GitHub Actions has no native "run at time T" API. schedule_queue.jsonl
holds pending entries; scheduler-tick.yml runs every 15 min (GitHub's
practical reliable minimum - exact-minute firing is NOT guaranteed,
run_after is a lower bound not an exact time) and dispatches due
entries via `gh workflow run`.

SAFETY: only workflows already present in .github/workflows/ can be
targeted - the queue cannot invoke arbitrary commands even if the
file were tampered with. This adds *when*, never *what*.
"""
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone

QUEUE_PATH = "ping-pongings/knowledge-base/schedule_queue.jsonl"
WORKFLOWS_DIR = ".github/workflows"


def _now():
    return datetime.now(timezone.utc)


def _load():
    if not os.path.exists(QUEUE_PATH):
        return []
    entries = []
    with open(QUEUE_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def _save(entries):
    os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def _valid_workflow(name):
    return os.path.isfile(os.path.join(WORKFLOWS_DIR, name))


def schedule(workflow, run_after_iso, note="", inputs=None):
    if not _valid_workflow(workflow):
        sys.exit(f"Refusing to schedule: '{workflow}' is not a real file in {WORKFLOWS_DIR}/")
    try:
        datetime.fromisoformat(run_after_iso.replace("Z", "+00:00"))
    except ValueError:
        sys.exit(f"run_after must be real ISO 8601, got: {run_after_iso}")

    entry = {
        "id": str(uuid.uuid4())[:8],
        "workflow": workflow,
        "inputs": inputs or {},
        "note": note,
        "run_after": run_after_iso,
        "status": "pending",
        "created_at": _now().isoformat(),
        "created_by": os.environ.get("SCHEDULED_BY", "manual"),
    }
    entries = _load()
    entries.append(entry)
    _save(entries)
    print(f"Scheduled {entry['id']}: {workflow} at {run_after_iso}" + (f" ({note})" if note else ""))
    return entry


def tick():
    entries = _load()
    now = _now()
    changed = False
    fired = 0
    for e in entries:
        if e["status"] != "pending":
            continue
        try:
            due = datetime.fromisoformat(e["run_after"].replace("Z", "+00:00"))
        except ValueError:
            e["status"] = "failed"
            e["error"] = "unparseable run_after"
            changed = True
            continue
        if due > now:
            continue
        if not _valid_workflow(e["workflow"]):
            e["status"] = "failed"
            e["error"] = f"workflow '{e['workflow']}' no longer exists"
            changed = True
            continue

        cmd = ["gh", "workflow", "run", e["workflow"]]
        for k, v in e.get("inputs", {}).items():
            cmd += ["-f", f"{k}={v}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        e["fired_at"] = now.isoformat()
        if result.returncode == 0:
            e["status"] = "done"
        else:
            e["status"] = "failed"
            e["error"] = (result.stderr or result.stdout)[:300]
        changed = True
        fired += 1

    if changed:
        _save(entries)
    print(f"Tick complete: {fired} entr{'y' if fired == 1 else 'ies'} fired, {len(entries)} total in queue.")


def list_pending():
    entries = [e for e in _load() if e["status"] == "pending"]
    for e in sorted(entries, key=lambda x: x["run_after"]):
        print(f"{e['id']}  {e['run_after']}  {e['workflow']}  {e.get('note','')}")
    if not entries:
        print("No pending scheduled tasks.")


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: scheduler.py schedule|tick|list ...")
    cmd = sys.argv[1]
    if cmd == "tick":
        tick()
    elif cmd == "list":
        list_pending()
    elif cmd == "schedule":
        if len(sys.argv) < 4:
            sys.exit("usage: scheduler.py schedule <workflow.yml> <ISO8601-time> [note] [key=val ...]")
        workflow = sys.argv[2]
        run_after_iso = sys.argv[3]
        rest = sys.argv[4:]
        note = ""
        inputs = {}
        for tok in rest:
            if "=" in tok:
                k, v = tok.split("=", 1)
                inputs[k] = v
            else:
                note = tok
        schedule(workflow, run_after_iso, note, inputs)
    else:
        sys.exit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
