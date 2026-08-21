#!/usr/bin/env python3
"""
BARROT TASK ALLOCATOR -- Barrot assigns non-overlapping refactor scope
across barrot/gpt/ibm_bob. Non-overlap enforced because overlapping file
ownership is what causes concurrent-push collisions. Every assignment
becomes a scoped branch + PR through barrot-gated-merge.yml.
"""

import os, json, subprocess, sys, re, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY") or os.environ.get("CHATGPT_TOKEN", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "")

REPO_ROOT = Path(__file__).resolve().parent.parent
BANNED_TERMS = [
    "rm -rf", ".git/", "git reset --hard", "git checkout main", "sed -i",
    "git push", "os.system", "quantum harmonization", "free energy",
    "Willowchip", "Aethel", "144-agent council", "22-agent",
]
FABRICATED_DATA_PATTERNS = ["random.uniform", "random.random", "random.randint"]


def discover_openai_model(api_key):
    req = urllib.request.Request(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
    except Exception as e:
        print(f"[model_discovery] error: {e}")
        return None
    ids = [m["id"] for m in data.get("data", [])]
    excluded = ("embedding", "whisper", "tts", "moderation", "dall-e", "davinci-002", "babbage")
    candidates = sorted(
        [i for i in ids if i.startswith("gpt-") and not any(x in i for x in excluded)],
        reverse=True,
    )
    if candidates:
        print(f"[model_discovery] Selected {candidates[0]} from {len(candidates)} candidates")
        return candidates[0]
    return None


if not OPENAI_MODEL and OPENAI_KEY:
    OPENAI_MODEL = discover_openai_model(OPENAI_KEY) or ""


def call_groq(prompt, max_tokens=2000, tag=""):
    body = json.dumps({
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode()
            return json.loads(raw)["choices"][0]["message"]["content"], raw
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:500]
        print(f"[{tag}] Groq HTTP {e.code}: {err}")
        return "", err
    except Exception as e:
        print(f"[{tag}] Groq error: {e}")
        return "", str(e)


def call_openai(prompt, max_tokens=2000, tag=""):
    if not OPENAI_KEY or not OPENAI_MODEL:
        return "", "OPENAI_KEY or OPENAI_MODEL not available"
    body = json.dumps({
        "model": OPENAI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode()
            return json.loads(raw)["choices"][0]["message"]["content"], raw
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:500]
        print(f"[{tag}] OpenAI HTTP {e.code}: {err}")
        return "", err
    except Exception as e:
        print(f"[{tag}] OpenAI error: {e}")
        return "", str(e)


def extract_json(text):
    if "```" in text:
        for p in text.split("```"):
            p = p.strip()
            if p.startswith("json"):
                p = p[4:].strip()
            if p.startswith("{") or p.startswith("["):
                text = p
                break
    start = min([i for i in (text.find("{"), text.find("[")) if i != -1], default=-1)
    if start == -1:
        return None
    end = max(text.rfind("}"), text.rfind("]")) + 1
    try:
        return json.loads(text[start:end])
    except Exception:
        return None


def repo_snapshot(max_dirs=40):
    entries = []
    for p in sorted(REPO_ROOT.iterdir()):
        if p.name.startswith(".") or p.name in ("node_modules", "__pycache__"):
            continue
        if p.is_dir():
            try:
                size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
                count = sum(1 for _ in p.rglob("*.py"))
            except Exception:
                size, count = 0, 0
            entries.append(f"{p.name}/  ({count} .py files, {size//1024}KB)")
        if len(entries) >= max_dirs:
            break
    return "\n".join(entries)


def allocate_tasks(goal):
    snapshot = repo_snapshot()
    prompt = f"""Refactor goal: {goal}

Real current top-level repo structure:
{snapshot}

Assign refactor scope to exactly 3 workers: "barrot", "gpt", "ibm_bob".
HARD REQUIREMENT: each worker's assigned directories/files must be COMPLETELY
DISJOINT from the others -- no two workers may touch the same file or directory.
If you cannot find 3 genuinely independent scopes, assign fewer workers.

Output ONLY JSON:
{{"assignments": [{{"worker": "barrot|gpt|ibm_bob", "scope": ["dir_or_file"], "task": "specific description"}}], "overlap_check": "..."}}"""
    content, raw = call_groq(prompt, tag="allocate")
    parsed = extract_json(content) if content else None
    if parsed is None:
        print(f"Allocation failed to parse. Raw: {raw[:300]}")
        return None
    assignments = parsed.get("assignments", [])
    seen, validated = set(), []
    for a in assignments:
        scope = set(a.get("scope", []))
        if scope & seen:
            print(f"REJECTED {a.get('worker')}: overlaps {scope & seen}")
            continue
        seen |= scope
        validated.append(a)
    parsed["assignments"] = validated
    return parsed


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)


def check_banned(code):
    for term in BANNED_TERMS:
        if term in code:
            return term
    for pat in FABRICATED_DATA_PATTERNS:
        if pat in code:
            return pat
    return None


def open_pr_for_assignment(assignment, goal):
    worker = assignment["worker"]
    scope = assignment["scope"]
    task = assignment["task"]

    if worker == "ibm_bob":
        tickets_dir = REPO_ROOT / "tasks" / "ibm_bob"
        tickets_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        ticket = tickets_dir / f"refactor_ticket_{stamp}.md"
        ticket.write_text(
            f"# IBM Bob Refactor Ticket\n\n## Goal\n{goal}\n\n## Assigned scope\n"
            + "\n".join(f"- {s}" for s in scope)
            + f"\n\n## Task\n{task}\n\n## Status\nNOT auto-dispatched.\n"
        )
        print(f"[ibm_bob] Ticket written: {ticket}")
        return {"worker": "ibm_bob", "method": "ticket", "path": str(ticket)}

    scope_str = "\n".join(f"- {s}" for s in scope)
    prompt = f"""Refactor task: {task}
Assigned scope (ONLY touch these):
{scope_str}

Propose a concrete code change. Output the full content of ONE file within scope.
Do not touch anything outside scope. No git commands, no rm, no destructive shell ops.
No random.uniform/random/randint to fabricate data.

Format: first line = exact relative file path, blank line, then full file content."""

    if worker == "gpt":
        content, raw = call_openai(prompt, tag=f"gpt:{task[:30]}")
    else:
        content, raw = call_groq(prompt, tag=f"barrot:{task[:30]}")

    if not content:
        return {"worker": worker, "method": "pr", "ok": False, "error": raw[:200]}

    lines = content.strip().split("\n", 1)
    if len(lines) < 2:
        return {"worker": worker, "method": "pr", "ok": False, "error": "malformed response"}

    file_path_str = lines[0].strip().lstrip("#").strip()
    file_content = lines[1].strip()

    if not any(file_path_str.startswith(s.rstrip("/")) for s in scope):
        print(f"[{worker}] REJECTED: {file_path_str} outside scope {scope}")
        return {"worker": worker, "method": "pr", "ok": False, "error": "scope violation"}

    banned = check_banned(file_content)
    if banned:
        print(f"[{worker}] REJECTED: banned '{banned}'")
        return {"worker": worker, "method": "pr", "ok": False, "error": f"banned: {banned}"}

    target = REPO_ROOT / file_path_str
    if target.suffix == ".py":
        tmp = REPO_ROOT / ".allocator_candidate.py"
        tmp.write_text(file_content)
        r = subprocess.run(
            [sys.executable, "-m", "py_compile", str(tmp)],
            capture_output=True,
        )
        tmp.unlink(missing_ok=True)
        if r.returncode != 0:
            return {
                "worker": worker,
                "method": "pr",
                "ok": False,
                "error": f"syntax error: {r.stderr.decode()[:200]}",
            }

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    branch = f"allocator/{worker}-{stamp}"
    git("checkout", "-b", branch)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(file_content)
    git("add", str(target.relative_to(REPO_ROOT)))
    git("commit", "-m", f"[{worker}] {task[:60]}")

    push = git("push", "-u", "origin", branch)
    if push.returncode != 0:
        print(f"[{worker}] Push failed: {push.stderr[:300]}")
        git("checkout", "main")
        return {"worker": worker, "method": "pr", "ok": False, "error": "push failed"}

    body = (
        f"Allocator assignment for **{worker}**\n\n"
        f"**Goal:** {goal}\n\n"
        f"**Task:** {task}\n\n"
        f"**Scope:** {', '.join(scope)}\n\n"
        "Generated by scripts/barrot_task_allocator.py. Requires human review."
    )
    bf = REPO_ROOT / ".allocator_pr_body.md"
    bf.write_text(body)
    pr = subprocess.run(
        [
            "gh", "pr", "create",
            "--title", f"[{worker}] {task[:50]}",
            "--body-file", str(bf),
            "--base", "main",
            "--head", branch,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    bf.unlink(missing_ok=True)
    print(pr.stdout or pr.stderr)
    git("checkout", "main")
    return {
        "worker": worker,
        "method": "pr",
        "ok": pr.returncode == 0,
        "branch": branch,
        "file": file_path_str,
    }


def main():
    if not GROQ_KEY:
        sys.exit("GROQ_API_KEY not set")
    goal = os.environ.get("ALLOCATOR_GOAL", "").strip()
    if not goal:
        goal = "Improve code organization and remove dead paths without changing external behavior"
        print(f"No ALLOCATOR_GOAL set — using default: {goal}")

    print(f"Goal: {goal}\n")
    plan = allocate_tasks(goal)
    if not plan or not plan.get("assignments"):
        print("No valid assignments produced")
        sys.exit(1)

    print(json.dumps(plan, indent=2))
    results = []
    for a in plan["assignments"]:
        print(f"\n--- Processing {a['worker']} ---")
        results.append(open_pr_for_assignment(a, goal))

    print("\n=== RESULTS ===")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
