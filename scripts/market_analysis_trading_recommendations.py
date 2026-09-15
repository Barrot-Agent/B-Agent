#!/usr/bin/env python3
"""
Market analysis + trading recommendations (gap ID 1)

This script:
- Reads the GROQ_API_KEY environment variable.
- Sends a prompt to the Groq chat completion API using only the standard library.
- Writes the AI‑generated analysis and recommendations to a JSON file.
- If any required data cannot be obtained, the corresponding fields are set to null.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "mixtral-8x7b-32768"  # Example Groq model; adjust if needed
OUTPUT_FILE = Path("market_analysis.json")

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def fatal(msg: str) -> None:
    """Print an error message to stderr and exit with a non‑zero status."""
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def get_groq_api_key() -> str:
    """Retrieve the Groq API key from the environment."""
    key = os.getenv("GROQ_API_KEY")
    if not key:
        fatal("GROQ_API_KEY environment variable is not set.")
    return key


def call_groq(api_key: str, prompt: str) -> str:
    """Send a chat completion request to Groq and return the assistant's reply."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a concise financial analyst."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 1024,
    }

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request) as resp:
            resp_data = resp.read().decode("utf-8")
            resp_json = json.loads(resp_data)
            # Extract the assistant's message content
            return resp_json["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        # Return a clear error message instead of raising
        return f"[HTTP error {e.code}: {e.reason}]"
    except urllib.error.URLError as e:
        return f"[URL error: {e.reason}]"
    except Exception as e:
        return f"[Unexpected error: {str(e)}]"


def build_prompt() -> str:
    """Create the prompt sent to Groq."""
    return (
        "Provide a concise market analysis for the major U.S. equity indices (S&P 500, Nasdaq, Dow Jones) "
        "and give up to three short‑term trading recommendations (entry, stop‑loss, target). "
        "If you need recent price data, acknowledge that you do not have live data and base your answer on general market conditions."
    )


def write_output(result: dict) -> None:
    """Write the result dictionary to the JSON output file."""
    try:
        with OUTPUT_FILE.open("w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except Exception as e:
        fatal(f"Failed to write output file: {e}")


# ----------------------------------------------------------------------
# Main execution flow
# ----------------------------------------------------------------------
def main() -> None:
    api_key = get_groq_api_key()
    prompt = build_prompt()
    analysis_text = call_groq(api_key, prompt)

    # Build the final JSON structure
    result = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "analysis": analysis_text if analysis_text else None,
        # No real market data was fetched; explicitly mark as unavailable
        "market_data": None,
        # The raw content may contain both analysis and recommendations;
        # callers can parse as needed.
        "raw_content": analysis_text,
    }

    write_output(result)
    print(f"Market analysis written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()