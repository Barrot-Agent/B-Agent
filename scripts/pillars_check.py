#!/usr/bin/env python3
"""Pillars consistency check for external service availability and repository source.
The GitHub/HF source checks inspect GitHub main; only the HF stage check probes
the deployed Space runtime. This script does not verify deployed source parity
or claim repository source checks establish the live SYSTEM_PROMPT."""
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
    # Verify the app installation with a read-only endpoint. Do not mint an
    # installation access token merely to run a scheduled health check.
    r = requests.get(f"https://api.github.com/app/installations/{inst}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}, timeout=15)
    return r.status_code == 200, f"HTTP {r.status_code}"

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
    if r.status_code != 200:
        return False, f"HTTP {r.status_code}"
    try:
        payload = r.json()
        if not isinstance(payload, dict):
            return False, "invalid runtime response: expected object"
        stage = payload.get("stage", "unknown")
        return stage == "RUNNING", f"stage={stage}"
    except Exception as e:
        return False, f"parse error: {e}"

def check_repo_source_marker():
    """Checks a marker in GitHub main source; it does not verify the deployed Space revision."""
    r = requests.get("https://api.github.com/repos/Barrot-Agent/B-Agent/contents/hf_space/app.py", timeout=15)
    if r.status_code != 200:
        return False, f"HTTP {r.status_code}"
    content = base64.b64decode(r.json()["content"]).decode()
    ok = "Barrot-Ω" in content
    return ok, "GitHub main source marker present; deployed Space revision not checked"

def check_repo_source_fiction():
    """Scans GitHub main source, not the deployed Hugging Face runtime."""
    r = requests.get("https://raw.githubusercontent.com/Barrot-Agent/B-Agent/main/hf_space/app.py", timeout=15)
    if r.status_code != 200:
        return False, f"HTTP {r.status_code}"
    text = r.text
    KNOWN_SAFE = ["mrp_label AS signal_label"]  # real DB column, aliased not renamed
    scan_text = text
    for safe in KNOWN_SAFE:
        scan_text = scan_text.replace(safe, "")
    hits = [t for t in FICTION_TERMS if t.lower() in scan_text.lower()]
    detail = "GitHub main source clean; deployed runtime not inspected"
    return len(hits) == 0, (detail if not hits else f"fiction terms present in GitHub main hf_space/app.py: {hits}")

CHECKS = [
    ("github_app", check_github),
    ("databricks", check_databricks),
    ("hf_space", check_hf_space),
    ("repo_source_marker", check_repo_source_marker),
    ("repo_source_fiction", check_repo_source_fiction),
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
