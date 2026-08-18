with open("scripts/barrot_agent.py") as f:
    content = f.read()

if '"report"' in content:
    print("ALREADY PATCHED -- skipping, no changes made")
else:
    old1 = """2. REWRITING/REFORMATTING/REFACTORING a file's CONTENTS: a JSON object:
   {"commands":[...moves/dirs only...],"transmutations":[{"path":"rel/path.py","content":"FULL new file"}]}
   A transmutation replaces the ENTIRE file with content (complete file, not a diff).
   Types: .py .json .jsonl .yml .yaml .md .txt only.
CRITICAL:"""

    new1 = """2. REWRITING/REFORMATTING/REFACTORING a file's CONTENTS: a JSON object:
   {"commands":[...moves/dirs only...],"transmutations":[{"path":"rel/path.py","content":"FULL new file"}]}
   A transmutation replaces the ENTIRE file with content (complete file, not a diff).
   Types: .py .json .jsonl .yml .yaml .md .txt only.
3. REPORTING/AUDITING/ANALYZING with no code change needed: a JSON object:
   {"report":"your findings as plain text"}
   Use this when the task asks you to investigate, audit, or report -- not to modify anything.
CRITICAL:"""

    old2 = """    if isinstance(data, list):
        cmds, trans = data, []
    else:
        cmds = data.get("commands", []) or []
        trans = data.get("transmutations", []) or []"""

    new2 = """    if isinstance(data, list):
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
        sys.exit(0)"""

    c1, c2 = content.count(old1), content.count(old2)
    print(f"Match 1: {c1}, Match 2: {c2}")

    if c1 == 1 and c2 == 1:
        content = content.replace(old1, new1).replace(old2, new2)
        with open("scripts/barrot_agent.py", "w") as f:
            f.write(content)
        print("Patched scripts/barrot_agent.py")
    else:
        print("ABORTING -- expected exactly 1 match each")
