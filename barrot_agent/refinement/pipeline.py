"""Refinement pipeline — SOURCE → AUDIT → SEGMENT → REFINE → GENERATE
PATCHES → VALIDATE → APPLY → SEMANTIC EVALUATION → REGRESSION TEST →
RECORD RESULTS.

The scalable upgrade of the ping-pong baseline for large documents:
sections are refined independently (each within the model's real output
budget), changes land as validated patches (never full-document rewrites),
an independent judge scores semantics, a regression gate verifies the final
document against the original, and every operation is recorded to a
persistent, resumable run state + learning history.

Integrity rules enforced here:
- the run is NEVER reported complete while any section was skipped or failed;
- every patch is hash-preconditioned; failed patches are rejected with a
  cause and the original content is preserved;
- if semantic quality regresses, the refinement is NOT accepted merely
  because the mechanical score improved — the batch is rolled back;
- interrupted runs resume from the last committed section (atomic state).
"""
from __future__ import annotations

import copy
import json
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import paths, scoring, segmentation, patches, semantics
from .engine import DEFAULT_EPSILON, REFINABLE_DATA_CLASSES, refine_data
from .refiners import HeuristicRefiner, Refiner
from .segmentation import Slot

IMPLEMENTATION_VERSION = "pp-refine/1.1.0"
DEFAULT_RUNS_DIR = Path("ping-pongings/knowledge-base/refinement_runs")
DEFAULT_HISTORY = Path("ping-pongings/knowledge-base/refinement_history.jsonl")


# ---------------------------------------------------------------- run state
@dataclass
class SectionState:
    id: str
    path_label: str
    status: str = "pending"       # pending|refined|failed|skipped
    attempts: int = 0
    patch_count: int = 0
    rejected_count: int = 0
    errors: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {**self.__dict__}


@dataclass
class RunState:
    run_id: str
    source_hash: str
    source_chars: int
    objective: str
    document: Any                  # current working document (committed state)
    original: Any                  # immutable source snapshot
    sections: list = field(default_factory=list)
    semantic: dict | None = None
    verification: dict | None = None
    disposition: str = "in_progress"   # in_progress|complete|incomplete|rolled_back
    undo_stack: list = field(default_factory=list)
    created: str = ""
    updated: str = ""
    data_classification: str = "unknown"

    def to_dict(self) -> dict:
        d = {**self.__dict__}
        d["sections"] = [s.to_dict() if hasattr(s, "to_dict") else s
                         for s in self.sections]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RunState":
        st = cls.__new__(cls)
        st.__dict__.update(d)
        st.data_classification = str(d.get("data_classification", "unknown"))
        st.sections = [SectionState(**s) if isinstance(s, dict) else s
                       for s in st.sections]
        st.undo_stack = [tuple(u) for u in st.undo_stack]
        return st


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


_RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def _validate_run_id(run_id: str) -> str:
    if (not isinstance(run_id, str) or not _RUN_ID_RE.fullmatch(run_id)
            or ".." in run_id):
        raise ValueError("run_id must be a simple filename-safe identifier")
    return run_id


def _validate_refinement_access(refiners, data_classification: str,
                                allow_external: bool = False, judge=None) -> None:
    if data_classification not in REFINABLE_DATA_CLASSES:
        raise ValueError("unknown or immutable data classification cannot be refined")
    if allow_external:
        raise PermissionError("external refinement providers are decommissioned")


def load_run(run_id: str, runs_dir: Path | str = DEFAULT_RUNS_DIR) -> RunState:
    run_id = _validate_run_id(run_id)
    path = Path(runs_dir) / f"{run_id}.json"
    return RunState.from_dict(json.loads(path.read_text(encoding="utf-8")))


def find_completed(source_hash: str, objective: str,
                   history: Path | str = DEFAULT_HISTORY,
                   data_classification: str = "unknown") -> dict | None:
    """Persistent learning: a (source, objective) pair already refined to a
    verified complete disposition is not repeated."""
    hp = Path(history)
    if not hp.exists():
        return None
    for line in hp.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("source_hash") == source_hash \
                and rec.get("objective") == objective \
                and rec.get("data_classification", "unknown") == data_classification \
                and rec.get("disposition") == "complete":
            return rec
    return None


