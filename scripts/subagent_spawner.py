#!/usr/bin/env python3
"""Sub-agent spawning: decompose a complex task into independent subtasks,
run them as REAL concurrent Groq calls (concurrent.futures -- genuine
parallel network I/O within one process). No new API keys needed --
parallelism comes from concurrency against the existing GROQ_API_KEY.
For true OS-level parallelism see subagent-matrix.yml (real separate runners)."""
import os, json, urllib.request, concurrent.futures
from pathlib import Path
from datetime import datetime, timezone

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
MAX_PARALLEL = int(os.environ.get("MAX_PARALLEL_SUBAGENTS", "4"))

def call_groq(prompt, max_tokens=1200):
    body = json.dumps({
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.4,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {GROQ_KEY}",
                 "Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                 "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.load(resp)["choices"][0]["message"]["content"]
    except Exception as e:
        return f"SUBAGENT_ERROR: {e}"

def decompose_task(task_description):
    prompt = f"""Complex task: {task_description}

Decompose into 2-6 subtasks that can run INDEPENDENTLY and IN PARALLEL --
no subtask may depend on another subtask's output. If the task is
inherently sequential, say so explicitly instead of forcing a fake decomposition.

Output ONLY JSON: {{"parallelizable": true/false, "reason_if_not": "...", "subtasks": [{{"id": "...", "prompt": "..."}}]}}"""
    response = call_groq(prompt, max_tokens=800)
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        return json.loads(response[start:end])
    except Exception:
        return {"parallelizable": False, "reason_if_not": "DECOMPOSITION_PARSE_FAILED", "subtasks": []}

def run_subtask(subtask):
    result = call_groq(subtask["prompt"])
    return {"id": subtask["id"], "prompt": subtask["prompt"], "result": result}

def spawn_and_run(task_description):
    decomposition = decompose_task(task_description)
    if not decomposition.get("parallelizable"):
        return {
            "spawned": False,
            "reason": decomposition.get("reason_if_not", "not parallelizable"),
            "fallback": "run sequentially via a single ask_barrot.py call instead",
        }
    subtasks = decomposition["subtasks"]
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(MAX_PARALLEL, len(subtasks))) as executor:
        futures = {executor.submit(run_subtask, st): st["id"] for st in subtasks}
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    failed = [r for r in results if r["result"].startswith("SUBAGENT_ERROR")]
    return {
        "spawned": True, "subtask_count": len(subtasks),
        "succeeded": len(results) - len(failed), "failed": len(failed),
        "results": results,
    }

def aggregate_results(task_description, spawn_result):
    if not spawn_result.get("spawned"):
        return spawn_result
    results_text = "\n\n".join(f"[{r['id']}]: {r['result'][:600]}" for r in spawn_result["results"])
    failure_note = f"\n\nNOTE: {spawn_result['failed']} of {spawn_result['subtask_count']} subtasks failed -- treat synthesis as partial." if spawn_result["failed"] else ""
    prompt = f"""Original task: {task_description}

Subagent results:
{results_text}{failure_note}

Synthesize these into one coherent answer to the original task. If subtasks conflict, note the conflict rather than silently picking one."""
    synthesis = call_groq(prompt, max_tokens=1500)
    spawn_result["synthesis"] = synthesis
    return spawn_result

if __name__ == "__main__":
    if not GROQ_KEY:
        print("GROQ_API_KEY not set")
        raise SystemExit(1)
    task = os.environ.get("SPAWN_TASK", "")
    if not task:
        print("No SPAWN_TASK provided")
        raise SystemExit(1)
    spawn_result = spawn_and_run(task)
    final = aggregate_results(task, spawn_result)
    out = f"subagent_run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    Path(out).write_text(json.dumps(final, indent=2))
    print(f"Saved: {out}")
    if final.get("spawned"):
        print(f"{final['succeeded']}/{final['subtask_count']} subagents succeeded")
    else:
        print(f"Not spawned: {final.get('reason')}")
