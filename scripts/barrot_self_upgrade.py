#!/usr/bin/env python3
"""Barrot self-upgrade: identify capability gaps, generate new modules, test, commit."""
import os, json, subprocess, urllib.request, sys
from pathlib import Path
from datetime import datetime

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
REPO_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"

BANNED_TERMS = ["rm -rf", ".git/", "git reset --hard", "sed -i", "quantum_entanglement", "free_energy"]

def load_audit():
    """Load the latest capability audit."""
    audit_file = REPO_ROOT / "barrot_capability_audit.json"
    if audit_file.exists():
        with open(audit_file) as f:
            return json.load(f)
    return None

def call_groq(prompt):
    body = json.dumps({
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.5,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.load(resp)["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq error: {e}")
        return ""

def generate_capability(gap_id, gap_name):
    """Generate code for a missing capability."""
    prompt = f"""Barrot identified a capability gap: {gap_name} (ID: {gap_id})

Generate a complete, working Python script that implements this capability.
Requirements:
1. Use urllib for HTTP (no external libs except json/os/sys)
2. Call Groq openai/gpt-oss-120b for analysis
3. Output JSON results to a file
4. Include error handling
5. DO NOT include: rm commands, git reset, sed -i, or any destructive operations
6. DO NOT reference non-existent hardware or APIs

Output ONLY valid Python code, no explanation. Start with shebang."""
    
    code = call_groq(prompt)
    
    # Verify no banned terms
    for term in BANNED_TERMS:
        if term in code:
            print(f"REJECTED: banned term '{term}' found in generated code")
            return None
    
    return code

def test_capability(code):
    """Syntax-check the generated capability."""
    test_file = "/tmp/barrot_capability_test.py"
    with open(test_file, "w") as f:
        f.write(code)
    
    result = subprocess.run(
        ["python3", "-m", "py_compile", test_file],
        capture_output=True
    )
    
    if result.returncode == 0:
        print(f"✓ Syntax OK")
        return True
    else:
        print(f"✗ Syntax error: {result.stderr.decode()}")
        return False

def commit_capability(capability_name, code):
    """Commit new capability to main."""
    script_path = SCRIPTS_DIR / f"{capability_name.lower().replace(' ', '_')}.py"
    
    with open(script_path, "w") as f:
        f.write(code)
    
    subprocess.run(["git", "add", str(script_path)], cwd=REPO_ROOT, check=False)
    subprocess.run(
        ["git", "commit", "-m", f"Self-upgrade: {capability_name}"],
        cwd=REPO_ROOT,
        check=False
    )
    subprocess.run(["git", "push"], cwd=REPO_ROOT, check=False)
    
    print(f"✓ Committed: {script_path}")

def self_upgrade():
    """Full self-upgrade cycle."""
    audit = load_audit()
    if not audit or not audit.get("gaps"):
        print("No capability gaps found")
        return
    
    top_gap = audit["gaps"][0]
    gap_id, gap_name = top_gap["id"], top_gap["name"]
    
    print(f"Upgrading: {gap_name} (ID: {gap_id})")
    
    code = generate_capability(gap_id, gap_name)
    if not code:
        print("Failed to generate capability")
        return
    
    if not test_capability(code):
        print("Capability failed syntax check")
        return
    
    commit_capability(gap_name, code)
    print(f"✓ Self-upgrade complete: {gap_name}")

if __name__ == "__main__":
    if not GROQ_KEY:
        print("GROQ_API_KEY not set")
        sys.exit(1)
    self_upgrade()
