#!/usr/bin/env python3
"""
BARROT-Ω FINANCIAL DATA REFRESH — keeps the financial literacy
curriculum's dollar figures current automatically, instead of letting
them go stale in generated content (real bug caught: Barrot's first
curriculum draft used ~2-year-old contribution limits).

Real source: IRS's own evergreen COLA reference page, which the IRS
updates in place each year rather than publishing under a new dated
URL - this is what makes automated re-checking actually reliable
long-term, unlike the year-specific news-release URLs.

Extraction is grounded strictly in the real fetched page text via
Groq - the prompt explicitly forbids inventing any figure not present
in the fetched content. Output includes the raw source excerpt
alongside the structured figures so anything downstream (or a human)
can cross-check before using a number in real curriculum copy.

Known gap, not yet covered: HSA limits come from a separate IRS
Revenue Procedure with its own page - not yet wired in. Retirement
account figures (401k/IRA/Roth/SIMPLE) are the real, current scope.
"""

import json
import os
import time
import urllib.request

KB_DIR = "ping-pongings/knowledge-base"
OUT_PATH = os.path.join(KB_DIR, "financial_data.json")

SOURCE_URL = "https://www.irs.gov/retirement-plans/cola-increases-for-dollar-limitations-on-benefits-and-contributions"

KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = os.environ.get("BRAIN_MODEL", "").strip() or "openai/gpt-oss-120b"

EXTRACTION_PROMPT_TEMPLATE = """Below is real text fetched directly from the IRS's own official page on retirement contribution limits. Extract the CURRENT year's real figures ONLY from what is shown - do not use prior knowledge, do not invent any number not present in this text. If a figure isn't present in the text, use null rather than guessing.

Real fetched IRS page text:
---
{page_text}
---

Reply with JSON only, no prose:
{{
  "tax_year": <the current year these figures apply to, as an integer, or null>,
  "401k_employee_limit": <dollar amount as integer, or null>,
  "401k_catchup_50plus": <dollar amount as integer, or null>,
  "401k_catchup_60to63": <dollar amount as integer, or null>,
  "ira_limit": <dollar amount as integer, or null>,
  "ira_catchup_50plus": <dollar amount as integer, or null>,
  "roth_ira_phaseout_single_low": <dollar amount as integer, or null>,
  "roth_ira_phaseout_single_high": <dollar amount as integer, or null>,
  "roth_ira_phaseout_married_low": <dollar amount as integer, or null>,
  "roth_ira_phaseout_married_high": <dollar amount as integer, or null>,
  "simple_limit": <dollar amount as integer, or null>,
  "notes": "<any other real figures worth capturing, in one sentence, or empty string>"
}}"""


def fetch_source():
    req = urllib.request.Request(
        SOURCE_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode("utf-8", errors="ignore")
    return raw


def strip_html(raw):
    """Crude tag stripping - good enough for feeding to the LLM, which
    doesn't need clean formatting, just the real text content."""
    import re
    text = re.sub(r"<script[\s\S]*?</script>", " ", raw)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def ask_groq(prompt):
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500,
        "temperature": 0.0,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def parse_json_response(raw):
    a, b = raw.find("{"), raw.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("no json in response")
    return json.loads(raw[a:b + 1])


def main():
    if not KEY:
        raise SystemExit("GROQ_API_KEY not set")

    print(f"Fetching real source: {SOURCE_URL}")
    raw_html = fetch_source()
    page_text = strip_html(raw_html)[:8000]

    print(f"Fetched {len(page_text)} chars of real page text")
    print(f"First 300 chars: {page_text[:300]!r}")

    print("Extracting figures via Groq, grounded strictly in fetched text...")
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(page_text=page_text)
    raw_response = ask_groq(prompt)
    print(f"Raw Groq response ({len(raw_response)} chars): {raw_response[:500]!r}")
    figures = parse_json_response(raw_response)

    out = {
        "source_url": SOURCE_URL,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "figures": figures,
        "raw_source_excerpt": page_text[:2000],
        "note": (
            "Extracted from a real, live fetch of the IRS's own evergreen "
            "COLA page - not from static/training-data knowledge. Cross-check "
            "raw_source_excerpt before using any figure in published "
            "curriculum copy - LLM extraction can still err even when "
            "grounded in real source text."
        ),
    }

    os.makedirs(KB_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"\nExtracted figures: {json.dumps(figures, indent=2)}")
    print(f"\nWritten to {OUT_PATH}")


if __name__ == "__main__":
    main()
