#!/usr/bin/env python3
"""Live-runtime verification of the refinement upgrade (Barrot V3 directive).

Runs the REAL >24K document (barrot_capability_audit.json) through the full
patch pipeline with the live LunaRoute pool + independent judge, and prints
the evidence the final report needs. Never prints credentials.
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from barrot_agent.refinement import (          # noqa: E402
    LLMSemanticJudge,
    RefinementPipeline,
    audit_document,
    make_model_refiners,
    segment_document,
)

DOC = Path(__file__).resolve().parents[1] / "barrot_capability_audit.json"
OUT_DIR = (Path(__file__).resolve().parents[1]
           / "ping-pongings/knowledge-base/refinement_runs")


def main() -> int:
    if (os.environ.get("BARROT_LIVE_REFINEMENT") != "1"
            or os.environ.get("BARROT_ALLOW_EXTERNAL_REFINEMENT") != "1"
            or os.environ.get("BARROT_LIVE_REFINEMENT_APPROVED") != "1"):
        print("BLOCKED: live transfer requires three explicit approval variables", file=sys.stderr)
        return 2
    if "LUNAROUTE_API_KEY" not in os.environ:
        print("BLOCKED: LUNAROUTE_API_KEY not available", file=sys.stderr)
        return 2
    source = json.loads(DOC.read_text(encoding="utf-8"))
    audit = audit_document(source)
    slots = segment_document(source)
    print(f"SOURCE: {DOC.name} chars={audit.total_chars} leaves={audit.leaf_count} "
          f"nodes={audit.node_count} depth={audit.max_depth}")
    print(f"SEGMENTS: {len(slots)} slots "
          f"({sum(1 for s in slots if s.kind == 'list_slice')} list_slice, "
          f"{sum(1 for s in slots if s.kind == 'dict_keys')} dict_keys, "
          f"{sum(1 for s in slots if s.kind == 'string_range')} string_range), "
          f"max_slot_chars={max(s.chars for s in slots)}")

    refiners = make_model_refiners(allow_external=True,
                                   data_classification="public_documentation")
    print(f"POOL: {[r.name for r in refiners]}")
    judge = LLMSemanticJudge(refiners[1])   # independent: NOT refiners[0]
    print(f"JUDGE: {judge.name} (independent of refiner {refiners[0].name})")

    pipe = RefinementPipeline(
        refiners, judge=judge, ledger=None,
        data_classification="public_documentation", allow_external=True)
    t0 = time.time()
    objective = ("tighten wording, normalize spacing, remove redundancy; "
                 "preserve every fact and requirement")
    out = pipe.run(source, objective=objective,
                   source_identity="barrot_capability_audit.json",
                   force=True)
    elapsed = time.time() - t0
    print(f"DISPOSITION: {out['disposition']} (elapsed {elapsed:.1f}s)")
    print(f"MECHANICAL: {out['mechanical']['before']:.4f} -> "
          f"{out['mechanical']['after']:.4f}")
    sem = out["semantic"]
    print(f"SEMANTIC: status={sem['status']} score={sem['semantic']} "
          f"regression={sem['regression']} judge={sem['judge']} "
          f"calibrated={sem['calibrated']}")
    if sem.get("dimensions"):
        jd = {k: v for k, v in sem["dimensions"].items() if k.startswith("judge_")}
        if jd:
            print(f"JUDGE_DIMS: {json.dumps(jd)}")
    ver = out["verification"]
    print(f"VERIFICATION: ok={ver['ok']} missing={len(ver['missing_paths'])} "
          f"smuggled={len(ver['smuggled_changes'])} deletions={len(ver['deletions'])}")
    refined_n = sum(1 for s in out["sections"] if s["status"] == "refined")
    print(f"SECTIONS: {refined_n}/{len(out['sections'])} refined; "
          f"attempts={sum(s['attempts'] for s in out['sections'])}; "
          f"patches={sum(s['patch_count'] for s in out['sections'])}; "
          f"rejected={sum(s['rejected_count'] for s in out['sections'])}")
    if out.get("unresolved_conflicts"):
        print(f"CONFLICTS: {out['unresolved_conflicts'][:3]}")
    # persist the refined document as run evidence
    from barrot_agent.refinement import load_run
    final = load_run(out["run_id"]).document
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"live_refined_capability_audit-{out['run_id']}.json"
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing evidence: {out_path}")
    out_path.write_text(json.dumps(final, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"FINAL_SAVED: {out_path} chars={len(json.dumps(final, ensure_ascii=False))}")
    print(f"HISTORY: run_id={out['run_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())