# ----------------------------------------------------------------- pipeline
class RefinementPipeline:
    """Patch-based, semantically-evaluated, resumable refinement of large
    documents. Reuses the existing refiners and mechanical scorer; adds
    segmentation, patches, semantic evaluation, regression testing,
    rollback, resumability and the learning history."""

    def __init__(self, refiners, judge=None,
                 max_slot_chars: int = segmentation.DEFAULT_MAX_SLOT_CHARS,
                 max_section_attempts: int = 2,
                 ledger: Path | str | None = None,
                 runs_dir: Path | str = DEFAULT_RUNS_DIR,
                 history: Path | str = DEFAULT_HISTORY,
                 epsilon: float = DEFAULT_EPSILON,
                 data_classification: str = "unknown",
                 allow_external: bool = False):
        self.refiners: list[Refiner] = list(refiners)
        if not self.refiners:
            raise ValueError("RefinementPipeline needs at least one refiner")
        _validate_refinement_access(self.refiners, data_classification,
                                    allow_external, judge)
        self.data_classification = data_classification
        self.judge = judge
        self.max_slot_chars = max_slot_chars
        self.max_section_attempts = max_section_attempts
        self.ledger = Path(ledger) if ledger else None
        self.runs_dir = Path(runs_dir)
        self.history = Path(history)
        self.epsilon = epsilon

    # ------------------------------------------------------------ plumbing
    def _log(self, record: dict) -> None:
        if self.ledger is None:
            return
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True)
                     + "\n")

    def _commit(self, state: RunState) -> None:
        state.run_id = _validate_run_id(state.run_id)
        state.updated = _now()
        _atomic_write_json(self.runs_dir / f"{state.run_id}.json",
                           state.to_dict())

    def _append_history(self, record: dict) -> None:
        self.history.parent.mkdir(parents=True, exist_ok=True)
        with self.history.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False,
                                sort_keys=True) + "\n")

    # ------------------------------------------------------- section refine
    def _refine_slot(self, slot: Slot, state: RunState,
                     sstate: SectionState) -> tuple[Any, str | None]:
        """Ping-pong the slot through the refiner pool. Returns
        (refined_value | None, critique_for_retry). None = no acceptable
        refinement; causes are recorded on the SectionState."""
        value = slot.value
        baseline = scoring.score(value)
        critique: str | None = None
        best: tuple[float, Any] | None = None   # (score, candidate)
        cause: str | None = None
        for attempt in range(self.max_section_attempts):
            refiner = self.refiners[(attempt + int(slot.id[1:])) % len(self.refiners)]
            sstate.attempts += 1
            out = refiner.refine(value, critique)
            if out.verdict == "FAILED" or out.data is None:
                cause = f"{refiner.name}: {out.notes}"
                sstate.errors.append(cause)
                self._log({"ts": _now(), "run": state.run_id,
                           "section": slot.id, "actor": refiner.name,
                           "verdict": "FAILED", "notes": out.notes})
                continue
            if out.data == value:
                # nothing to change in this section — success with 0 patches
                return value, None
            if out.data == value:
                cause = f"{refiner.name}: no change proposed"
                continue
            cand_score = scoring.score(out.data)
            if cand_score < baseline - self.epsilon:
                cause = f"{refiner.name}: mechanical regression " \
                        f"{baseline:.4f}->{cand_score:.4f}"
                sstate.errors.append(cause)
                self._log({"ts": _now(), "run": state.run_id,
                           "section": slot.id, "actor": refiner.name,
                           "verdict": "REJECTED_MECHANICAL",
                           "notes": cause})
                critique = cause
                continue
            # deterministic semantic gate BEFORE any patch exists
            sem = semantics.heuristic_semantic_eval(value, out.data)
            if sem.regression < 0.90:
                cause = f"{refiner.name}: semantic regression " \
                        f"({'; '.join(sem.regressions[:3])})"
                sstate.errors.append(cause)
                self._log({"ts": _now(), "run": state.run_id,
                           "section": slot.id, "actor": refiner.name,
                           "verdict": "REJECTED_SEMANTIC", "notes": cause})
                critique = cause
                continue
            if best is None or cand_score > best[0]:
                best = (cand_score, out.data)
            if out.verdict == "CONVERGED":
                break
        if best is None:
            return None, cause
        if slot.kind == "string_range" and not isinstance(best[1], str):
            sstate.errors.append("string slot refined to non-string")
            return None, "string slot refined to non-string"
        return best[1], cause

    # ------------------------------------------------------------- main run
    def run(self, data: Any, objective: str = "", run_id: str | None = None,
            source_identity: str = "", force: bool = False) -> dict:
        t0 = time.time()
        source_hash = paths.value_hash(data)
        if run_id is None:
            run_id = f"ref-{source_hash[:12]}-{time.time_ns()}"
        else:
            run_id = _validate_run_id(run_id)
        if (self.runs_dir / f"{run_id}.json").exists():
            raise FileExistsError(f"refinement run already exists: {run_id}")

        # 1. SOURCE + persistent learning: skip already-completed work
        if not force:
            prior = find_completed(source_hash, objective, self.history,
                                   self.data_classification)
            if prior is not None:
                return {"run_id": prior.get("run_id"), "disposition":
                        "already_converged", "resumed": False,
                        "history": prior}

        # 2. AUDIT
        audit = segmentation.audit_document(data)
        self._log({"ts": _now(), "run": run_id, "event": "audit",
                   "audit": audit.to_dict()})

        # 3. SEGMENT (coverage-exact; raises if the plan would skip content)
        slots = segmentation.segment_document(data, self.max_slot_chars)
        state = RunState(
            run_id=run_id, source_hash=source_hash,
            source_chars=audit.total_chars, objective=objective,
            document=copy.deepcopy(data), original=copy.deepcopy(data),
            data_classification=self.data_classification,
            sections=[SectionState(id=s.id, path_label=s.path_label)
                      for s in slots],
            created=_now())
        self._commit(state)

        outcome = self._execute(state, slots, source_identity, t0)
        return outcome

    def _execute(self, state: RunState, slots: list[Slot],
                 source_identity: str, t0: float) -> dict:
        doc = state.document
        original = state.original
        smap = {s.id: s for s in slots}
        batch_undo: list = []
        applied_patches: list = []
        unresolved_conflicts: list = []

        # 4-7. REFINE -> GENERATE PATCHES -> VALIDATE -> APPLY per section
        doc = state.document
        splice_shift: dict[str, int] = {}   # cumulative length delta per leaf
        for sstate in state.sections:
            if sstate.status == "refined":
                continue                      # resume: already done
            slot = smap[sstate.id]
            refined, cause = self._refine_slot(slot, state, sstate)
            if refined is None:
                sstate.status = "failed"
                self._log({"ts": _now(), "run": state.run_id,
                           "event": "section_failed",
                           "section": slot.id, "cause": cause})
                self._commit(state)
                continue
            if slot.kind == "string_range":
                # splice patches; offsets shifted by earlier splices on the
                # same leaf so preconditions stay valid (slots are disjoint
                # and generated in ascending order)
                current = paths.resolve(doc, slot.parent_path)
                shift = splice_shift.get(slot.parent_path, 0)
                gen = [patches.make_splice(
                    slot.parent_path, current,
                    slot.start + shift, slot.end + shift, str(refined),
                    "pipeline", f"section {slot.id}")]
            else:
                gen = patches.diff_values(slot.value, refined, "", "pipeline")
                for j, g in enumerate(gen):
                    g.path = slot.absolute_leaf_path(g.path)
                    g.patch_id = f"{state.run_id}/{slot.id}/{j}"
            before = scoring.score(doc)
            batch = patches.apply_patches(doc, gen)
            doc = batch.document
            state.document = doc
            if gen and gen[0].op == patches.SPLICE:
                splice_shift[slot.parent_path] = shift + (
                    len(str(refined)) - (slot.end - slot.start))
            batch_undo.extend(batch.undo)
            applied_patches.extend(batch.applied)
            sstate.patch_count = len(batch.applied)
            sstate.rejected_count = len(batch.rejected)
            unresolved_conflicts.extend(
                {"path": p.path, "cause": p.failure_cause}
                for p in batch.rejected
                if p.status == patches.REJECTED_CONFLICT)
            if batch.rejected:
                sstate.errors.extend(
                    f"{p.path}: {p.failure_cause}" for p in batch.rejected)
            after = scoring.score(doc)
            sstate.status = "refined"
            self._log({"ts": _now(), "run": state.run_id,
                       "event": "section_refined", "section": slot.id,
                       "patches_applied": len(batch.applied),
                       "patches_rejected": len(batch.rejected),
                       "score_before": before, "score_after": after})
            self._commit(state)               # atomic resume point

        # 8. SEMANTIC EVALUATION (independent judge; deterministic fallback)
        mechanical_before = scoring.score(original)
        sem = semantics.evaluate(original, doc, judge=self.judge,
                                 objective=state.objective,
                                 mechanical_before=mechanical_before)
        state.semantic = sem.to_dict()

        # 9. REGRESSION TEST: verify against original + semantic gate
        ver = patches.verify_against_original(original, doc, applied_patches)
        state.verification = ver.to_dict()

        if sem.status == "regressed" and applied_patches:
            # semantic regression veto: restore the original, then allow one
            # corrected attempt with the judge's regressions as critique
            self._log({"ts": _now(), "run": state.run_id,
                       "event": "semantic_veto_rollback",
                       "regressions": sem.regressions[:5]})
            doc = copy.deepcopy(original)
            state.document = doc
            applied_patches = []
            batch_undo = []
            retry = self._corrected_retry(state, slots, smap, sem.regressions)
            if retry is not None:
                doc, applied_patches, batch_undo = retry
                state.document = doc
                sem2 = semantics.evaluate(
                    original, doc, judge=self.judge,
                    objective=state.objective,
                    mechanical_before=scoring.score(original))
                ver2 = patches.verify_against_original(original, doc,
                                                       applied_patches)
                if sem2.status != "regressed" and ver2.ok:
                    sem, ver = sem2, ver2
                    state.semantic = sem.to_dict()
                else:
                    doc = copy.deepcopy(original)
                    state.document = doc
                    applied_patches = []
                    state.disposition = "rolled_back"
            else:
                state.disposition = "rolled_back"
        state.verification = ver.to_dict()

        # final disposition: complete ONLY if nothing was skipped or failed
        failed = [s for s in state.sections
                  if s.status in ("failed", "skipped")]
        if state.disposition != "rolled_back":
            state.disposition = "complete" if (not failed and ver.ok) \
                else "incomplete"

        # 10. RECORD RESULTS — persistent learning history
        record = {
            "ts": _now(),
            "implementation_version": IMPLEMENTATION_VERSION,
            "run_id": state.run_id,
            "source_identity": source_identity,
            "source_hash": state.source_hash,
            "final_hash": paths.value_hash(doc),
            "objective": state.objective,
            "data_classification": state.data_classification,
            "sections_total": len(state.sections),
            "sections_refined": sum(1 for s in state.sections
                                    if s.status == "refined"),
            "sections_failed": [s.id for s in state.sections
                                if s.status in ("failed", "skipped")],
            "patches_generated": len(applied_patches),
            "patches_applied": len(applied_patches),
            "mechanical": {"before": mechanical_before,
                           "after": scoring.score(doc)},
            "semantic": state.semantic,
            "regression": {"verification_ok": ver.ok,
                           "missing": len(ver.missing_paths),
                           "smuggled": len(ver.smuggled_changes),
                           "score": (state.semantic or {}).get("regression")},
            "failures_and_corrections": [
                {"section": s.id, "errors": s.errors[-3:]}
                for s in state.sections if s.errors],
            "unresolved_conflicts": unresolved_conflicts[:20],
            "disposition": state.disposition,
            "elapsed_s": round(time.time() - t0, 3),
        }
        self._append_history(record)
        state.disposition = record["disposition"]
        self._commit(state)
        return {"run_id": state.run_id,
                "disposition": state.disposition,
                "resumed": False,
                "sections": [s.__dict__ for s in state.sections],
                "mechanical": record["mechanical"],
                "semantic": state.semantic,
                "verification": state.verification,
                "unresolved_conflicts": record["unresolved_conflicts"],
                "history": record}

    # --------------------------------------------------- corrected attempt
    def _corrected_retry(self, state: RunState, slots: list[Slot], smap,
                         regressions: list[str]):
        """One corrected pass over materially-changed sections, with the
        judge's regressions injected as critique. Returns
        (doc, applied, undo) or None."""
        doc = state.document
        applied: list = []
        undo: list = []
        critique = "PRIOR ATTEMPT REGRESSED: " + "; ".join(regressions[:5])
        for sstate in state.sections:
            if sstate.status != "refined":
                continue
            slot = smap[sstate.id]
            refined, _c = self._refine_slot_with_critique(slot, critique)
            if refined is None:
                continue
            gen = patches.diff_values(slot.value, refined, "", "pipeline")
            for g in gen:
                g.path = slot.absolute_leaf_path(g.path)
            batch = patches.apply_patches(doc, gen)
            doc = batch.document
            applied.extend(batch.applied)
            undo.extend(batch.undo)
        if not applied:
            return None
        return doc, applied, undo

    def _refine_slot_with_critique(self, slot: Slot, critique: str):
        value = slot.value
        baseline = scoring.score(value)
        for refiner in self.refiners:
            out = refiner.refine(value, critique)
            if out.verdict == "FAILED" or out.data is None or out.data == value:
                continue
            if scoring.score(out.data) < baseline - self.epsilon:
                continue
            sem = semantics.heuristic_semantic_eval(value, out.data)
            if sem.regression < 0.90:
                continue
            return out.data, None
        return None, None

    # -------------------------------------------------------------- resume
    def resume(self, run_id: str) -> dict:
        """Resume an interrupted run from its committed state. Sections with
        status 'refined' are skipped (never repeated); pending/failed
        sections get fresh attempts."""
        state = load_run(run_id, self.runs_dir)
        if state.data_classification != self.data_classification:
            raise PermissionError("resume classification does not match the saved run")
        if state.disposition not in ("in_progress", "incomplete"):
            return {"run_id": run_id, "disposition": state.disposition,
                    "resumed": True, "note": "nothing to resume"}
        slots = segmentation.segment_document(state.original,
                                              self.max_slot_chars)
        smap = {s.id: s for s in slots}
        if len(smap) != len(state.sections):
            raise RuntimeError("run state inconsistent with source plan")
        t0 = time.time()
        outcome = self._execute(state, slots, "", t0)
        outcome["resumed"] = True
        return outcome


