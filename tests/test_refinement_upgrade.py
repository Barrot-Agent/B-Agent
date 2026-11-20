"""Tests for the Barrot V3 refinement upgrade: patch-based large-document
refinement + semantic evaluation.

Test tiers (explicitly distinguished):
- MOCKED (default): every test here is offline/deterministic — scripted
  refiners/judges, temp dirs, no network.
- REAL RUNTIME: tests marked with @skipUnless(BARROT_LIVE_REFINEMENT) hit
  the live LunaRoute API with a real document slice; they never run in the
  default suite.
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from barrot_agent.refinement import (          # noqa: E402
    CALIBRATION_CASES,
    HeuristicRefiner,
    LunaRouteRefiner,
    LLMSemanticJudge,
    Patch,
    Refiner,
    RefinementOutput,
    RefinementPipeline,
    RunState,
    SectionState,
    apply_patches,
    audit_document,
    calibrate,
    detect_conflicts,
    evaluate,
    heuristic_semantic_eval,
    load_run,
    make_delete,
    make_replace,
    make_set,
    make_splice,
    paths,
    refine_document,
    rollback,
    scoring,
    segment_document,
    verify_against_original,
)

LIVE = (os.environ.get("BARROT_LIVE_REFINEMENT") == "1" and
        os.environ.get("BARROT_ALLOW_EXTERNAL_REFINEMENT") == "1" and
        os.environ.get("BARROT_LIVE_REFINEMENT_APPROVED") == "1")


def _big_document(sections: int = 60) -> dict:
    """Synthetic >24K document with realistic structure."""
    return {
        "title": "Integration Knowledge Base",
        "revision": 3,
        "sections": [{
            "id": f"sec{i}",
            "name": f"Topic  {i}",
            "body": f"Discusses subject {i} with  double spacing. " * 25,
            "tags": [f"tag{i}", f"tag{i}"],
            "weight": i * 1.5,
        } for i in range(sections)],
        "glossary": {"term  one": "def one", "term2": ""},
        "provenance": {"source": "synthetic", "confidence": "high"},
    }


class TestSegmentation(unittest.TestCase):
    def test_small_document_single_slot(self):
        doc = {"a": 1, "b": "x  y"}
        slots = segment_document(doc, max_chars=9000)
        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0].kind, "root")

    def test_large_document_segmented_with_full_coverage(self):
        big = _big_document()
        audit = audit_document(big)
        self.assertGreater(audit.total_chars, 24000)
        self.assertTrue(audit.needs_segmentation)
        slots = segment_document(big)
        self.assertGreater(len(slots), 1)
        for s in slots:
            self.assertLessEqual(s.chars, 9000)
            self.assertTrue(s.context)          # context present

    def test_coverage_exact_no_skip_no_dup(self):
        big = _big_document(sections=80)
        slots = segment_document(big, max_chars=6000)
        original_leaves = {p for p, _ in paths.walk_leaves(big)
                           if not p.endswith("/")}
        covered = set()
        for s in slots:
            if s.kind == "string_range":
                covered.add(s.parent_path)
            else:
                for p, _ in paths.walk_leaves(s.value):
                    if not p.endswith("/"):
                        covered.add(s.absolute_leaf_path(p))
        self.assertEqual(original_leaves - covered, set())   # nothing skipped
        self.assertEqual(len(covered), len(original_leaves))  # no duplicates

    def test_very_large_document(self):
        big = _big_document(sections=600)               # ~300KB
        self.assertGreater(audit_document(big).total_chars, 200000)
        slots = segment_document(big, max_chars=8000)
        self.assertGreater(len(slots), 30)
        # order preservation: list_slice slots ascend without gaps
        slices = [(s.start, s.end) for s in slots if s.kind == "list_slice"]
        self.assertEqual(slices, sorted(slices))
        for (a, b), (c, d) in zip(slices, slices[1:]):
            self.assertEqual(b, c)                       # contiguous

    def test_oversized_string_leaf_split(self):
        doc = {"prose": "Sentence number one. " * 1200}   # ~26KB string
        slots = segment_document(doc, max_chars=8000)
        self.assertGreater(len(slots), 1)
        ranges = [(s.start, s.end) for s in slots]
        self.assertEqual(ranges[0][0], 0)
        self.assertEqual(ranges[-1][1], len(doc["prose"]))
        for (a, b), (c, _) in zip(ranges, ranges[1:]):
            self.assertEqual(b, c)                       # contiguous, ordered
        # natural boundaries preferred: cuts land on ". " when available
        for (a, b) in ranges[:-1]:
            self.assertTrue(doc["prose"][b - 1] in "\n.")

    def test_section_boundaries_nested(self):
        doc = {"deep": {"list": [{"k": "v" * 3000} for _ in range(10)]}}
        slots = segment_document(doc, max_chars=4000)
        original_leaves = {p for p, _ in paths.walk_leaves(doc)
                           if not p.endswith("/")}
        covered = {s.absolute_leaf_path(p)
                   for s in slots for p, _ in paths.walk_leaves(s.value)
                   if not p.endswith("/") and s.kind != "string_range"}
        self.assertEqual(original_leaves - covered, set())

    def test_segmentation_deterministic(self):
        big = _big_document()
        a = [(s.id, s.kind, s.parent_path, s.start, s.end, tuple(s.keys))
             for s in segment_document(big)]
        b = [(s.id, s.kind, s.parent_path, s.start, s.end, tuple(s.keys))
             for s in segment_document(big)]
        self.assertEqual(a, b)

    def test_dotted_and_backslash_keys_escape_correctly(self):
        # real-world regression: barrot_capability_audit.json keys file
        # names with literal dots ("a2a_server.py"); lone backslashes must
        # survive too. Buggy escaping produced invalid paths and tripped
        # the coverage contract on the real document.
        for key in ("a2a_server.py", "back\\slash.key", "dots...here"):
            p = paths.ptr_child("evidence", key)
            self.assertEqual(paths.ptr_split(p), ["evidence", key])
        doc = {"evidence": {"a2a_server.py": {"fingerprint": "x" * 5000,
                                              "path": "y" * 5000},
                            "plain": "z"}}
        slots = segment_document(doc, max_chars=3000)   # must not raise
        original_leaves = {p for p, _ in paths.walk_leaves(doc)
                           if not p.endswith("/")}
        covered = set()
        for s in slots:
            if s.kind == "string_range":
                covered.add(s.parent_path)
            else:
                covered |= {s.absolute_leaf_path(pth)
                            for pth, _ in paths.walk_leaves(s.value)
                            if not pth.endswith("/")}
        self.assertEqual(original_leaves - covered, set())

    def test_slot_budget_respected_with_key_overhead(self):
        # key-name overhead (quotes/colon) counts against the slot budget
        doc = {"files": {f"module_number_{i}.py": "x" * 700
                         for i in range(40)}}
        slots = segment_document(doc, max_chars=9000)
        self.assertLessEqual(max(s.chars for s in slots), 9000 + 2)


class TestPatches(unittest.TestCase):
    def setUp(self):
        self.doc = {"meta": {"n": 3, "title": "t"}, "items": [1, 2, 3],
                    "prose": "hello world"}

    def test_replace_set_delete_apply(self):
        res = apply_patches(self.doc, [
            make_replace("meta.n", 3, 5),
            make_set("meta", "extra", True),
            make_delete("items", [1, 2, 3]),
        ])
        self.assertEqual(len(res.applied), 3)
        self.assertEqual(res.document["meta"], {"n": 5, "title": "t",
                                                "extra": True})
        self.assertNotIn("items", res.document)

    def test_stale_precondition_rejected(self):
        stale = make_replace("meta.n", 99, 5)      # doc holds 3, not 99
        res = apply_patches(self.doc, [stale])
        self.assertEqual(len(res.applied), 0)
        self.assertEqual(stale.status, "rejected_stale")

    def test_conflicts_same_path_and_ancestor(self):
        a = make_replace("meta.n", 3, 5)
        b = make_replace("meta.n", 3, 7)           # conflicting new
        detect_conflicts([a, b])
        self.assertEqual(b.status, "rejected_conflict")

        anc = make_replace("meta", {"n": 9}, {"n": 9})
        deep = make_replace("meta.n", 3, 5)
        detect_conflicts([anc, deep])
        self.assertEqual(deep.status, "rejected_conflict")  # ancestor wins

    def test_incompatible_delete_vs_set(self):
        d = make_delete("meta", {"n": 3, "title": "t"})
        s = make_set("meta", "extra", 1)
        detect_conflicts([d, s])
        self.assertEqual(s.status, "rejected_conflict")

    def test_noop_skipped(self):
        p = make_replace("meta.n", 3, 3)
        res = apply_patches(self.doc, [p])
        self.assertEqual(p.status, "skipped_noop")
        self.assertEqual(len(res.applied), 0)

    def test_corrupted_patch_rejected_with_cause(self):
        bad = Patch(op="frobnicate", path="meta.n", old_hash="x")
        apply_patches(self.doc, [bad])
        self.assertEqual(bad.status, "rejected_invalid")
        self.assertTrue(bad.failure_cause)
        # structurally-broken patch: unresolvable path
        broken = make_replace("meta.no Such Key!!", None, {"a": 1})
        apply_patches(self.doc, [broken])
        self.assertEqual(broken.status, "rejected_invalid")

    def test_rollback_restores_exactly(self):
        res = apply_patches(self.doc, [
            make_replace("meta.n", 3, 9),
            make_delete("items", [1, 2, 3]),
            make_splice("prose", "hello world", 0, 5, "HELLO"),
        ])
        rollback(res.document, res.undo)
        self.assertEqual(res.document, self.doc)

    def test_splice_order_and_shift(self):
        # two splices on one leaf: later-offset splice must stay valid
        text = "AAAA BBBB CCCC"
        res = apply_patches(self.doc | {"prose": text}, [
            make_splice("prose", text, 0, 4, "X"),      # AAAA -> X (shorter)
            make_splice("prose", text, 10, 14, "Z"),
        ])
        self.assertEqual(len(res.applied), 2)
        self.assertEqual(res.document["prose"], "X BBBB Z")

    def test_verify_catches_smuggled_change(self):
        final = copy.deepcopy(self.doc)
        final["items"][1] = 999                       # undeclared
        res = apply_patches(self.doc, [make_replace("meta.n", 3, 5)])
        ver = verify_against_original(self.doc, final, res.applied)
        self.assertFalse(ver.ok)
        self.assertIn("items.1", ver.smuggled_changes)

    def test_verify_catches_missing_content(self):
        final = copy.deepcopy(self.doc)
        del final["items"][2]
        ver = verify_against_original(self.doc, final, [])
        self.assertFalse(ver.ok)
        self.assertTrue(ver.missing_paths)

    def test_verify_accepts_declared_deletion(self):
        res = apply_patches(self.doc, [make_delete("meta.title", "t")])
        ver = verify_against_original(self.doc, res.document, res.applied)
        self.assertTrue(ver.ok)
        self.assertEqual(ver.deletions, ["meta.title"])

    def test_diff_generates_targeted_patches(self):
        old = {"a": "x  x", "b": 1, "c": [1, 1, 2]}
        new = {"a": "x x", "b": 1, "c": [1, 2]}
        gen = __import__("barrot_agent.refinement.patches", fromlist=["x"]) \
            .diff_values(old, new, "", "t")
        applied_paths = {p.path for p in gen}
        self.assertIn("a", applied_paths)
        self.assertNotIn("b", applied_paths)          # unchanged → no patch
        res = apply_patches(copy.deepcopy(old), gen)
        self.assertEqual(res.document, new)


class TestSemantics(unittest.TestCase):
    def test_semantic_improvement_without_structural_change(self):
        orig = {"analysis": "the latency performance observed is good "
                            "across the board", "owner": "team-a"}
        refined = {"analysis": "p99 latency measured at 120ms across 14 "
                               "days of traces", "owner": "team-a"}
        self.assertEqual(scoring.score(orig), scoring.score(refined))  # flat
        v = heuristic_semantic_eval(orig, refined)
        self.assertNotEqual(v.status, "regressed")    # not punished

    def test_meaning_changing_regression_detected(self):
        orig = {"requirement": "all payments must be signed with HMAC-SHA256"
                               " and replay-protected with a 5 minute nonce"
                               " window"}
        refined = {"requirement": "payments are signed"}
        v = heuristic_semantic_eval(orig, refined)
        self.assertEqual(v.status, "regressed")
        self.assertLess(v.regression, 0.9)

    def test_factual_inconsistency_detected(self):
        v = heuristic_semantic_eval({"rate": 0.87}, {"rate": 0.99})
        self.assertEqual(v.status, "regressed")
        self.assertTrue(any("numeric_changed:rate" in r
                            for r in v.regressions))

    def test_scoring_repeatable(self):
        orig = {"a": "x  y", "b": [1, 1, 2]}
        refined = {"a": "x y", "b": [1, 2]}
        v1 = heuristic_semantic_eval(orig, refined).to_dict()
        v2 = heuristic_semantic_eval(orig, refined).to_dict()
        self.assertEqual(v1, v2)

    def test_four_separate_results_present(self):
        v = evaluate({"a": 1}, {"a": 1})
        self.assertIsInstance(v.mechanical, float)
        self.assertIsInstance(v.semantic, float)
        self.assertIsInstance(v.regression, float)
        self.assertIn(v.status, ("improved", "unchanged", "regressed"))

    def test_calibration_cases_exist_and_deterministic_core_passes(self):
        self.assertEqual(len(CALIBRATION_CASES), 3)
        trusted, failures = calibrate(heuristic_semantic_eval)
        self.assertTrue(trusted, failures)

    def test_uncalibrated_judge_cannot_claim_improved(self):
        class LyingJudge:
            is_llm = True
            name = "lying"

            def evaluate(self, o, r, objective=""):
                return type(heuristic_semantic_eval({}, {}))(
                    status="improved", calibrated=True, judge=self.name,
                    semantic=0.99)

        v = evaluate({"a": "x"}, {"a": "x"}, judge=LyingJudge())
        self.assertFalse(v.calibrated)
        self.assertEqual(v.status, "unchanged")     # cannot claim improved

    def test_calibrated_good_judge_can_claim_improved(self):
        class GoodJudge:
            is_llm = True
            name = "good"

            def evaluate(self, o, r, objective=""):
                for case in CALIBRATION_CASES:
                    if paths.value_hash(o) == \
                            paths.value_hash(case["original"]):
                        return type(heuristic_semantic_eval({}, {}))(
                            status=case["expected_status"],
                            calibrated=True, judge=self.name, semantic=0.95,
                            regression=1.0)
                text = paths.canonical(r).lower()
                if "redis" in text and "utilizes" not in text:
                    return type(heuristic_semantic_eval({}, {}))(
                        status="improved", calibrated=True, judge=self.name,
                        semantic=0.95, regression=1.0)
                return type(heuristic_semantic_eval({}, {}))(
                    status="unchanged", calibrated=True, judge=self.name,
                    semantic=0.5, regression=1.0)

        trusted, failures = calibrate(GoodJudge())
        self.assertTrue(trusted, failures)
        orig = {"note": "the system utilizes caching effectively"}
        refined = {"note": "the system uses Redis caching; hit rate 87%"}
        v = evaluate(orig, refined, judge=GoodJudge())
        self.assertEqual(v.status, "improved")
        self.assertEqual(v.judge, "good")   # scripted judge's own name

    def test_deterministic_veto_overrides_judge(self):
        class BlindJudge:
            is_llm = True
            name = "blind"

            def evaluate(self, o, r, objective=""):
                return type(heuristic_semantic_eval({}, {}))(
                    status="improved", calibrated=True, judge=self.name,
                    semantic=0.99, regression=1.0)

        orig = {"req": "sign with HMAC-SHA256 and use nonce replay defense "
                       "window 5 minutes", "n": 7}
        refined = {"req": "sign things", "n": 7}
        v = evaluate(orig, refined, judge=BlindJudge())
        self.assertEqual(v.status, "regressed")     # core vetoes the judge


class _FlakyCounter(Refiner):
    """Refiner that fails on demand — for interruption/incomplete tests."""

    def __init__(self, name, fail_paths=()):
        self.name = name
        self.fail_paths = set(fail_paths)
        self.calls = 0

    def refine(self, data, critique=None):
        self.calls += 1
        if isinstance(data, dict) and data.get("id") in self.fail_paths:
            return RefinementOutput(self.name, "refine", "FAILED",
                                    data=None, notes="simulated outage")
        if isinstance(data, list) and any(
                isinstance(x, dict) and x.get("id") in self.fail_paths
                for x in data):
            return RefinementOutput(self.name, "refine", "FAILED",
                                    data=None, notes="simulated outage")
        d = copy.deepcopy(data)
        if isinstance(d, dict):
            if "name" in d:
                d["name"] = d["name"].replace("  ", " ")
        elif isinstance(d, list):
            for x in d:
                if isinstance(x, dict) and "name" in x:
                    x["name"] = x["name"].replace("  ", " ")
        return RefinementOutput(self.name, "refine", "REFINED", data=d)

    def critique(self, data):
        return RefinementOutput(self.name, "critique", "CONVERGED",
                                critique="ok")


class TestPipeline(unittest.TestCase):
    def _pipe(self, td, refiners=None, **kw):
        kw.setdefault("data_classification", "derived_summary")
        return RefinementPipeline(
            refiners or [HeuristicRefiner(), HeuristicRefiner("h2")],
            runs_dir=Path(td) / "runs",
            history=Path(td) / "hist.jsonl",
            ledger=None, **kw)

    def test_large_document_end_to_end(self):
        big = _big_document()
        with tempfile.TemporaryDirectory() as td:
            out = self._pipe(td).run(big, objective="normalize")
            self.assertEqual(out["disposition"], "complete")
            self.assertTrue(out["verification"]["ok"])
            self.assertGreater(out["mechanical"]["after"],
                               out["mechanical"]["before"])
            self.assertEqual(out["semantic"]["status"], "improved")
            # ordering + content preserved
            st = load_run(out["run_id"], Path(td) / "runs")
            ids = [s["id"] for s in st.document["sections"]]
            self.assertEqual(ids, [f"sec{i}" for i in range(60)])

    def test_never_reports_complete_when_section_skipped(self):
        big = _big_document(sections=30)
        # make exactly one section's id trip the flaky refiner
        target_id = big["sections"][7]["id"]
        with tempfile.TemporaryDirectory() as td:
            out = self._pipe(td, [_FlakyCounter("f", fail_paths={target_id})],
                             max_section_attempts=1).run(big)
            self.assertEqual(out["disposition"], "incomplete")
            failed = [s for s in out["sections"] if s["status"] != "refined"]
            self.assertEqual(len(failed), 1)
            self.assertEqual(failed[0]["id"],
                             [s.id for s in load_run(out["run_id"], Path(td) /
                              "runs").sections if s.status != "refined"][0])
            # original content preserved for the failed section
            st = load_run(out["run_id"], Path(td) / "runs")
            self.assertEqual(st.document["sections"][7],
                             big["sections"][7])

    def test_resume_skips_refined_sections(self):
        big = _big_document(sections=40)
        with tempfile.TemporaryDirectory() as td:
            refiners = [HeuristicRefiner(), HeuristicRefiner("h2")]
            pipe = self._pipe(td, refiners)
            # build a partial run: only first 2 sections refined
            from barrot_agent.refinement import segment_document
            slots = segment_document(big)
            state = RunState(
                run_id="partial-run", source_hash=paths.value_hash(big),
                source_chars=1, objective="partial resume test",
                document=copy.deepcopy(big), original=copy.deepcopy(big),
                sections=[SectionState(id=s.id, path_label=s.path_label)
                          for s in slots], created="t",
                data_classification=pipe.data_classification)
            for s in state.sections[:2]:
                s.status = "refined"
            pipe._commit(state)
            out = pipe.resume("partial-run")
            self.assertEqual(out["disposition"], "complete")
            done = [s for s in out["sections"] if s["status"] == "refined"]
            self.assertEqual(len(done), len(slots))
            # the 2 pre-refined sections were NOT re-refined: their
            # HeuristicRefiner would have normalized "Topic  {i}" names —
            # but we marked them refined without touching the document,
            # so those double spaces must STILL be present
            st = load_run("partial-run", Path(td) / "runs")
            self.assertIn("  ", st.document["sections"][0]["name"])
            self.assertEqual(st.document["sections"][0]["tags"],
                             ["tag0", "tag0"])
            # while the resumed sections genuinely changed
            self.assertEqual(st.document["sections"][8]["name"], "Topic 8")
            self.assertEqual(st.document["sections"][8]["tags"], ["tag8"])
            self.assertGreaterEqual(out["mechanical"]["after"],
                                    out["mechanical"]["before"])

    def test_interrupted_run_resumes_from_disk(self):
        big = _big_document(sections=20)
        with tempfile.TemporaryDirectory() as td:
            pipe = self._pipe(td)
            out = pipe.run(big, objective="x")
            run_id = out["run_id"]
            # simulate interruption: reset half the sections to pending
            st = load_run(run_id, Path(td) / "runs")
            for s in st.sections[len(st.sections) // 2:]:
                s.status = "pending"
            pipe._commit(st)
            out2 = pipe.resume(run_id)
            self.assertEqual(out2["disposition"], "complete")
            self.assertTrue(out2["resumed"])

    def test_learning_history_prevents_repeat_work(self):
        big = _big_document(sections=10)
        with tempfile.TemporaryDirectory() as td:
            pipe = self._pipe(td)
            first = pipe.run(big, objective="dedupe tags")
            self.assertEqual(first["disposition"], "complete")
            again = pipe.run(big, objective="dedupe tags")
            self.assertEqual(again["disposition"], "already_converged")
            forced = pipe.run(big, objective="dedupe tags", force=True)
            self.assertEqual(forced["disposition"], "complete")

    def test_history_record_has_required_fields(self):
        big = _big_document(sections=6)
        with tempfile.TemporaryDirectory() as td:
            self._pipe(td).run(big, objective="obj-x")
            rec = json.loads((Path(td) / "hist.jsonl").read_text()
                             .splitlines()[0])
            for field in ("source_hash", "final_hash", "objective",
                          "data_classification",
                          "patches_applied", "mechanical", "semantic",
                          "regression", "failures_and_corrections",
                          "disposition", "ts", "implementation_version"):
                self.assertIn(field, rec)

    def test_small_document_routes_to_classic_engine(self):
        small = {"a": "x  x", "items": [1, 1, 2]}
        with tempfile.TemporaryDirectory():
            out = refine_document(small, refiners=[HeuristicRefiner()],
                                  ledger=None, data_classification="derived_summary")
            self.assertEqual(out["mode"], "classic")
            report = out["report"]
            self.assertTrue(report.converged)
            self.assertEqual(report.data, {"a": "x x", "items": [1, 2]})

    def test_judge_is_not_the_refining_model(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._pipe(td).run(_big_document(sections=8),
                                     objective="j")
            # offline pipeline has no LLM judge -> deterministic fallback
            self.assertEqual(out["semantic"]["judge"], "deterministic")


    def test_immutable_classification_is_rejected(self):
        with self.assertRaises(ValueError):
            RefinementPipeline([HeuristicRefiner()],
                               data_classification="raw_source")

    def test_refine_document_rejects_immutable_classification(self):
        with self.assertRaises(ValueError):
            refine_document({"summary": "x"},
                            refiners=[HeuristicRefiner()],
                            data_classification="forecast_ledger")

    def test_external_refinement_requires_explicit_opt_in(self):
        refiner = LunaRouteRefiner(
            "test-model", api_key="not-a-real-key",
            allow_external=False, data_classification="public_documentation")
        with self.assertRaises(PermissionError):
            RefinementPipeline([refiner],
                               data_classification="public_documentation",
                               allow_external=False)

    def test_external_run_approval_is_required(self):
        previous_allow = os.environ.get("BARROT_ALLOW_EXTERNAL_REFINEMENT")
        previous_approval = os.environ.get("BARROT_LIVE_REFINEMENT_APPROVED")
        try:
            os.environ["BARROT_ALLOW_EXTERNAL_REFINEMENT"] = "1"
            os.environ.pop("BARROT_LIVE_REFINEMENT_APPROVED", None)
            refiner = LunaRouteRefiner(
                "test-model", api_key="not-a-real-key",
                allow_external=True, data_classification="public_documentation")
            with self.assertRaises(PermissionError):
                RefinementPipeline([refiner],
                                   data_classification="public_documentation",
                                   allow_external=True)
        finally:
            if previous_allow is None:
                os.environ.pop("BARROT_ALLOW_EXTERNAL_REFINEMENT", None)
            else:
                os.environ["BARROT_ALLOW_EXTERNAL_REFINEMENT"] = previous_allow
            if previous_approval is None:
                os.environ.pop("BARROT_LIVE_REFINEMENT_APPROVED", None)
            else:
                os.environ["BARROT_LIVE_REFINEMENT_APPROVED"] = previous_approval

    def test_run_id_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            pipe = self._pipe(td)
            with self.assertRaises(ValueError):
                pipe.run({"safe": True}, run_id="../escape")

    def test_run_id_collision_never_overwrites_prior_state(self):
        with tempfile.TemporaryDirectory() as td:
            pipe = self._pipe(td)
            pipe.run({"safe": True}, run_id="fixed-run")
            with self.assertRaises(FileExistsError):
                pipe.run({"safe": True}, run_id="fixed-run", force=True)

    def test_resume_requires_same_data_classification(self):
        with tempfile.TemporaryDirectory() as td:
            pipe = self._pipe(td)
            result = pipe.run(_big_document(sections=1), run_id="resume-class")
            other = RefinementPipeline(
                [HeuristicRefiner()], runs_dir=Path(td) / "runs",
                history=Path(td) / "history.jsonl",
                data_classification="public_documentation")
            with self.assertRaises(PermissionError):
                other.resume(result["run_id"])


class TestRealRuntime(unittest.TestCase):
    """REAL RUNTIME TIER — hits the live LunaRoute API. Opt-in via
    BARROT_LIVE_REFINEMENT=1; never runs in the default suite."""

    @unittest.skipUnless(LIVE, "real-runtime tier requires three explicit opt-in variables")
    def test_live_section_refine_and_judge(self):
        from barrot_agent.refinement import make_model_refiners
        refiners = make_model_refiners(allow_external=True,
                                       data_classification="public_documentation")
        if len(refiners) < 2:
            self.skipTest("no live pool")
        source = json.loads(
            (REPO_ROOT / "barrot_capability_audit.json").read_text())
        audit = audit_document(source)
        self.assertGreater(audit.total_chars, 24000)
        slots = segment_document(source)
        slot = slots[1]
        out = refiners[0].refine(slot.value, None)
        self.assertIn(out.verdict, ("REFINED", "CONVERGED"))
        if out.data is not None and out.data != slot.value:
            gen = __import__("barrot_agent.refinement.patches",
                             fromlist=["diff_values"]).diff_values(
                slot.value, out.data, "", refiners[0].name)
            for g in gen:
                g.path = slot.absolute_leaf_path(g.path)
            res = apply_patches(copy.deepcopy(source), gen)
            self.assertTrue(res.applied)
        judge = LLMSemanticJudge(refiners[1])
        verdict = judge.evaluate(source, source, objective="identity check")
        self.assertIn(verdict.status, ("improved", "unchanged", "regressed"))
        self.assertNotEqual(judge.name, refiners[0].name)


if __name__ == "__main__":
    unittest.main()