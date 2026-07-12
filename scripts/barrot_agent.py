#!/usr/bin/env python3
"""
BARROT AGENT — autonomous repo worker
Triggered by an issue labeled 'barrot-task'. Reads the task, works in a
branch, opens ONE pull request. Never pushes to main. The gated-merge
workflow + your 'approved' label decide what lands.
"""
import os, subprocess, json, urllib.request, sys

REPO   = os.environ["REPO"]
TASK   = os.environ.get("TASK_BODY", "")
TITLE  = os.environ.get("TASK_TITLE", "Barrot task")
ISSUE  = os.environ.get("ISSUE_NUMBER", "")
BRANCH = os.environ.get("BRANCH", "barrot/task")
KEY    = os.environ.get("GROQ_API_KEY", "")
MODEL  = os.environ.get("BRAIN_MODEL", "llama-3.3-70b-versatile")

def run(cmd, check=True, quiet=False):
    print("+", cmd)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if not quiet:
        if r.stdout.strip(): print(r.stdout[:3000])
        if r.stderr.strip(): print(r.stderr[:3000])
    if check and r.returncode != 0:
        sys.exit(f"command failed: {cmd}\n{r.stderr[:1000]}")
    return r.stdout

NOISE_PREFIXES = (".git", ".npm", "node_modules", ".cache", "_cacache")

def repo_inventory(max_files=400):
    files = run("git ls-files", check=False, quiet=True).splitlines()
    files = [f for f in files if not any(f.startswith(p) for p in NOISE_PREFIXES)]
    tree = []
    for f in files[:max_files]:
        try: sz = os.path.getsize(f)
        except OSError: sz = 0
        tree.append(f"{f} ({sz}b)")
    extra = len(files) - max_files
    if extra > 0:
        tree.append(f"... ({extra} more files omitted)")
    return "\n".join(tree)

def ask_brain(system, user):
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role":"system","content":system},{"role":"user","content":user}],
        "max_tokens": 4096, "temperature": 0.2,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.load(resp)["choices"][0]["message"]["content"]

SYSTEM = """You are Barrot-Ω operating as an autonomous repository engineer on your own repo.
You output ONLY a JSON array of shell commands (git mv, mkdir -p, rm, sed) that perform the
requested task. No prose, no markdown fences, no explanation. Each command must be safe and
scoped. Never use 'git add -A'. Never touch .git/. Never delete files under core/, hf_space/,
web/, or scripts/emit_signal.py. Output format: ["cmd1","cmd2",...]"""

def main():
    run("git config user.email 'barrot@barrot-agent.com'")
    run("git config user.name 'Barrot-Agent'")
    run(f"git checkout -b {BRANCH}")

    inv = repo_inventory()
    prompt = f"TASK:\n{TITLE}\n{TASK}\n\nCURRENT REPO FILES:\n{inv}\n\nOutput the JSON command array."
    raw = ask_brain(SYSTEM, prompt).strip()

    a, b = raw.find("["), raw.rfind("]")
    if a == -1 or b == -1:
        sys.exit(f"brain did not return a command array:\n{raw[:500]}")
    cmds = json.loads(raw[a:b+1])

    BANNED = ["git add -a", "git push", "rm -rf", ".git/", "git reset --hard", "git checkout main"]
    PROTECTED_DEL = ["rm core/", "rm hf_space/", "rm web/", "rm scripts/emit_signal.py"]
    safe = []
    for c in cmds:
        low = c.lower()
        if any(x in low for x in BANNED) or any(p in low for p in PROTECTED_DEL):
            print("REJECTED unsafe command:", c); continue
        safe.append(c)
    if not safe:
        sys.exit("no safe commands produced")

    for c in safe:
        run(c, check=False)

    run("git add -u", check=False)
    run("git add .", check=False)
    if not run("git status --porcelain", check=False).strip():
        sys.exit("no changes produced")

    summary = "\\n".join(f"- {c}" for c in safe)
    run('git commit -m "Barrot autonomous task: ' + TITLE.replace('"',"'") + '"')
    run(f"git push origin {BRANCH}")

    pr_body = (f"Autonomous execution of #{ISSUE} by Barrot.\\n\\nCommands run:\\n{summary}\\n\\n"
               f"Review the diff; apply the approved label to merge protected or large changes.")
    run(f'gh pr create --repo {REPO} --title "Barrot: {TITLE}" --body "{pr_body}" --head {BRANCH} --base main', check=False)
    print("DONE — PR opened, awaiting gate + review.")

if __name__ == "__main__":
    main()
