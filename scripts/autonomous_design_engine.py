#!/usr/bin/env python3
"""Autonomous design: given requirements and constraints, design system, justify trade-offs, implement."""
import os, json, urllib.request, sys
from datetime import datetime

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

def call_groq(prompt):
    body = json.dumps({
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.7,
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

def design_system(requirements, constraints):
    """Design a system given incomplete requirements and competing constraints."""
    prompt = f"""Requirements: {json.dumps(requirements)}
Constraints: {json.dumps(constraints)}

Design a system. Address:
1. Architecture (components, interactions)
2. Trade-offs (performance vs cost, speed vs reliability, etc)
3. Implementation priorities (what first, why)
4. Adaptation strategy (how to respond to real usage)

Output JSON: {{"architecture": "...", "tradeoffs": [...], "implementation_plan": [...], "adaptation": "..."}}"""
    
    response = call_groq(prompt)
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        design = json.loads(response[start:end])
    except:
        design = {"architecture": response[:500], "tradeoffs": [], "implementation_plan": [], "adaptation": ""}
    
    return design

def implement_design(design):
    """Generate code stubs for the designed system."""
    prompt = f"""System design: {json.dumps(design)[:1000]}

Generate Python code stubs for the core components. Output ONLY valid Python code, no explanation."""
    
    response = call_groq(prompt)
    return response

if __name__ == "__main__":
    if not GROQ_KEY:
        print("GROQ_API_KEY not set")
        sys.exit(1)
    
    requirements = json.loads(os.environ.get("REQUIREMENTS", '{"goal": "low-latency data pipeline", "scale": "1M events/sec"}'))
    constraints = json.loads(os.environ.get("CONSTRAINTS", '{"budget": "$50K", "team": "2 engineers", "timeline": "3 months"}'))
    
    design = design_system(requirements, constraints)
    
    out_file = f"autonomous_design_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_file, "w") as f:
        json.dump({
            "requirements": requirements,
            "constraints": constraints,
            "design": design,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"Design complete: {out_file}")
