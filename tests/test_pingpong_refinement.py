"""Tests for barrot_agent.refinement — ping-pong model refinement baseline.

All tests are offline/deterministic except the adapter shape test, which
mocks the network layer (no key, no socket).
"""
from __future__ import annotations

import io
import json
import os
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from barrot_agent.refinement import (          # noqa: E402
    DEFAULT_MAX_ROUNDS,
    HeuristicRefiner,
    LunaRouteRefiner,
    PingPongRefiner,
    Refiner,
    RefinementOutput,
    refine_data,
    make_model_refiners,
    scoring,
)


DIRTY = {
    "topic": "signal  analysis",          # double space -> normalizable
    "confidence": "high",
    "confidence2": "low",                 # near-duplicate key (see below)
    "CONFIDENCE": "low",                  # noqa: E501 - semantic dup w/ different value
    "items": ["btc surge", "btc surge", "eth dip"],   # redundancy
    "gap": "",                            # empty leaf
    "vague": "TBD",                       # placeholder
    "nested": {"note": "  spaced  out  ", "n": None},
}


class TestScoring(unittest.TestCase):
    def test_score_deterministic_and_bounded(self):
        a = scoring.score(DIRTY)
        b = scoring.score(DIRTY)
        self.assertEqual(a, b)
        self.assertGreaterEqual(a, 0.0)
        self.assertLessEqual(a, 1.0)

    def test_clean_data_scores_higher_than_dirty(self):
        clean = {
            "topic": "signal analysis",
            "confidence": "high",
            "items": ["btc surge", "eth dip"],
            "gap": "filled",
            "vague": "quantified at 0.82",
            "nested": {"note": "spaced out", "n": 0},
        }
        self.assertGreater(scoring.score(clean), scoring.score(DIRTY))

    def test_breakdown_components_present(self):
        bd = scoring.breakdown(DIRTY)
        for k in ("completeness", "consistency", "specificity", "redundancy", "total"):
            self.assertIn(k, bd)

    def test_sibling_list_items_are_not_conflicts(self):
        # different list items legitimately hold different values
        data = {"items": [{"status": "open"}, {"status": "merged"}]}
        self.assertEqual(scoring.consistency(data), 1.0)

    def test_case_variant_duplicate_keys_conflict(self):
        data = {"confidence": "high", "CONFIDENCE": "low"}
        self.assertLess(scoring.consistency(data), 1.0)
        # agreeing case-variants are not conflicts
        self.assertEqual(
            scoring.consistency({"confidence": "high", "CONFIDENCE": "high"}),
            1.0)


class TestHeuristicRefiner(unittest.TestCase):
    def test_refines_and_then_converges_at_fixed_point(self):
        r = HeuristicRefiner()
        out1 = r.refine(DIRTY, None)
        self.assertEqual(out1.verdict, "REFINED")
        self.assertNotEqual(out1.data, DIRTY)          # something improved
        out2 = r.refine(out1.data, None)
        self.assertEqual(out2.verdict, "CONVERGED")    # nothing left to do
        self.assertEqual(out2.data, out1.data)         # fixed point: identical

    def test_critique_flags_then_clears(self):
        r = HeuristicRefiner()
        c1 = r.critique(DIRTY)
        self.assertEqual(c1.verdict, "REFINE")
        refined = r.refine(DIRTY, c1.critique).data
        c2 = r.critique(refined)
        self.assertEqual(c2.verdict, "CONVERGED")


class _ScriptedRefiner(Refiner):
    """Test double: scripted verdicts, optional data transform."""

    def __init__(self, name, refine_verdicts, critique_verdicts,
                 transform=None):
        self.name = name
        self.rv = list(refine_verdicts)
        self.cv = list(critique_verdicts)
        self.transform = transform or (lambda d: d)
        self.refine_calls = 0
        self.critique_calls = 0

    def refine(self, data, critique=None):
        self.refine_calls += 1
        verdict = self.rv.pop(0) if self.rv else "CONVERGED"
        return RefinementOutput(self.name, "refine", verdict,
                                data=self.transform(data) if verdict == "REFINED" else data)

    def critique(self, data):
        self.critique_calls += 1
        verdict = self.cv.pop(0) if self.cv else "CONVERGED"
        return RefinementOutput(self.name, "critique", verdict,
                                critique="scripted")


