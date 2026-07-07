#!/usr/bin/env python3
import os, json, time
from datetime import datetime, timezone

def health():
    token = bool((os.getenv("GITHUB_TOKEN","").strip() or os.getenv("GH_MODELS_TOKEN","").strip()))
    groq = bool(os.getenv("GROQ_API_KEY","").strip())
    model = os.getenv("GITHUB_MODEL","google/gemma-3-12b-it")
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "github_token_present": token,
        "groq_key_present": groq,
        "github_model": model,
        "provider_order": ["github","groq"],
        "status": "ready" if (token or groq) else "waiting_for_secrets"
    }

if __name__ == "__main__":
    os.makedirs("web", exist_ok=True)
    out = health()
    with open("web/backend_health.json","w",encoding="utf-8") as f:
        json.dump(out,f,indent=2)
    print(json.dumps(out))
