#!/usr/bin/env python3
"""Market analysis: pull data from Databricks, analyze via Groq, generate trading recommendations."""
import os, json, urllib.request, sys
from datetime import datetime

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST", "dbc-82d64fee-1c2e.cloud.databricks.com")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN", "")

def query_databricks(query):
    """Execute SQL query on Databricks, return results."""
    body = json.dumps({"sql": query}).encode()
    req = urllib.request.Request(
        f"https://{DATABRICKS_HOST}/api/2.0/sql/statements",
        data=body,
        headers={
            "Authorization": f"Bearer {DATABRICKS_TOKEN}",
            "Content-Type": "application/json"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)
    except Exception as e:
        print(f"Databricks error: {e}")
        return None

def call_groq(prompt):
    body = json.dumps({
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500,
        "temperature": 0.5,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq error: {e}")
        return ""

def analyze_market():
    """Pull last 30 days of signal data, analyze trends, recommend actions."""
    query = "SELECT date, direction, confidence, accuracy FROM workspace.barrot.signals ORDER BY date DESC LIMIT 30"
    
    data = query_databricks(query)
    if not data:
        print("Failed to fetch Databricks data")
        sys.exit(1)
    
    analysis_prompt = f"""Market data (last 30 days):
{json.dumps(data, indent=2)[:1500]}

Analyze this trading signal history. Identify:
1. Trend patterns (is accuracy improving/degrading?)
2. Confidence vs accuracy correlation
3. Specific actionable trades within pre-approved limits ($5M total, max $500K per trade)
4. Risk assessment and failure modes

Output JSON: {{"analysis": "...", "recommendations": [...], "confidence_score": 0.0-1.0}}"""
    
    analysis = call_groq(analysis_prompt)
    
    out_file = f"market_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_file, "w") as f:
        f.write(analysis)
    
    print(f"Analysis saved to {out_file}")
    return out_file

if __name__ == "__main__":
    if not GROQ_KEY:
        print("GROQ_API_KEY not set")
        sys.exit(1)
    analyze_market()
