#!/usr/bin/env python3
"""
Market analysis + trading recommendations (gap ID 1)

This script:
  1. Reads the GROQ_API_KEY from the environment (exits non‑zero if missing).
  2. Accepts an optional list of ticker symbols on the command line.
  3. Sends a prompt to the Groq API (via urllib) asking for a concise market
     analysis and trading recommendations for the supplied tickers.
  4. Writes the API response (or explicit null/unavailable markers) to a JSON
     file whose path is supplied as the first positional argument.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama3-70b-8192"
TEMPERATURE = 0.7

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def fatal(msg: str, code: int = 1) -> None:
    """Print an error message to stderr and exit."""
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def read_api_key() -> str:
    """Fetch GROQ_API_KEY from the environment or abort."""
    key = os.getenv("GROQ_API_KEY")
    if not key:
        fatal("Environment variable GROQ_API_KEY is not set.")
    return key


def build_prompt(tickers):
    """Create the prompt sent to Groq."""
    if not tickers:
        return (
            "Provide a concise market analysis and trading recommendations. "
            "No ticker symbols were supplied, so indicate that the required "
            "input data is unavailable."
        )
    tickers_str = ", ".join(tickers)
    return (
        f"Provide a concise market analysis and trading recommendations for the "
        f"following ticker symbols: {tickers_str}. "
        "Return the answer in plain text, without any markdown formatting."
    )


def call_groq(api_key: str, prompt: str) -> str:
    """Send a chat completion request to Groq and return the assistant's content."""
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        GROQ_ENDPOINT,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_data = resp.read().decode("utf-8")
            resp_json = json.loads(resp_data)
            # Expected structure: {"choices": [{"message": {"content": "..."} }], ...}
            choices = resp_json.get("choices")
            if not choices:
                raise ValueError("No choices returned in Groq response.")
            content = choices[0].get("message", {}).get("content")
            if content is None:
                raise ValueError("Missing content in Groq response.")
            return content.strip()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Groq API HTTP error {e.code}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Groq API connection error: {e.reason}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to decode Groq response as JSON: {e}") from e


def write_output(output_path: Path, result: dict) -> None:
    """Write the result dictionary to the given path as pretty‑printed JSON."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    except OSError as e:
        fatal(f"Failed to write output file '{output_path}': {e}", code=2)


# --------------------------------------------------------------------------- #
# Main execution
# --------------------------------------------------------------------------- #
def main():
    if len(sys.argv) < 2:
        fatal(
            "Usage: market_analysis.py <output_json_path> [ticker1 ticker2 ...]",
            code=1,
        )

    output_path = Path(sys.argv[1])

    # Remaining arguments are treated as ticker symbols (optional)
    tickers = sys.argv[2:] if len(sys.argv) > 2 else None
    if tickers == []:
        tickers = None  # Normalize empty list to None

    api_key = read_api_key()
    prompt = build_prompt(tickers)

    result = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "tickers": tickers if tickers is not None else None,
        "analysis": None,
        "error": None,
    }

    try:
        response_text = call_groq(api_key, prompt)
        result["analysis"] = response_text
    except Exception as exc:
        result["analysis"] = None
        result["error"] = str(exc)

    write_output(output_path, result)


if __name__ == "__main__":
    main()