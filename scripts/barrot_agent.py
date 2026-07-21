#!/usr/bin/env python3
"""
BARROT AGENT — autonomous repo worker
Triggered by an issue labeled 'barrot-task'. Reads the task, works in a
branch, opens ONE pull request. Never pushes to main. The gated-merge
workflow + your 'approved' label decide what lands.
"""

import os, subprocess, json, urllib.request, urllib.error, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sandbox import verify_result

REPO = os.environ["REPO"]
TASK = os.environ.get("TASK_BODY", "")
TITLE = os.environ.get("TASK_TITLE", "Barrot task")
ISSUE = os.environ.get("ISSUE_NUMBER", "")
BRANCH = os.environ.get("BRANCH", "barrot/task")
KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = os.environ.get("BRAIN_MODEL", "").strip() or "llama-3.3-70b-versatile"


def run(cmd, check=True, quiet=False):
    print("+", cmd)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if not quiet:
        if r.stdout.strip():
            print(r.stdout[:3000])
        if r.stderr.strip():
            print(r.stderr[:3000])
    if check and r.returncode != 0:
        sys.exit(f"command failed: {cmd}\n{r.stderr[:1000]}")
    return r.stdout


NOISE_PREFIXES = (".git", ".npm", "node_modules", ".cache", "_cacache")


def repo_inventory(max_files=400):
    files = run("git ls-files", check=False, quiet=True).splitlines()
    files = [f for f in files if not any(f.startswith(p) for p in NOISE_PREFIXES)]
    tree = []
    for f in files[:max_files]:
        try:
            sz = os.path.getsize(f)
        except OSError:
            sz = 0
        tree.append(f"{f} ({sz}b)")
    extra = len(files) - max_files
    if extra > 0:
        tree.append(f"... ({extra} more files omitted)")
    return "\n".join(tree)