def refine_document(data: Any, objective: str = "",
                    refiners=None, judge=None,
                    source_identity: str = "", force: bool = False,
                    ledger: Path | str | None = None,
                    max_rounds: int | None = None,
                    data_classification: str = "unknown",
                    allow_external: bool = False) -> dict:
    """Refine explicitly classified derived data; canonical evidence is rejected."""
    if allow_external:
        raise PermissionError("external refinement providers are decommissioned")
    if refiners is None:
        refiners = [HeuristicRefiner(), HeuristicRefiner("heuristic-2")]
    refiners = list(refiners)
    _validate_refinement_access(refiners, data_classification,
                                allow_external, judge)
    audit = segmentation.audit_document(data)
    if not audit.needs_segmentation:
        kwargs = {
            "refiners": refiners, "ledger": ledger,
            "data_classification": data_classification,
        }
        if max_rounds is not None:
            kwargs["max_rounds"] = max_rounds
        report = refine_data(data, **kwargs)
        return {"disposition": "complete" if report.converged else "capped",
                "mode": "classic", "report": report}
    pipe = RefinementPipeline(
        refiners, judge=judge, ledger=ledger,
        data_classification=data_classification,
        allow_external=False)
    return pipe.run(data, objective=objective,
                    source_identity=source_identity, force=force)
