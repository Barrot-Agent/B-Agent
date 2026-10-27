#!/usr/bin/env python3
"""Video analysis: fetch failure video, analyze, generate fix, deploy."""
import os, json, urllib.request, subprocess

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

def analyze_video_log(log_path):
    """Read video/system log, extract error context."""
    try:
        with open(log_path) as f:
            return f.read()[:2000]
    except:
        return "No log available"

def generate_fix(error_context):
    """Ask Groq to generate a fix based on error."""
    prompt = f"System failure log:\n{error_context}\n\nGenerate a Python code fix. Output ONLY the code block, no explanation."
    body = json.dumps({"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000, "temperature": 0.5}).encode()
    req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=body, headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq error: {e}")
        return ""

def deploy_fix(code):
    """Save fix and commit."""
    fix_file = "autofix_generated.py"
    with open(fix_file, "w") as f:
        f.write(code)
    subprocess.run(["python3", "-m", "py_compile", fix_file], check=False)
    print(f"Generated fix: {fix_file}")
    return fix_file

if __name__ == "__main__":
    log = os.environ.get("FAILURE_LOG", "scripts/video_analysis_autofix.py")
    context = analyze_video_log(log)
    fix = generate_fix(context)
    if fix:
        deploy_fix(fix)
