#!/usr/bin/env python3
"""
BARROT-Ω TERMUX RUNNER — executes queued command bundles locally on
Sean's device instead of him pasting them by hand.
"""
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone

QUEUE_PATH = "ping-pongings/knowledge-base/termux_tasks.jsonl"
CATASTROPHIC = [
    "rm -rf /", "rm -rf /*", "rm -rf ~", "rm -rf $HOME",
    ":(){ :|:& };:", "mkfs.", "> /dev/sda", "dd if=/dev/zero of=/dev",
]


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


def _is_catastrophic(cmd):
    lowered = cmd.lower()
    return any(pattern in lowered for pattern in CATASTROPHIC)


def _git_commit_push(message):
    subprocess.run(["git", "add", QUEUE_PATH], check=False)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if diff.returncode == 0:
        return
    subprocess.run(["git", "commit", "-m", message], check=False)
    push = subprocess.run(["git", "push"], capture_output=True, text=True)
    if push.returncode != 0:
        subprocess.run(["git", "pull", "--no-rebase", "--no-edit", "origin", "main"], check=False)
        subprocess.run(["git", "push"], check=False)


def enqueue(commands, note=""):
    bad = [c for c in commands if _is_catastrophic(c)]
    if bad:
        sys.exit(f"Refusing to enqueue - catastrophic pattern matched in: {bad}")
    entry = {
        "id": str(uuid.uuid4())[:8],
        "commands": commands,
        "note": note,
        "status": "pending",
        "created_at": _now().isoformat(),
        "results": [],
    }
    entries = _load()
    entries.append(entry)
    _save(entries)
    print(f"Enqueued {entry['id']}: {len(commands)} command(s)" + (f" ({note})" if note else ""))
    return entry


def _run_task(e):
    e["status"] = "running"
    e["started_at"] = _now().isoformat()
    results = []
    ok = True
    for cmd in e["commands"]:
        if _is_catastrophic(cmd):
            results.append({"cmd": cmd, "returncode": -1, "stdout": "", "stderr": "BLOCKED: catastrophic pattern"})
            ok = False
            break
        proc = subprocess.run(cmd, shell=True, cwd=os.getcwd(),
                               capture_output=True, text=True, timeout=600)
        results.append({
            "cmd": cmd,
            "returncode": proc.returncode,
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-2000:],
        })
        if proc.returncode != 0:
            ok = False
            break
    e["results"] = results
    e["status"] = "done" if ok else "failed"
    e["finished_at"] = _now().isoformat()
    return e


def process_pending():
    entries = _load()
    fired = 0
    for e in entries:
        if e["status"] != "pending":
            continue
        print(f"Running task {e['id']}: {e.get('note','')}")
        _run_task(e)
        _save(entries)
        _git_commit_push(f"Termux runner: task {e['id']} {e['status']} [skip ci]")
        fired += 1
        print(f"  -> {'OK' if e['status']=='done' else 'FAILED'}")
    if fired == 0:
        print("No pending tasks.")
    return fired


def watch(interval=30):
    print(f"Watching {QUEUE_PATH} every {interval}s. Ctrl+C to stop.")
    try:
        while True:
            subprocess.run(["git", "pull", "--no-rebase", "--no-edit", "origin", "main"], capture_output=True)
            process_pending()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped.")


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: termux_runner.py enqueue <note> (commands on stdin) | once | watch [interval]")
    cmd = sys.argv[1]
    if cmd == "enqueue":
        note = sys.argv[2] if len(sys.argv) > 2 else ""
        commands = [line.rstrip("\n") for line in sys.stdin if line.strip()]
        if not commands:
            sys.exit("no commands provided on stdin")
        enqueue(commands, note)
    elif cmd == "once":
        process_pending()
    elif cmd == "watch":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        watch(interval)
    else:
        sys.exit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
