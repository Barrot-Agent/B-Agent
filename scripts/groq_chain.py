#!/usr/bin/env python3
"""
BARROT-Ω CHAIN-OF-THOUGHT + SELF-CONSISTENCY CLASSIFIER

Real technique, real citations:
- "Chain-of-Thought Prompting Elicits Reasoning in Large Language
  Models" (Wei et al., 2022)
- "Self-Consistency Improves Chain-of-Thought Reasoning in Language
  Models" (Wang et al., 2023)

Replaces a single-shot "bullish/bearish/neutral?" classification with:
1. A step-by-step prompt forcing the model to name the catalyst and
   justify its label before answering.
2. Three independent calls at different temperatures.
3. Majority vote on the label, averaged confidence across agreeing calls.

Standalone and independently testable - not wired into the live signal
pipeline (emit_signal.py) until proven correct on its own. Same output
shape (score, confidence, label) as the existing classifier, so it can
be swapped in as a drop-in replacement later.
"""

import json
import os
from collections import Counter

import requests

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.environ.get("BRAIN_MODEL", "").strip() or "openai/gpt-oss-120b"
KEY = os.environ.get("GROQ_API_KEY", "")

SYSTEM_PROMPT = (
    "You are a careful sentiment classifier for crypto market headlines. "
    "Think step by step, then answer. First identify the real catalyst in "
    "the headline. Then decide if that catalyst is bullish, bearish, or "
    "neutral for the asset. Then give a one-sentence justification tied "
    "specifically to the catalyst you named - not a generic statement.\n\n"
    "Reply with JSON only, no prose, no markdown fences:\n"
    '{"catalyst": "the specific real event/fact from the headline", '
    '"label": "bullish" or "bearish" or "neutral", '
    '"score": integer 0-100 (50=neutral, 100=max bullish, 0=max bearish), '
    '"confidence": float 0-1, '
    '"justification": "one sentence tied to the catalyst"}'
)


def _call_groq(signal_text, temperature):
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Headline: {signal_text}"},
        ],
        "max_tokens": 400,
        "temperature": temperature,
    })
    r = requests.post(
        GROQ_ENDPOINT,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        data=body,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def _parse(raw):
    a, b = raw.find("{"), raw.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("no json in response")
    d = json.loads(raw[a:b + 1])
    label = d.get("label")
    if label not in ("bullish", "bearish", "neutral"):
        raise ValueError(f"invalid label: {label}")
    score = int(max(0, min(100, int(d.get("score", 50)))))
    confidence = float(max(0.0, min(1.0, float(d.get("confidence", 0.5)))))
    return {
        "label": label,
        "score": score,
        "confidence": confidence,
        "catalyst": d.get("catalyst", ""),
        "justification": d.get("justification", ""),
    }


def classify_with_self_consistency(signal_text, n=3, temperatures=(0.2, 0.5, 0.8)):
    """Real self-consistency: n independent calls, majority vote on label,
    average score/confidence across calls that agree with the majority."""
    if not KEY:
        raise RuntimeError("GROQ_API_KEY not set")

    results = []
    for i in range(n):
        temp = temperatures[i % len(temperatures)]
        try:
            raw = _call_groq(signal_text, temp)
            results.append(_parse(raw))
        except Exception as e:
            results.append({"error": str(e)})

    valid = [r for r in results if "error" not in r]
    if not valid:
        return {"label": "neutral", "score": 50, "confidence": 0.0,
                "note": "all classification attempts failed", "raw_results": results}

    label_counts = Counter(r["label"] for r in valid)
    majority_label, vote_count = label_counts.most_common(1)[0]
    agreeing = [r for r in valid if r["label"] == majority_label]

    avg_score = sum(r["score"] for r in agreeing) / len(agreeing)
    avg_confidence = sum(r["confidence"] for r in agreeing) / len(agreeing)
    # confidence penalty when the vote isn't unanimous - real disagreement
    # is itself a signal, not something to hide
    unanimity = vote_count / len(valid)

    return {
        "label": majority_label,
        "score": round(avg_score),
        "confidence": round(avg_confidence * unanimity, 3),
        "vote": f"{vote_count}/{len(valid)}",
        "catalyst": agreeing[0].get("catalyst", ""),
        "justification": agreeing[0].get("justification", ""),
        "raw_results": results,
    }


if __name__ == "__main__":
    import sys
    text = os.environ.get("TEST_HEADLINE") or (sys.argv[1] if len(sys.argv) > 1 else "")
    if not text:
        sys.exit("Provide a headline via TEST_HEADLINE env var or argv[1]")
    result = classify_with_self_consistency(text)
    print(json.dumps(result, indent=2))
