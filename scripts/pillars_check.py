#!/usr/bin/env python3
"""Pillars consistency check — verifies GitHub/Databricks/HF/deploy pillars
match reality, and flags fiction vocabulary leaking into the live
SYSTEM_PROMPT the chat brain uses to describe itself."""
import os, re, json, sys, base64, time
import requests

FICTION_TERMS = [
    "Fractal Sovereign", "Quantum Assimilation", "$130.8M", "144-agent council",
    "Willowchip", "Aethel", "Loihi", "Planck-scale", "quantum harmonization",
    "free energy", "NotebookLM-as-runtime", "SHRM v2", "SEANIFOLD_GLYPH",
    "Cognition Fusion Directive", "Hermetic synthesis", "bio-computing",
    "quantum chronodynamics", "Sovereign Absolution", "Apex-12",
    "MRP", "MMIP", "RIAP",
]

def check_github():
    app_id, priv, inst = os.getenv("GITHUB_APP_ID"), os.getenv("GITHUB_APP_PRIVATE_KEY"), os.getenv("GITHUB_INSTALLATION_ID")
    if not (app_id and priv and inst):
        return False, "missing GITHUB_APP_ID/PRIVATE_KEY/INSTALLATION_ID"
    import jwt
    now = int(time.time())
    token = jwt.encode({"iat": now - 60, "exp": now + 300, "iss": app_id}, priv, algorithm="RS256")
    r = requests.post(f"https://api.github.com/app/installations/{inst}/access_tokens",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}, timeout=15)
    return r.status_code == 201, f"HTTP {r.status_code}"

def check_databricks():
    host, token, wh = os.getenv("DATABRICKS_HOST"), os.getenv("DATABRICKS_TOKEN"), os.getenv("DATABRICKS_WAREHOUSE_ID")
    if not (host and token and wh):
        return False, "missing DATABRICKS_HOST/TOKEN/WAREHOUSE_ID"
    r = requests.post(f"https://{host}/api/2.0/sql/statements",
        headers={"Authorization": f"Bearer {token}"},
        json={"warehouse_id": wh, "statement": "SELECT 1", "wait_timeout": "10s"}, timeout=20)
    return r.status_code == 200, f"HTTP {r.status_code}"

def check_hf_space():
    r = requests.get("https://huggingface.co/api/spaces/Scribedpengenius/Barrot-Omega/runtime", timeout=20)
    try:
        stage = r.json().get("stage", "unknown")
        return stage == "RUNNING", f"stage={stage}"
    except Exception as e:
        return False, f"parse error: {e}"

def check_deploy_sync():
    r = requests.get("https://api.github.com/repos/Barrot-Agent/B-Agent/contents/hf_space/app.py", timeout=15)
    if r.status_code != 200:
        return False, f"HTTP {r.status_code}"
    content = base64.b64decode(r.json()["content"]).decode()
    return "Barrot-\u03a9" in content, "checked main branch hf_space/app.py"

def check_system_prompt_fiction():
    r = requests.get("https://raw.githubusercontent.com/Barrot-Agent/B-Agent/main/hf_space/app.py", timeout=15)
    m = re.search(r'SYSTEM_PROMPT = f?"""(.*?)"""', r.text, re.S)
    prompt = m.group(1) if m else ""
    hits = [t for t in FICTION_TERMS if t.lower() in prompt.lower()]
    return len(hits) == 0, ("clean" if not hits else f"fiction terms present: {hits}")

CHECKS = [
    ("github_app", check_github),
    ("databricks", check_databricks),
    ("hf_space", check_hf_space),
    ("deploy_sync", check_deploy_sync),
    ("system_prompt_fiction", check_system_prompt_fiction),
]

if __name__ == "__main__":
    all_ok = True
    for name, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, f"exception: {e}"
        all_ok &= ok
        print(f"[{'OK' if ok else 'FAIL'}] {name}: {detail}")
    sys.exit(0 if all_ok else 1)
