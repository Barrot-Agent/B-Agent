#!/usr/bin/env python3
"""
BARROT-Ω TERMUX RUNNER — executes queued command bundles locally on
Sean's device instead of him pasting them by hand.
"""
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

QUEUE_PATH = "ping-pongings/knowledge-base/termux_tasks.jsonl"
APPROVAL_STORE_PATH = Path(
    os.environ.get(
        "BARROT_LOCAL_APPROVAL_STORE",
        str(Path.home() / ".config" / "barrot" / "approved_tasks.json"),
    )
).expanduser()
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


def _command_digest(commands):
    """Hash the exact ordered command list so approval cannot survive edits."""
    payload = json.dumps(commands, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_approvals():
    # This store must remain on the local device, outside the repository queue.
    try:
        data = json.loads(APPROVAL_STORE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_approvals(approvals):
    APPROVAL_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = APPROVAL_STORE_PATH.with_name(
        f".{APPROVAL_STORE_PATH.name}.{os.getpid()}.tmp"
    )
    try:
        temporary.write_text(
            json.dumps(approvals, ensure_ascii=False, indent=2, sort_keys=True) + "\\n",
            encoding="utf-8",
        )
        os.chmod(temporary, 0o600)
        os.replace(temporary, APPROVAL_STORE_PATH)
        os.chmod(APPROVAL_STORE_PATH, 0o600)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _approval_matches(task, approvals=None):
    approvals = _load_approvals() if approvals is None else approvals
    task_id = str(task.get("id", ""))
    record = approvals.get(task_id)
    commands = task.get("commands")
    return (
        isinstance(record, dict)
        and isinstance(commands, list)
        and record.get("commands_sha256") == _command_digest(commands)
    )


def approve_task(task_id):
    """Interactively approve one exact pending command list on this device."""
    task = next((entry for entry in _load() if str(entry.get("id")) == str(task_id)), None)
    if task is None or task.get("status") != "pending":
        print("Approval refused: task was not found as pending.")
        return False

    commands = task.get("commands")
    if not isinstance(commands, list) or not commands or any(
        not isinstance(command, str) or not command.strip() for command in commands
    ):
        print("Approval refused: task command list is invalid.")
        return False

    print(f"Task ID: {task_id}")
    print(f"Note: {task.get('note', '')}")
    print("Exact commands to execute:")
    for index, command in enumerate(commands, start=1):
        print(f"  {index}. {command}")
    expected = f"APPROVE {task_id}"
    print(f"To authorize this exact list locally, type: {expected}")
    try:
        response = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("Approval cancelled.")
        return False
    if response != expected:
        print("Approval cancelled; no local approval was written.")
        return False

    approvals = _load_approvals()
    approvals[str(task_id)] = {
        "commands_sha256": _command_digest(commands),
        "approved_at": _now().isoformat(),
    }
    _write_approvals(approvals)
    print(f"Local approval recorded for task {task_id}.")
    return True


def _consume_task_approval(task):
    """Consume approval before execution; edited or replayed tasks fail closed."""
    approvals = _load_approvals()
    task_id = str(task.get("id", ""))
    if not _approval_matches(task, approvals):
        return False
    del approvals[task_id]
    # If this write fails, the exception prevents command execution.
    _write_approvals(approvals)
    return True


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
    pending_seen = False
    for e in entries:
        if e["status"] != "pending":
            continue
        pending_seen = True
        if not _consume_task_approval(e):
            print(
                f"BLOCKED task {e.get('id')}: local approval required; "
                f"run 'python scripts/termux_runner.py approve {e.get('id')}' "
                "on this device after reviewing the exact commands."
            )
            continue
        print(f"Running locally approved task {e['id']}: {e.get('note','')}")
        _run_task(e)
        _save(entries)
        _git_commit_push(f"Termux runner: task {e['id']} {e['status']} [skip ci]")
        fired += 1
        print(f"  -> {'OK' if e['status']=='done' else 'FAILED'}")
    if fired == 0:
        if pending_seen:
            print("No approved pending tasks executed; unapproved tasks remain pending.")
        else:
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
        sys.exit("usage: termux_runner.py enqueue <note> (commands on stdin) | approve <task_id> | once | watch [interval]")
    cmd = sys.argv[1]
    if cmd == "enqueue":
        note = sys.argv[2] if len(sys.argv) > 2 else ""
        commands = [line.rstrip("\n") for line in sys.stdin if line.strip()]
        if not commands:
            sys.exit("no commands provided on stdin")
        enqueue(commands, note)
    elif cmd == "approve":
        if len(sys.argv) < 3:
            sys.exit("usage: termux_runner.py approve <task_id>")
        sys.exit(0 if approve_task(sys.argv[2]) else 1)
    elif cmd == "once":
        process_pending()
    elif cmd == "watch":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        watch(interval)
    else:
        sys.exit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
