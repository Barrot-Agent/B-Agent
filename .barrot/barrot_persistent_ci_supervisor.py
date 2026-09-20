from pathlib import Path
from datetime import datetime, timezone, timedelta
import json
import os
import re
import subprocess
import sys
import time

ROOT = Path.cwd()
STATE = ROOT / ".barrot" / "persistent_ci_supervisor.json"
LOG = ROOT / ".barrot" / "persistent_ci_supervisor.log"
BARROT_LOG = ROOT / ".barrot" / "persistent_barrot_run.log"
TASK = ROOT / ".barrot" / "ci_repair_task.txt"

CI_RUN = "35251712943"
CI_SHA = "82a0c59f7aea3f86d5873f8b7a0ffa28a6d38639"
BRANCH = "barrot/tool-call-resilience"

def log(msg):
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def save(state):
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")

def load():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "ci_run": CI_RUN,
        "ci_sha": CI_SHA,
        "branch": BRANCH,
        "attempt": 0,
        "stage": "INITIALIZED",
        "next_attempt": None,
        "last_exit": None,
    }

def gh(*args):
    p = subprocess.run(
        ["gh", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return p.returncode, p.stdout

def check_ci():
    rc, out = gh(
        "run", "view", CI_RUN,
        "--repo", "Barrot-Agent/B-Agent",
        "--json", "databaseId,status,conclusion,headSha,headBranch,url"
    )
    if rc == 0:
        try:
            data = json.loads(out)
            log(
                f"CI_RUN={data.get('databaseId')} "
                f"STATUS={data.get('status')} "
                f"CONCLUSION={data.get('conclusion')} "
                f"SHA={data.get('headSha')}"
            )
            return data
        except Exception:
            pass
    log("CI_QUERY_FAILED")
    return None

def check_main():
    rc, out = gh(
        "run", "list",
        "--repo", "Barrot-Agent/B-Agent",
        "--workflow", "ci.yml",
        "--branch", "main",
        "--limit", "1",
        "--json", "databaseId,status,conclusion,headSha,url"
    )
    evidence = ROOT / ".barrot" / "ci_remote_evidence" / "main_latest.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)

    if rc == 0:
        try:
            data = json.loads(out)
            evidence.write_text(json.dumps(data, indent=2), encoding="utf-8")
            log(f"MAIN_CI={json.dumps(data)}")
            return data
        except Exception:
            pass

    evidence.write_text(
        json.dumps({"query_failed": True, "raw": out}, indent=2),
        encoding="utf-8",
    )
    log("MAIN_CI_QUERY_FAILED")
    return None

def git_status():
    rc, out = subprocess.getstatusoutput("git status --short")
    (ROOT / ".barrot" / "persistent_git_status.txt").write_text(
        out + "\n", encoding="utf-8"
    )
    return out

def detect_quota(text):
    if "LLM_RATE_LIMITED" not in text and "HTTP 429" not in text:
        return None

    matches = re.findall(
        r"retry in ([0-9]+(?:\.[0-9]+)?)m([0-9]+(?:\.[0-9]+)?)s",
        text,
        flags=re.I,
    )
    if matches:
        minutes, seconds = matches[-1]
        return float(minutes) * 60 + float(seconds)

    matches = re.findall(
        r"retry in ([0-9]+(?:\.[0-9]+)?)s",
        text,
        flags=re.I,
    )
    if matches:
        return float(matches[-1])

    return 2700.0

def run_barrot(state):
    state["attempt"] += 1
    state["stage"] = "BARROT_RUNNING"
    state["last_started"] = datetime.now(timezone.utc).isoformat()
    save(state)

    TASK.write_text(
        """Investigate and repair the actual CI/repository state for Barrot V3.

Use repository evidence and controlled tooling only.
The known successful remote CI evidence is:
run 35251712943
branch barrot/tool-call-resilience
commit 82a0c59f7aea3f86d5873f8b7a0ffa28a6d38639
111 tests passed.

Determine whether main has a concrete CI failure and whether the current
repository contains a deterministic defect requiring repair.

Do not invent failures.
Do not overwrite unrelated work.
Preserve all existing changes and evidence.
If a repair is required, diagnose it, apply the smallest controlled repair,
validate it locally, and preserve the evidence.
If no repair is required, record that conclusion with evidence.

The objective is evidence-backed repository repair, not cosmetic CI manipulation.
""",
        encoding="utf-8",
    )

    log(f"BARROT_ATTEMPT={state['attempt']} START")

    with BARROT_LOG.open("a", encoding="utf-8") as f:
        p = subprocess.Popen(
            ["python", "scripts/barrot_agent.py"],
            cwd=ROOT,
            stdout=f,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        state["barrot_pid"] = p.pid
        save(state)
        log(f"BARROT_PID={p.pid}")
        rc = p.wait()

    state["last_exit"] = rc
    state["last_finished"] = datetime.now(timezone.utc).isoformat()
    state["stage"] = "BARROT_FINISHED"
    save(state)

    log(f"BARROT_EXIT={rc}")

    text = ""
    if BARROT_LOG.exists():
        text = BARROT_LOG.read_text(encoding="utf-8", errors="replace")

    quota = detect_quota(text)
    if quota is not None:
        wait = max(int(quota) + 300, 900)
        state["next_attempt"] = (
            datetime.now(timezone.utc) + timedelta(seconds=wait)
        ).isoformat()
        state["stage"] = "QUOTA_WAIT"
        state["quota_wait_seconds"] = wait
        save(state)
        log(f"QUOTA_DETECTED=YES RETRY_IN={wait}s")
        return

    state["next_attempt"] = None
    state["stage"] = "POST_BARROT_EVALUATION"
    save(state)

def main():
    ROOT.joinpath(".barrot").mkdir(exist_ok=True)
    state = load()

    log("=== BARROT PERSISTENT SUPERVISOR ===")
    log(f"BRANCH={BRANCH}")
    log(f"KNOWN_GREEN_CI={CI_RUN}")

    check_ci()
    check_main()

    status = git_status()
    log(f"GIT_STATUS_LINES={len(status.splitlines()) if status else 0}")

    if state.get("stage") == "BARROT_RUNNING":
        pid = state.get("barrot_pid")
        if pid:
            try:
                os.kill(pid, 0)
                log(f"BARROT_ALREADY_RUNNING={pid}")
                return
            except OSError:
                state["stage"] = "RECOVERING_AFTER_PROCESS_LOSS"
                save(state)

    next_attempt = state.get("next_attempt")
    if next_attempt:
        try:
            when = datetime.fromisoformat(next_attempt)
            now = datetime.now(timezone.utc)
            if now < when:
                remaining = int((when - now).total_seconds())
                log(f"WAITING_FOR_QUOTA={remaining}s")
                return
        except Exception:
            state["next_attempt"] = None
            save(state)

    run_barrot(state)

    check_ci()
    check_main()
    git_status()

if __name__ == "__main__":
    main()
