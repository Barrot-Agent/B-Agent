#!/usr/bin/env python3
"""Barrot self-upgrade: identify capability gaps, generate a module, verify it,
open a PR. Never pushes to main -- barrot-gated-merge.yml tiers the result."""
import os, json, subprocess, urllib.request, urllib.error, sys, re, time, random
from pathlib import Path
from datetime import datetime, timezone

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"

MODEL_CANDIDATES = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

BANNED_TERMS = [
    "rm -rf", ".git/", "git reset --hard", "git checkout main", "sed -i",
    "git push", "subprocess.run([\"git\"", "os.system",
    "quantum harmonization", "free energy", "Willowchip", "Aethel",
    "Planck-scale", "bio-computing", "144-agent council",
]

def load_audit():
    f = REPO_ROOT / "barrot_capability_audit.json"
    if not f.exists():
        return None
    with open(f) as fh:
        return json.load(fh)

def call_groq(prompt, max_retries=5):
    last_error = ""
    for model in MODEL_CANDIDATES:
        body = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.4,
        }).encode()
        for attempt in range(max_retries):
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=body,
                headers={
                    "Authorization": f"Bearer {GROQ_KEY}",
                    "Content-Type": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(req, timeout=90) as resp:
                    content = json.load(resp)["choices"][0]["message"]["content"]
                    print(f"✓ Groq success with model {model}")
                    return content
            except urllib.error.HTTPError as e:
                status = e.code
                try:
                    err_body = e.read().decode()[:400]
                except Exception:
                    err_body = ""
                last_error = f"HTTP {status}: {e.reason} | {err_body}"
                if status in (401, 403):
                    print(f"✗ {model} → {last_error}")
                    break
                if status in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                    wait = min(2 ** attempt + random.uniform(0, 1.5), 30)
                    print(f"↻ {model} {status} – retry in {wait:.1f}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(wait)
                    continue
                print(f"✗ {model} → {last_error}")
                break
            except Exception as e:
                last_error = str(e)
                print(f"✗ {model} → {last_error}")
                break
    print(f"All models failed. Last error: {last_error}")
    return ""

def strip_fences(text):
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    return m.group(1) if m else text

def generate_capability(gap_id, gap_name):
    prompt = f"""Implement this capability as a standalone Python script: {gap_name} (gap ID {gap_id})

HARD CONSTRAINTS:
- stdlib only (os, sys, json, urllib.request, pathlib, datetime, subprocess for read-only checks)
- Call Groq via urllib for any analysis
- Read GROQ_API_KEY from env; exit non-zero if unset
- Write results to a JSON file; never mutate existing repo files
- NO git commands, NO os.system, NO shell mutation, NO rm
- If real input data is unavailable, write an explicit null/unavailable field.
  NEVER generate placeholder, simulated, or randomized values as if they were results.
- Do not reference hardware, APIs, or database tables you cannot verify exist

Output ONLY the Python source, starting with the shebang."""
    raw = call_groq(prompt)
    if not raw:
        return None
    code = strip_fences(raw).strip()
    if not code.startswith("#!"):
        print("REJECTED: output does not look like a script")
        return None
    for term in BANNED_TERMS:
        if term in code:
            print(f"REJECTED: banned term {term!r}")
            return None
    for fake in ("random.uniform", "random.random", "random.randint", "fake_", "placeholder"):
        if fake in code:
            print(f"REJECTED: fabricated-data pattern {fake!r}")
            return None
    return code

def verify_syntax(code):
    tmp = REPO_ROOT / ".selfupgrade_candidate.py"
    tmp.write_text(code)
    r = subprocess.run([sys.executable, "-m", "py_compile", str(tmp)],
                       capture_output=True, text=True)
    tmp.unlink(missing_ok=True)
    if r.returncode != 0:
        print(f"REJECTED: syntax error\n{r.stderr[:400]}")
        return False
    print("Syntax OK")
    return True

def git(*args, check=False):
    return subprocess.run(["git", *args], cwd=REPO_ROOT,
                          capture_output=True, text=True, check=check)

def open_capability_pr(gap_name, code):
    slug = re.sub(r"[^a-z0-9]+", "_", gap_name.lower()).strip("_")[:40]
    target = SCRIPTS_DIR / f"{slug}.py"
    if target.exists():
        print(f"ABORT: {target.name} already exists")
        return False
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    branch = f"selfupgrade/{slug}-{stamp}"
    git("checkout", "-b", branch)
    target.write_text(code)
    git("add", str(target.relative_to(REPO_ROOT)))
    git("commit", "-m", f"Self-upgrade candidate: {gap_name}")
    push = git("push", "-u", "origin", branch)
    if push.returncode != 0:
        print(f"Push failed: {push.stderr[:300]}")
        git("checkout", "main")
        return False
    body = (f"Autonomous self-upgrade candidate for gap: **{gap_name}**\n\n"
            "Generated by scripts/barrot_self_upgrade.py. Passed banned-term, "
            "fabricated-data, and syntax checks only. NOT executed. "
            "Requires human review before merge.")
    bf = REPO_ROOT / ".selfupgrade_pr_body.md"
    bf.write_text(body)
    pr = subprocess.run(
        ["gh", "pr", "create", "--title", f"Self-upgrade: {gap_name}",
         "--body-file", str(bf), "--base", "main", "--head", branch],
        cwd=REPO_ROOT, capture_output=True, text=True)
    bf.unlink(missing_ok=True)
    print(pr.stdout or pr.stderr)
    git("checkout", "main")
    return pr.returncode == 0

def self_upgrade():
    audit = load_audit()
    if not audit or not audit.get("gaps"):
        print("No capability gaps found")
        return 0
    gap = audit["gaps"][0]
    print(f"Upgrading: {gap['name']} (id {gap['id']})")
    code = generate_capability(gap["id"], gap["name"])
    if not code or not verify_syntax(code):
        print("Generation or verification failed")
        return 1
    if open_capability_pr(gap["name"], code):
        print(f"✓ Self-upgrade candidate opened as PR: {gap['name']}")
        return 0
    print("Failed to open PR")
    return 1

if __name__ == "__main__":
    if not GROQ_KEY:
        print("GROQ_API_KEY not set")
        sys.exit(1)
    sys.exit(self_upgrade())
