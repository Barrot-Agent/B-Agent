#!/usr/bin/env python3
"""
BARROT-Ω BENCHMARK SUMMARY — summarizes benchmark_log.jsonl (real, weekly,
machine-graded coding task results) for the getBarrotBenchmark WebMCP tool.
Includes every run, including failures - honesty about a bad run is the
actual trust signal, not hiding it.
"""

import json
import os

KB_DIR = "ping-pongings/knowledge-base"
LOG_PATH = os.path.join(KB_DIR, "benchmark_log.jsonl")
OUT_PATH = os.path.join(KB_DIR, "benchmark_summary.json")


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def main():
    runs = load_jsonl(LOG_PATH)
    if not runs:
        print("No benchmark runs found.")
        return

    total_tasks = sum(r.get("tasks_total", 0) for r in runs)
    total_passed = sum(r.get("tasks_passed", 0) for r in runs)

    history = [
        {
            "run_id": r.get("run_id"),
            "run_at": r.get("run_at"),
            "tasks_passed": r.get("tasks_passed"),
            "tasks_total": r.get("tasks_total"),
        }
        for r in runs
    ]

    latest = runs[-1]

    out = {
        "note": (
            "Machine-graded coding tasks only - generated code executed "
            "against real assertions, not self-reported. This measures "
            "coding-benchmark performance, not trading signal accuracy "
            "(see getSignalAccuracy for that). All runs shown, including "
            "any failures."
        ),
        "total_runs": len(runs),
        "aggregate_pass_rate": round(total_passed / total_tasks, 3) if total_tasks else None,
        "latest_run": {
            "run_id": latest.get("run_id"),
            "run_at": latest.get("run_at"),
            "tasks_passed": latest.get("tasks_passed"),
            "tasks_total": latest.get("tasks_total"),
        },
        "history": history,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    web_path = os.path.join("web", os.path.basename(OUT_PATH))
    os.makedirs("web", exist_ok=True)
    with open(web_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Total runs: {len(runs)}")
    print(f"Aggregate pass rate: {out['aggregate_pass_rate']}")
    print(f"Latest: {latest.get('tasks_passed')}/{latest.get('tasks_total')}")
    print(f"\nWritten to {OUT_PATH}")


if __name__ == "__main__":
    main()