class TestEngine(unittest.TestCase):
    def test_alternates_models_and_roles(self):
        # No side ever converges: forces the full dynamic pattern
        # round0: A refine, B critique; round1: B refine, A critique (flip).
        # patience=3 keeps the score-plateau backstop from firing early.
        a = _ScriptedRefiner("A", ["REFINED"] * 8, ["REFINE"] * 8)
        b = _ScriptedRefiner("B", ["REFINED"] * 8, ["REFINE"] * 8)
        report = PingPongRefiner([a, b], ledger=None, max_rounds=2,
                                 patience=3, data_classification="derived_summary").run({"x": 1})
        halves = [(h.actor, h.role) for h in report.history]
        self.assertEqual(halves, [("A", "refine"), ("B", "critique"),
                                  ("B", "refine"), ("A", "critique")])
        self.assertFalse(report.converged)
        self.assertEqual(report.stop_reason, "max_rounds")

    def test_converges_at_fixed_point(self):
        a = _ScriptedRefiner("A", ["REFINED", "CONVERGED"], ["CONVERGED"])
        b = _ScriptedRefiner("B", ["CONVERGED"], ["CONVERGED"])
        report = PingPongRefiner([a, b], ledger=None, data_classification="derived_summary").run({"x": "  y  "})
        self.assertTrue(report.converged)
        self.assertEqual(report.stop_reason, "model_consensus")

    def test_data_only_advances_on_improvement(self):
        data = {"k": "v  double"}                     # heuristic will tighten

        class ImproveOnce(_ScriptedRefiner):
            def refine(self, d, critique=None):
                self.refine_calls += 1
                if self.refine_calls == 1:
                    return RefinementOutput(self.name, "refine", "REFINED",
                                            data={"k": "v double"})
                return RefinementOutput(self.name, "refine", "REFINED", data=d)

        a = ImproveOnce("A", [], [])
        b = _ScriptedRefiner("B", ["REFINED", "REFINED", "REFINED"],
                             ["REFINE", "REFINE", "CONVERGED"])
        report = PingPongRefiner([a, b], ledger=None, max_rounds=6, data_classification="derived_summary").run(data)
        self.assertEqual(report.data, {"k": "v double"})   # improved exactly once
        # the flat follow-up pings trip the objective plateau backstop
        self.assertTrue(report.converged)
        self.assertEqual(report.stop_reason, "score_plateau")

    def test_score_plateau_stops_cosmetic_churn(self):
        # Models keep "improving" (adding churn keys) but the measured score
        # never moves: the plateau backstop must end the loop regardless of
        # model enthusiasm — this is what kills cosmetic byte-churn.
        class Churn(_ScriptedRefiner):
            def refine(self, d, critique=None):
                self.refine_calls += 1
                return RefinementOutput(self.name, "refine", "REFINED",
                                        data={**d, "churn": self.refine_calls})

        a = Churn("A", [], [])
        b = Churn("B", [], [])
        report = PingPongRefiner([a, b], ledger=None, max_rounds=12, data_classification="derived_summary").run({"x": 1})
        self.assertTrue(report.converged)
        self.assertEqual(report.stop_reason, "score_plateau")
        self.assertLess(report.rounds, 12)     # stopped long before the cap

    def test_max_rounds_safety_cap(self):
        class FillOne(_ScriptedRefiner):
            def refine(self, d, critique=None):
                self.refine_calls += 1
                # genuinely improves the measured score every ping (fills one
                # empty leaf), so the plateau backstop never fires and the
                # hard cap is what stops the loop
                nd = dict(d)
                for k in ("a", "b", "c", "d", "e", "f", "g", "h"):
                    if nd.get(k) == "":
                        nd[k] = f"filled-{self.refine_calls}"
                        break
                return RefinementOutput(self.name, "refine", "REFINED", data=nd)

        a = FillOne("A", [], [])
        b = _ScriptedRefiner("B", ["REFINE"] * 99, ["REFINE"] * 99)
        report = PingPongRefiner([a, b], ledger=None, max_rounds=4, data_classification="derived_summary").run(
            {"a": "", "b": "", "c": "", "d": ""})
        self.assertFalse(report.converged)
        self.assertEqual(report.stop_reason, "max_rounds")
        self.assertEqual(len(report.history), 8)   # 4 rounds x (ping + pong)
        self.assertLessEqual(len(report.history), DEFAULT_MAX_ROUNDS * 2)

    def test_failure_circuit_breaker(self):
        class Broken(_ScriptedRefiner):
            def refine(self, d, critique=None):
                return RefinementOutput(self.name, "refine", "FAILED",
                                        data=None, notes="api down")

        a = Broken("A", [], [])
        b = Broken("B", [], [])
        report = PingPongRefiner([a, b], ledger=None, data_classification="derived_summary").run({"x": 1})
        self.assertFalse(report.converged)
        self.assertEqual(report.stop_reason, "pool_exhausted")
        failed = [h for h in report.history if h.verdict == "FAILED"]
        self.assertEqual(len(failed), 2)      # one full pool rotation, then stop

    def test_dead_model_hands_paddle_to_next(self):
        class Dead(_ScriptedRefiner):
            def refine(self, d, critique=None):
                return RefinementOutput(self.name, "refine", "FAILED",
                                        data=None, notes="api down")

        dead = Dead("dead", [], [])
        alive = _ScriptedRefiner("alive", ["REFINED", "CONVERGED"],
                                 ["CONVERGED"])
        report = PingPongRefiner([dead, alive], ledger=None, data_classification="derived_summary").run({"x": "  y "})
        self.assertTrue(report.converged)
        self.assertIn("alive", report.models_used)
        # the dead model's FAILED round is ledgered, then the pool rotated
        self.assertTrue(any(h.actor == "dead" and h.verdict == "FAILED"
                            for h in report.history))

    def test_ledger_jsonl_written(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            led = Path(td) / "log.jsonl"
            a = _ScriptedRefiner("A", ["REFINED", "CONVERGED"], ["CONVERGED"])
            b = _ScriptedRefiner("B", ["CONVERGED"], ["CONVERGED"])
            PingPongRefiner([a, b], ledger=led, data_classification="derived_summary").run({"x": "  y  "})
            lines = led.read_text().strip().splitlines()
            self.assertTrue(lines)
            rows = [json.loads(line) for line in lines]
            self.assertTrue(all({"ts", "round", "actor", "role",
                                 "verdict"} <= set(r) for r in rows))
            self.assertEqual({r["role"] for r in rows}, {"refine", "critique"})

    def test_needs_refiner(self):
        with self.assertRaises(ValueError):
            PingPongRefiner([])


class TestBaselineAPI(unittest.TestCase):
    def test_refine_data_dict_fixed_point(self):
        report = refine_data(DIRTY,
                             refiners=[HeuristicRefiner(), HeuristicRefiner("heuristic2")],
                             ledger=None, data_classification="derived_summary")
        self.assertTrue(report.converged)
        self.assertGreaterEqual(report.score_end, report.score_start)
        # converged data re-refines to identical output (true fixed point)
        again = refine_data(report.data,
                            refiners=[HeuristicRefiner(), HeuristicRefiner("h2")],
                            ledger=None, data_classification="derived_summary")
        self.assertEqual(again.data, report.data)

    def test_refine_data_string_and_list(self):
        r1 = refine_data("  spaced   out  ", refiners=[HeuristicRefiner()], ledger=None, data_classification="derived_summary")
        self.assertEqual(r1.data, "spaced out")
        r2 = refine_data(["a", "a", "b", "", ""], refiners=[HeuristicRefiner()], ledger=None, data_classification="derived_summary")
        self.assertEqual(r2.data, ["a", "b"])

    def test_default_refinement_is_offline_even_when_lunaroute_key_exists(self):
        with mock.patch.dict(os.environ, {"LUNAROUTE_API_KEY": "test-key", "BARROT_ALLOW_EXTERNAL_REFINEMENT": "1"}), \
             mock.patch("urllib.request.urlopen", side_effect=AssertionError("network must stay closed")):
            report = refine_data(DIRTY, data_classification="derived_summary", ledger=None)
        self.assertTrue(report.converged)

    def test_unknown_and_immutable_data_classes_are_rejected(self):
        for classification in ("unknown", "raw_source", "source_receipt", "feature_snapshot",
                               "feature_store", "event_timeline", "forecast_ledger",
                               "market_data", "credentials", "secrets", "user_private"):
            with self.subTest(classification=classification):
                with self.assertRaises(ValueError):
                    refine_data({"value": "x"}, data_classification=classification, ledger=None)

    def test_external_refinement_requires_explicit_caller_opt_in(self):
        refiner = LunaRouteRefiner("glm-5.3-flash", api_key="test-key",
                                   allow_external=True, data_classification="public_derived_summary")
        with mock.patch.dict(os.environ, {"BARROT_ALLOW_EXTERNAL_REFINEMENT": "1"}):
            with self.assertRaises(PermissionError):
                refine_data({"value": "public"}, refiners=[refiner],
                            data_classification="public_derived_summary", ledger=None)

    def test_external_refinement_requires_environment_gate(self):
        refiner = LunaRouteRefiner("glm-5.3-flash", api_key="test-key",
                                   allow_external=True, data_classification="public_derived_summary")
        with mock.patch.dict(os.environ, {"BARROT_ALLOW_EXTERNAL_REFINEMENT": "0"}):
            with self.assertRaises(PermissionError):
                refine_data({"value": "public"}, refiners=[refiner],
                            data_classification="public_derived_summary",
                            allow_external=True, ledger=None)

    def test_model_refiner_factory_is_disabled_by_default(self):
        with mock.patch.dict(os.environ, {"LUNAROUTE_API_KEY": "test-key", "BARROT_ALLOW_EXTERNAL_REFINEMENT": "1"}):
            self.assertEqual(make_model_refiners(), [])

    def test_model_refiner_factory_requires_public_classification(self):
        with mock.patch.dict(os.environ, {"LUNAROUTE_API_KEY": "test-key", "BARROT_ALLOW_EXTERNAL_REFINEMENT": "1"}):
            self.assertEqual(make_model_refiners(allow_external=True, data_classification="derived_summary"), [])

    def test_file_roundtrip(self):
        import tempfile
        from barrot_agent.refinement import refine_json_file
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "doc.json"
            p.write_text(json.dumps({"a": "x  x", "dup": [1, 1, 2]}))
            report = refine_json_file(p, refiners=[HeuristicRefiner()], ledger=None, data_classification="derived_summary")
            self.assertTrue(report.converged)
            reloaded = json.loads(p.read_text())
            self.assertEqual(reloaded, {"a": "x x", "dup": [1, 2]})


class TestLunaRouteAdapterShape(unittest.TestCase):
    def setUp(self):
        # These adapter tests mock every HTTP request. Satisfy both explicit external
        # refinement gates without enabling any real provider call.
        self._external_gate = mock.patch.dict(os.environ, {
            "BARROT_ALLOW_EXTERNAL_REFINEMENT": "1",
            "BARROT_LIVE_REFINEMENT_APPROVED": "1",
        })
        self._external_gate.start()
        self.addCleanup(self._external_gate.stop)

    def test_request_shape_and_parsing(self):
        captured = {}

        class FakeResp(io.StringIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            status = 200

        payload = {"choices": [{"message": {
            "content": json.dumps({"data": {"a": 1}, "verdict": "REFINED",
                                   "notes": "ok"}),
            "reasoning_content": ""}}]}

        def fake_urlopen(req, timeout=0):
            captured["url"] = req.full_url
            captured["headers"] = dict(req.headers)
            captured["body"] = json.loads(req.data.decode())
            return FakeResp(json.dumps(payload))

        r = LunaRouteRefiner("glm-5.3-flash", api_key="test-key-123", allow_external=True, data_classification="public_derived_summary")
        with mock.patch("urllib.request.urlopen", fake_urlopen):
            out = r.refine({"a": 1}, critique="fix the thing")
        self.assertEqual(out.verdict, "REFINED")
        self.assertEqual(out.data, {"a": 1})
        self.assertIn("/chat/completions", captured["url"])
        self.assertEqual(captured["body"]["model"], "glm-5.3-flash")
        # the key must go to the API, never into the URL
        auth = captured["headers"].get("Authorization", "")
        self.assertTrue(auth.startswith("Bearer "))
        self.assertNotIn("test-key-123", captured["url"])

    def test_no_key_means_unavailable(self):
        r = LunaRouteRefiner("glm-5.3-flash", api_key="")
        self.assertFalse(r.available)

    def test_garbage_output_is_failed_not_fatal(self):
        class FakeResp(io.StringIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        payload = {"choices": [{"message": {"content": "I refuse to emit json"}}]}

        def fake_urlopen(req, timeout=0):
            return FakeResp(json.dumps(payload))

        r = LunaRouteRefiner("glm-5.3-flash", api_key="k", allow_external=True, data_classification="public_derived_summary")
        with mock.patch("urllib.request.urlopen", fake_urlopen):
            out = r.refine({"a": 1}, critique=None)
        self.assertEqual(out.verdict, "FAILED")

    def test_truncated_response_retried_with_doubled_budget(self):
        calls = []

        class FakeResp(io.StringIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def truncated_then_ok(req, timeout=0):
            body = json.loads(req.data.decode())
            calls.append(body["max_tokens"])
            if len(calls) == 1:               # cut off mid-JSON
                return FakeResp(json.dumps({"choices": [{
                    "message": {"content": '{"data": {"a": 1}, "verdict": "REFI'},
                    "finish_reason": "length"}]}))
            return FakeResp(json.dumps({"choices": [{
                "message": {"content": json.dumps(
                    {"data": {"a": 2}, "verdict": "REFINED", "notes": "ok"}),
                    "reasoning_content": ""},
                "finish_reason": "stop"}]}))

        r = LunaRouteRefiner("deepseek-4.1-flash", api_key="k", allow_external=True, data_classification="public_derived_summary")
        with mock.patch("urllib.request.urlopen", truncated_then_ok):
            out = r.refine({"a": 1}, critique=None)
        self.assertEqual(out.verdict, "REFINED")
        self.assertEqual(out.data, {"a": 2})
        self.assertEqual(len(calls), 2)
        self.assertGreater(calls[1], calls[0])     # doubled budget on retry

    def test_secret_like_payload_is_blocked_before_network(self):
        r = LunaRouteRefiner("glm-5.3-flash", api_key="test-key",
                             allow_external=True, data_classification="public_derived_summary")
        out = r.refine({"token": "ghp_" + "a" * 32}, critique=None)
        self.assertEqual(out.verdict, "FAILED")
        self.assertIn("secret-like", out.notes)

    def test_oversized_payload_is_rejected_without_truncation(self):
        r = LunaRouteRefiner("glm-5.3-flash", api_key="test-key",
                             allow_external=True, data_classification="public_derived_summary")
        out = r.refine({"text": "x" * 25_000}, critique=None)
        self.assertEqual(out.verdict, "FAILED")
        self.assertIn("without truncation", out.notes)

    def test_extract_json_handles_fences(self):
        text = 'Sure!\n```json\n{"data": [1], "verdict": "REFINED", "notes": "n"}\n```'
        self.assertEqual(LunaRouteRefiner._extract_json(text)["data"], [1])

    def test_transient_errors_retried_with_backoff(self):
        attempts = {"n": 0}

        class FakeResp(io.StringIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        payload = {"choices": [{"message": {
            "content": json.dumps({"data": {"a": 2}, "verdict": "REFINED",
                                   "notes": "ok"})}}]}

        def flaky_urlopen(req, timeout=0):
            attempts["n"] += 1
            if attempts["n"] <= 2:            # two transient 429s, then success
                raise urllib.error.HTTPError(req.full_url, 429,
                                             "slow down", {}, None)
            return FakeResp(json.dumps(payload))

        r = LunaRouteRefiner("deepseek-4.1-flash", api_key="k", allow_external=True, data_classification="public_derived_summary")
        with mock.patch("urllib.request.urlopen", flaky_urlopen), \
                mock.patch("barrot_agent.refinement.refiners.time.sleep") as sleeper:
            out = r.refine({"a": 1}, critique=None)
        self.assertEqual(out.verdict, "REFINED")
        self.assertEqual(out.data, {"a": 2})
        self.assertEqual(attempts["n"], 3)     # retried up to 3 attempts total
        self.assertEqual(sleeper.call_count, 2)  # backoff between attempts

    def test_permanent_http_error_not_retried(self):
        def forbidden_urlopen(req, timeout=0):
            raise urllib.error.HTTPError(req.full_url, 403,
                                         "forbidden", {}, None)

        r = LunaRouteRefiner("deepseek-4.1-flash", api_key="k", allow_external=True, data_classification="public_derived_summary")
        with mock.patch("urllib.request.urlopen", forbidden_urlopen), \
                mock.patch("barrot_agent.refinement.refiners.time.sleep") as sleeper:
            out = r.refine({"a": 1}, critique=None)
        self.assertEqual(out.verdict, "FAILED")   # surfaced, not retried
        sleeper.assert_not_called()


if __name__ == "__main__":
    unittest.main()