def ask_brain(system, user):
    body = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": 4096,
            "temperature": 0.2,
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.load(resp)["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        print(f"[ask_brain] Groq HTTP {e.code}: {body[:600]}")
        sys.exit(f"Groq API error {e.code}: {body[:400]}")


SYSTEM = """You are Barrot-Ω operating as an autonomous repository engineer on your own repo.
You output ONLY JSON, no prose, no fences. Two modes:
1. MOVING/DELETING files: a JSON array of shell commands. Example: ["git mv a.md docs/","mkdir -p docs"]
2. REWRITING/REFORMATTING/REFACTORING a file's CONTENTS: a JSON object:
   {"commands":[...moves/dirs only...],"transmutations":[{"path":"rel/path.py","content":"FULL new file"}]}
   A transmutation replaces the ENTIRE file with content (complete file, not a diff).
   Types: .py .json .jsonl .yml .yaml .md .txt only.
3. REPORTING/AUDITING/ANALYZING with no code change needed: a JSON object:
   {"report":"your findings as plain text"}
   Use this when the task asks you to investigate, audit, or report -- not to modify anything.
CRITICAL: to change what is INSIDE a file, use a transmutation. sed for content editing is
forbidden and will be rejected. Never use 'git add -A'. Never touch .git/. Never modify or
delete files under core/, hf_space/, web/, scripts/emit_signal.py, or .github/workflows/. The sandbox/ directory is your FREE EXPERIMENT ZONE — you may create, edit, and test anything there without restriction; it never affects the real stack."""


def validate_command(cmd):
    """Reject malformed/unsafe commands before execution. Returns (ok, reason)."""
    import shlex, re, os

    stripped = cmd.strip()
    if not stripped:
        return False, "empty command"
    try:
        parts = shlex.split(stripped)
    except ValueError as e:
        return False, f"unparseable shell syntax: {e}"
    if not parts:
        return False, "no tokens"
    verb = parts[0]
    ALLOWED = {"git", "mkdir", "rm", "sed", "mv", "cp", "touch"}
    if verb not in ALLOWED:
        return False, f"disallowed command '{verb}'"
    if verb == "sed":
        script = None
        for x in parts[1:]:
            if x.startswith("-"):
                continue
            script = x
            break
        if script and script.startswith("s"):
            delim = script[1] if len(script) > 1 else ""
            if not delim or delim.isalnum():
                return False, f"malformed sed: bad delimiter in {script!r}"
            body = script[2:]
            count = len(re.findall(r"(?<!\\)" + re.escape(delim), body))
            if count != 2:
                return False, f"malformed sed: expected 2 delimiters, found {count}"
            segs = re.split(r"(?<!\\)" + re.escape(delim), body)
            if segs and segs[0] == "":
                return False, "malformed sed: empty search pattern"
    if verb == "git" and len(parts) >= 4 and parts[1] == "mv":
        if not os.path.exists(parts[2]):
            return False, f"git mv source does not exist: {parts[2]}"
    return True, "ok"


def verify_content(path, content):
    """Verify rewritten content is well-formed for its type. Returns (ok, reason).
    Fails closed: unknown types are not allowed to be rewritten."""
    import ast as _ast, json as _json, os as _os

    ext = _os.path.splitext(path)[1].lower()
    if ext == ".py":
        try:
            _ast.parse(content)
        except SyntaxError as e:
            return False, f"python syntax error line {e.lineno}: {e.msg}"
        return True, "ok"
    if ext == ".json":
        try:
            _json.loads(content)
        except Exception as e:
            return False, f"json parse error: {e}"
        return True, "ok"
    if ext in (".yml", ".yaml"):
        try:
            import yaml

            yaml.safe_load(content)
        except Exception as e:
            return False, f"yaml parse error: {e}"
        return True, "ok"
    if ext == ".jsonl":
        for i, line in enumerate(content.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                _json.loads(line)
            except Exception as e:
                return False, f"jsonl parse error on line {i}: {e}"
        return True, "ok"
    if ext in (".md", ".txt"):
        return True, "ok"  # plain text: nothing to break
    return False, f"no verifier for '{ext}' — rewrite not allowed"


PROTECTED_WRITE = ("core/", "hf_space/", "web/", "scripts/emit_signal.py", ".github/workflows/")


def preservation_check(old_content, new_content, min_retain=0.5):
    """Reject a rewrite that destroyed most original content."""

    def toks(s):
        return set(w for w in s.split() if len(w) > 3)

    old_t = toks(old_content)
    if not old_t:
        return True, "original trivial"
    retained = len(old_t & toks(new_content)) / len(old_t)
    len_ratio = len(new_content) / max(len(old_content), 1)
    if retained < min_retain:
        return False, f"content-loss: only {retained:.0%} of original words retained"
    if len_ratio < 0.3:
        return False, f"content-loss: shrank to {len_ratio:.0%} of size"
    return True, f"preserved {retained:.0%}"


def apply_transmutations(transmutations):
    """Each item: {\"path\": str, \"content\": str}. Verify BEFORE writing.
    Returns list of applied paths. Never writes unverified or protected content."""
    import os as _os

    applied = []
    for t in transmutations:
        path = t.get("path", "")
        content = t.get("content", "")
        if not path or content is None:
            print(f"REJECTED transmute: missing path/content")
            continue
        if any(path.startswith(pp) for pp in PROTECTED_WRITE):
            print(f"REJECTED transmute (protected path): {path}")
            continue
        if ".." in path or path.startswith("/"):
            print(f"REJECTED transmute (unsafe path): {path}")
            continue
        ok, reason = verify_content(path, content)
        if not ok:
            print(f"REJECTED transmute ({reason}): {path}")
            continue
        if os.path.exists(path):
            with open(path) as _f:
                _old = _f.read()
            pok, preason = preservation_check(_old, content)
            if not pok:
                justification = t.get("justification", "").strip()
                if len(justification) >= 40:
                    print(f"OVERRIDE transmute ({preason}) - justified: {path}")
                    print(f"  justification: {justification}")
                else:
                    print(f"REJECTED transmute ({preason}): {path}")
                    continue
        d = _os.path.dirname(path)
        if d:
            _os.makedirs(d, exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        applied.append(path)
        print(f"transmuted: {path}")
    return applied


def main():
    run("git config user.email 'barrot@barrot-agent.com'")
    run("git config user.name 'Barrot-Agent'")
    run(f"git checkout -b {BRANCH}")

    inv = repo_inventory()
    import re as _re

    named = _re.findall(r"[\w./-]+\.(?:py|jsonl|json|ya?ml|md|txt)", f"{TITLE}\n{TASK}")
    file_ctx = ""
    for fp in list(dict.fromkeys(named))[:5]:
        if os.path.exists(fp):
            try:
                with open(fp) as _f:
                    file_ctx += (
                        f"\n=== CURRENT CONTENT OF {fp} ===\n{_f.read()}\n=== END {fp} ===\n"
                    )
            except Exception:
                pass
    # Inject REAL GitHub data when the task is about PRs or issues
    gh_ctx = ""
    tl = f"{TITLE} {TASK}".lower()
    if "pull request" in tl or " pr " in tl or "prs" in tl:
        out = run(
            "gh pr list --repo " + REPO + " --state open --limit 100 "
            "--json number,title,mergeable,additions,deletions,author "
            "-q '.[] | \"#\\(.number) | \\(.mergeable) | +\\(.additions)/-\\(.deletions) | "
            "@\\(.author.login) | \\(.title)\"'",
            check=False,
            quiet=True,
        )
        if out.strip():
            gh_ctx += f"\n=== REAL OPEN PULL REQUESTS (use ONLY these, never invent) ===\n{out[:12000]}\n=== END PRS ===\n"
    # If the task names specific PR numbers, fetch their REAL diffs (not just titles)
    import re as _re2
    pr_nums = _re2.findall(r"#(\d+)", f"{TITLE} {TASK}")
    if pr_nums:
        seen = []
        for _n in dict.fromkeys(pr_nums):
            if len(seen) >= 4:
                break
            d = run(f"gh pr diff {_n} --repo {REPO}", check=False, quiet=True)
            if d.strip():
                # cap each diff so many fit; names/paths/first lines carry the signal
                seen.append(f"--- PR #{_n} DIFF ---\n{d[:1200]}")
        if seen:
            gh_ctx += ("\n=== REAL PR DIFFS (actual file changes — judge ONLY from these, "
                       "never from the title) ===\n" + "\n\n".join(seen) + "\n=== END DIFFS ===\n")
    if "issue" in tl:
        out = run(
            "gh issue list --repo " + REPO + " --state open --limit 100 "
            "--json number,title,author -q '.[] | \"#\\(.number) | \\(.author.login) | \\(.title)\"'",
            check=False,
            quiet=True,
        )
        if out.strip():
            gh_ctx += f"\n=== REAL OPEN ISSUES (use ONLY these, never invent) ===\n{out[:8000]}\n=== END ISSUES ===\n"

    note = ""
    if file_ctx:
        note = (
            "\n\nIMPORTANT: for any file shown above, if reformatting/editing it you MUST return "
            "the FULL file preserving ALL existing information — change only what the task asks. "
            "Do NOT invent new content or drop existing sections."
        )
    if gh_ctx:
        note += (
            "\n\nCRITICAL: the pull requests / issues listed above are the ONLY real ones. "
            "Use their actual numbers, authors, and titles verbatim. NEVER invent placeholder "
            "entries (no 'user1', no 'Fix typo', no '...' rows). If you cannot assess one, say so "
            "for that specific real PR. Every row you write must correspond to a real entry above."
        )
    prompt = (
        f"TASK:\n{TITLE}\n{TASK}\n\n" + ("" if "REAL PR DIFFS" in gh_ctx else f"CURRENT REPO FILES:\n{inv}") + f"{file_ctx}{gh_ctx}{note}"
        f"\n\nOutput JSON (array for moves, or object with transmutations for rewrites)."
    )
    raw = ask_brain(SYSTEM, prompt).strip()

    import re

    obj_a, arr_a = raw.find("{"), raw.find("[")
    if obj_a == -1 and arr_a == -1:
        sys.exit(f"brain returned no JSON:\n{raw[:800]}")
    use_obj = obj_a != -1 and (arr_a == -1 or obj_a < arr_a)
    if use_obj:
        a, b = raw.find("{"), raw.rfind("}")
    else:
        a, b = raw.find("["), raw.rfind("]")
    blob = raw[a : b + 1]
    try:
        data = json.loads(blob)
    except json.JSONDecodeError:
        fixed = re.sub(r'\\(?![\\/"bfnrtu])', r"\\\\", blob)
        try:
            data = json.loads(fixed)
        except json.JSONDecodeError as e:
            sys.exit(f"could not parse brain output ({e}):\n{blob[:800]}")
    if isinstance(data, list):
        cmds, trans = data, []
    else:
        cmds = data.get("commands", []) or []
        trans = data.get("transmutations", []) or []

    report = data.get("report") if isinstance(data, dict) else None
    if report and not cmds and not trans:
        run("git checkout main", check=False)
        run(f"git branch -D {BRANCH}", check=False)
        comment_body = report.replace(chr(34), chr(39))[:60000]
        run(f'gh issue comment {ISSUE} --repo {REPO} --body "{comment_body}"', check=False)
        print("DONE -- report posted as issue comment, no code change needed.")
        sys.exit(0)

    BANNED = [
        "git add -a",
        "git push",
        "rm -rf",
        ".git/",
        "git reset --hard",
        "git checkout main",
        "sed -i",
    ]
    PROTECTED_DEL = ["rm core/", "rm hf_space/", "rm web/", "rm scripts/emit_signal.py"]
    safe = []
    for c in cmds:
        low = c.lower()
        if any(x in low for x in BANNED) or any(p in low for p in PROTECTED_DEL):
            print("REJECTED unsafe command:", c)
            continue
        ok, reason = validate_command(c)
        if not ok:
            print(f"REJECTED malformed command: {c}  ({reason})")
            continue
        safe.append(c)
    if not safe and not trans:
        sys.exit("no safe commands or transmutations produced")

    for c in safe:
        run(c, check=False)

    applied = apply_transmutations(trans) if trans else []
    if applied:
        print(f"Applied {len(applied)} verified transmutations.")

    run("git add -u", check=False)
    run("git add .", check=False)
    if not run("git status --porcelain", check=False).strip():
        sys.exit("no changes produced")

    # SANDBOX SAFETY: verify the resulting working tree before committing.
    # A broken result blocks the PR instead of shipping it.
    sb_ok, sb_report = verify_result(".")
    print(f"[sandbox] verification: {'PASS' if sb_ok else 'FAIL'}")
    if sb_report and sb_report != "clean":
        print(f"[sandbox] {sb_report}")
    if not sb_ok:
        sys.exit("SANDBOX BLOCKED: task produced broken files; no PR opened.")

    summary = "\\n".join(f"- {c}" for c in safe)
    run('git commit -m "Barrot autonomous task: ' + TITLE.replace('"', "'") + '"')
    run(f"git push origin {BRANCH}")

    pr_body = (
        f"Autonomous execution of #{ISSUE} by Barrot.\\n\\nCommands run:\\n{summary}\\n\\n"
        f"Review the diff; apply the approved label to merge protected or large changes."
    )
    run(
        f'gh pr create --repo {REPO} --title "Barrot: {TITLE}" --body "{pr_body}" --head {BRANCH} --base main',
        check=False,
    )
    print("DONE — PR opened, awaiting gate + review.")


if __name__ == "__main__":
    main()
