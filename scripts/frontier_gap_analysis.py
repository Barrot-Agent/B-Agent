import json
import os
from pathlib import Path

# Hardcoded current stack configuration (manually maintained)
CURRENT_STACK = {
    "inference": ["Groq", "openai/gpt-oss-120b"],
    "image_gen": ["HF ZeroGPU black-forest-labs/FLUX.1-dev", "HF ZeroGPU yanze/PuLID-FLUX"]
}

# Paths to knowledge‑base files
KB_ROOT = Path(__file__).resolve().parents[2] / "ping-pongings" / "knowledge-base"
FRONTIER_LOG = KB_ROOT / "frontier_log.jsonl"
BENCHMARK_LOG = KB_ROOT / "benchmark_log.jsonl"
UPGRADE_RECS = KB_ROOT / "upgrade_recommendations.jsonl"

# Simple heuristic keywords for free/low‑cost options
FREE_KEYWORDS = [
    "free tier",
    "free model",
    "free inference",
    "low cost",
    "zero gpu",
    "zero‑gpu",
    "zero gpu",
    "open source",
    "community model",
    "public api",
    "no cost",
    "gratis",
]

def load_jsonl(path: Path):
    """Yield each JSON object from a .jsonl file."""
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

def entry_mentions_free_option(entry: dict) -> bool:
    """Return True if the entry text contains any free‑tier keyword.
    The entry is expected to have a 'content' or 'summary' field; fallback to the whole dict.
    """
    text = ""
    for key in ("content", "summary", "title", "description"):
        if key in entry and isinstance(entry[key], str):
            text += entry[key].lower() + " "
    # If no explicit field, stringify the entry
    if not text:
        text = json.dumps(entry).lower()
    return any(kw in text for kw in FREE_KEYWORDS)

def entry_targets_current_component(entry: dict) -> bool:
    """Check if the entry mentions any component from CURRENT_STACK.
    Simple string containment check (case‑insensitive).
    """
    text = json.dumps(entry).lower()
    for comp_list in CURRENT_STACK.values():
        for comp in comp_list:
            if comp.lower() in text:
                return True
    return False

def generate_recommendation(entry: dict) -> dict:
    """Create a recommendation dict grounded in the given frontier entry."""
    return {
        "generated_at": "{{TIMESTAMP}}",  # placeholder to be filled at runtime
        "source_entry": entry,
        "recommendation": "Potential free‑tier or low‑cost option detected that could improve the current stack. Review for possible adoption.",
        "grounded_on": entry.get("id", "unknown")
    }

def main():
    # Load frontier entries of interest
    frontier_entries = [e for e in load_jsonl(FRONTIER_LOG)
                        if e.get("claim_type") in {"benchmark_result", "proposed_method"}]

    # Load benchmark scores (currently unused but loaded per spec)
    benchmark_entries = list(load_jsonl(BENCHMARK_LOG))

    recommendations = []
    for entry in frontier_entries:
        if entry_mentions_free_option(entry) and entry_targets_current_component(entry):
            rec = generate_recommendation(entry)
            # Fill timestamp now
            rec["generated_at"] = datetime.utcnow().isoformat() + "Z"
            recommendations.append(rec)

    # If no actionable findings, log a no‑action entry
    if not recommendations:
        no_action = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "recommendation": "No actionable free‑tier or low‑cost findings this cycle.",
            "source_entry": None
        }
        recommendations.append(no_action)

    # Append recommendations to the JSONL file (create if missing)
    UPGRADE_RECS.parent.mkdir(parents=True, exist_ok=True)
    with UPGRADE_RECS.open("a", encoding="utf-8") as f:
        for rec in recommendations:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    from datetime import datetime
    main()
