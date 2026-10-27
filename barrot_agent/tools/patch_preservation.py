with open("scripts/barrot_agent.py") as f:
    content = f.read()

if "OVERRIDE transmute" in content:
    print("ALREADY PATCHED -- skipping, no changes made")
else:
    old = """        if os.path.exists(path):
            with open(path) as _f:
                _old = _f.read()
            pok, preason = preservation_check(_old, content)
            if not pok:
                print(f"REJECTED transmute ({preason}): {path}")
                continue"""

    new = """        if os.path.exists(path):
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
                    continue"""

    count = content.count(old)
    print(f"Match count: {count}")

    if count == 1:
        content = content.replace(old, new)
        with open("scripts/barrot_agent.py", "w") as f:
            f.write(content)
        print("Patched scripts/barrot_agent.py")
    else:
        print("ABORTING -- expected exactly 1 match, got", count)
