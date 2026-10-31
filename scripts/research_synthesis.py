#!/usr/bin/env python3
"""Research synthesis: fetch papers, analyze via Groq, generate PDF report."""
import os, json, urllib.request, subprocess
from datetime import datetime

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

def search_arxiv(query, max_results=10):
    """Fetch papers from arXiv."""
    url = f"http://export.arxiv.org/api/query?search_query={urllib.parse.quote(query)}&start=0&max_results={max_results}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.read().decode()
    except Exception as e:
        print(f"arXiv error: {e}")
        return ""

def call_groq(prompt):
    body = json.dumps({"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1500, "temperature": 0.7}).encode()
    req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=body, headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq error: {e}")
        return ""

def synthesize(query):
    arxiv_data = search_arxiv(query, 5)
    synthesis_prompt = f"Analyze these research papers on '{query}' and synthesize a summary of novel findings, methods, and implications:\n{arxiv_data[:2000]}"
    analysis = call_groq(synthesis_prompt)
    
    out_file = f"research_synthesis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(out_file, "w") as f:
        f.write(f"# Research Synthesis: {query}\n\n{analysis}\n")
    
    print(f"Saved to {out_file}")
    return out_file

if __name__ == "__main__":
    query = os.environ.get("RESEARCH_QUERY", "AI agents autonomous decision-making")
    synthesize(query)
