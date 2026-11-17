"""PHOENIX Level 2 hypothesis: 8 x 12 gist slots at a 96-word budget.

Run by ``barrot_agent.sandbox.SandboxRunner`` in a disposable directory.  The
runner copies this script, ``gist_memory.py`` and ``input.json`` into the run
directory; the script imports the copied module (the code under test is frozen
for the duration of the run).

Hypothesis: at a fixed 96-word budget, 8 slots x 12 words preserves every
long-context test fact that the current 16 x 10 default keeps, while 16 slots x
6 words loses a measurement.

Pass condition:
* wide (8 x 12) recall is 1.0;
* wide recall is at least current (16 x 10) recall;
* wide uses fewer words than current.

The narrow (16 x 6) result is recorded as the width-effect observation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from gist_memory import GistMemory  # noqa: E402  (copied module, not the package)


def measure(documents: list[str], questions: list[dict], slots: int, words: int) -> dict:
    memory = GistMemory(num_memories=slots, words_per_token=words)
    matched = 0
    total = 0
    gist_words = 0
    prompt_chars = 0
    missing: list[str] = []
    per_question = []
    for question in questions:
        result = memory.compress(documents, question.get("question", ""))
        prompt = result.render().lower()
        gist_words += result.words
        prompt_chars += len(prompt)
        found = []
        absent = []
        for term in question.get("expect", []):
            total += 1
            if term.lower() in prompt:
                matched += 1
                found.append(term)
            else:
                absent.append(term)
                missing.append(term)
        per_question.append(
            {
                "id": question.get("id", ""),
                "matched": found,
                "missing": absent,
                "words": result.words,
                "prompt_chars": len(prompt),
            }
        )
    return {
        "slots": slots,
        "words_per_slot": words,
        "budget_words": slots * words,
        "recall": round(matched / total, 4) if total else 0.0,
        "matched": matched,
        "total": total,
        "gist_words": gist_words,
        "prompt_chars": prompt_chars,
        "missing": missing,
        "per_question": per_question,
    }


def main() -> int:
    payload = json.loads((ROOT / "input.json").read_text(encoding="utf-8"))
    documents = payload["documents"]
    questions = payload["questions"]

    current = measure(documents, questions, 16, 10)
    wide = measure(documents, questions, 8, 12)
    narrow = measure(documents, questions, 16, 6)

    passed = (
        wide["recall"] == 1.0
        and wide["recall"] >= current["recall"]
        and wide["gist_words"] < current["gist_words"]
    )
    result = {
        "hypothesis": payload.get("hypothesis", ""),
        "passed": passed,
        "metrics": {
            "documents": len(documents),
            "questions": len(questions),
            "current_16x10": current,
            "wide_8x12": wide,
            "narrow_16x6": narrow,
            "width_effect_observed": narrow["recall"] < wide["recall"],
            "word_saving": current["gist_words"] - wide["gist_words"],
        },
    }
    (ROOT / "result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["metrics"], indent=2, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
