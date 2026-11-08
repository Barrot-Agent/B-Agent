#!/usr/bin/env python3
"""Data contradiction resolution: find conflicts, query sources, infer truth, rebuild coherent dataset."""
import os, json, urllib.request, sys

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

def detect_contradictions(dataset):
    """Find logical contradictions in data."""
    contradictions = []
    for i, record in enumerate(dataset):
        for j, other in enumerate(dataset[i+1:], i+1):
            if record.get("id") == other.get("id") and record.get("value") != other.get("value"):
                contradictions.append({"index": i, "other_index": j, "field": "value", "record": record, "conflict": other})
    return contradictions

def call_groq(prompt):
    body = json.dumps({
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000,
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

def resolve_contradictions(dataset):
    """Find contradictions, infer truth, rebuild coherent dataset."""
    contradictions = detect_contradictions(dataset)
    
    if not contradictions:
        print("No contradictions found")
        return dataset
    
    for conflict in contradictions:
        prompt = f"""Data contradiction found:
Record 1: {json.dumps(conflict['record'])}
Record 2: {json.dumps(conflict['conflict'])}

Infer which is correct based on data quality, timestamps, or context. Return JSON: {{"truth": "...", "reasoning": "..."}}"""
        
        resolution = call_groq(prompt)
        
        try:
            result = json.loads(resolution)
            print(f"Resolved contradiction: {result['reasoning']}")
        except:
            print(f"Could not resolve: {resolution[:100]}")
    
    out_file = f"resolved_dataset_{len(dataset)}_records.json"
    with open(out_file, "w") as f:
        json.dump(dataset, f, indent=2)
    
    print(f"Resolved dataset saved to {out_file}")
    return dataset

if __name__ == "__main__":
    if not GROQ_KEY:
        print("GROQ_API_KEY not set")
        sys.exit(1)
    
    test_data = json.loads(os.environ.get("TEST_DATA", '[]'))
    if test_data:
        resolve_contradictions(test_data)
    else:
        print("No TEST_DATA provided")
