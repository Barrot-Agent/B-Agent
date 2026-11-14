"""Semantic evaluation layer for ping-pong refinement.

The mechanical scorer (scoring.py) measures structure. This module measures
MEANING — and never inflates: the deterministic core can only certify
non-regression or flag regressions; claiming "improved" on semantic grounds
requires an independent judge that passed calibration.

Four separate results, per standing directive:
  A. mechanical score  (scoring.py, unchanged)
  B. semantic score    (this module: 0..1)
  C. regression score  (1.0 = no regressions detected)
  D. overall status    ("improved" | "unchanged" | "regressed")

Independent checks: the judge must be a DIFFERENT model than the refiner
(the pipeline wires the critic side as judge), and every judge must pass
CALIBRATION_CASES — reference examples with known expected verdicts — before
its "improved" verdicts are trusted. An uncalibrated judge downgrades to the
deterministic core (which cannot claim improvement, only non-regression).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from . import paths, scoring

_TOKEN = re.compile(r"[a-z0-9][a-z0-9_\-]{2,}")
_STOP = {"the", "and", "for", "with", "this", "that", "from", "are", "was",
         "were", "has", "have", "had", "not", "but", "all", "any", "can",
         "may", "its", "his", "her", "our", "their", "you", "your", "who",
         "what", "when", "how", "why", "into", "onto", "over", "under",
         "than", "then", "also", "been", "being", "each", "which", "will",
         "would", "could", "should", "shall", "might"}
#: hedge/filler vocabulary — losing these is not meaning loss; concrete
#: replacements for vague hedges are exactly what good refinement produces
_HEDGES = {"utilize", "utilizes", "utilized", "utilizing", "effectively",
           "basically", "various", "some", "most", "several", "generally",
           "usually", "often", "sometimes", "good", "nice", "fine", "okay",
           "adequate", "sufficient", "reasonable", "etc", "things", "stuff",
           "aspects", "areas", "factors", "manner", "mechanisms", "scenarios"}


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN.findall(text.lower()) if t not in _STOP}


def _numeric_facts(data: Any) -> dict[str, float]:
    """Numeric leaves keyed by the normalized semantic key of their path."""
    facts: dict[str, float] = {}
    for p, v in paths.walk_leaves(data):
        if p.endswith("/") or isinstance(v, bool) \
                or not isinstance(v, (int, float)):
            continue
        key = p.rsplit(".", 1)[-1].lower().replace("_", "").replace("-", "")
        if key:
            facts.setdefault(key, float(v))
    return facts


def _content_terms(data: Any) -> set[str]:
    terms: set[str] = set()
    for p, v in paths.walk_leaves(data):
        if p.endswith("/") or not isinstance(v, str):
            continue
        terms |= _tokens(v)
    return terms


def _keys(data: Any) -> set[str]:
    keys = set()
    for p, v in paths.walk_leaves(data):
        if not p.endswith("/"):
            keys.add(p.rsplit(".", 1)[-1].lower()
                     .replace("_", "").replace("-", ""))
    return keys


@dataclass
class SemanticVerdict:
    mechanical: float = 0.0
    semantic: float = 0.0
    regression: float = 1.0
    status: str = "unchanged"        # improved | unchanged | regressed
    judge: str = "deterministic"
    calibrated: bool = True
    dimensions: dict = field(default_factory=dict)
    regressions: list = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        return {**self.__dict__}


# ------------------------------------------------------- deterministic core
def heuristic_semantic_eval(original: Any, refined: Any,
                            objective: str = "") -> SemanticVerdict:
    """Deterministic, repeatable, offline semantic evaluation.

    Honest by construction: it detects MEANING LOSS, FACTUAL DRIFT,
    CONTRADICTIONS and MISSING CONTENT — it never claims improvement it
    cannot prove, so its best case is status "unchanged" (mechanical gains
    are what can upgrade that to "improved")."""
    orig_terms = _content_terms(original) - _HEDGES
    ref_terms = _content_terms(refined)
    coverage = (len(orig_terms & ref_terms) / len(orig_terms)) \
        if orig_terms else 1.0

    orig_facts = _numeric_facts(original)
    ref_facts = _numeric_facts(refined)
    changed = [k for k in orig_facts
               if k in ref_facts and abs(orig_facts[k] - ref_facts[k]) > 1e-12]
    removed = [k for k in orig_facts if k not in ref_facts]

    orig_keys = _keys(original)
    ref_keys = _keys(refined)
    key_coverage = (len(orig_keys & ref_keys) / len(orig_keys)) \
        if orig_keys else 1.0

    vague_orig = _vague_count(original)
    vague_ref = _vague_count(refined)

    regressions: list[str] = []
    #: conservative loss line: the deterministic core flags MEANING LOSS only
    #: when >40% of content terms vanish; subtler phrasing shifts are the
    #: independent judge's job (this core must never cry wolf)
    MEANING_LOSS_LINE = 0.60
    if coverage < MEANING_LOSS_LINE:
        regressions.append(f"meaning_coverage={coverage:.3f}")
    for k in changed:
        regressions.append(f"numeric_changed:{k}")
    for k in removed:
        regressions.append(f"numeric_removed:{k}")

    regression_score = max(0.0, 1.0
                           - 0.60 * max(0.0, (MEANING_LOSS_LINE - coverage)
                                        / MEANING_LOSS_LINE)
                           - 0.15 * len(changed)
                           - 0.075 * len(removed)
                           - 0.10 * (1.0 - key_coverage))

    structure_ok = _same_root_shape(original, refined)
    if not structure_ok:
        regressions.append("root_shape_changed")
        regression_score = min(regression_score, 0.5)

    semantic = round(min(1.0, 0.30 * coverage
                         + 0.25 * (1.0 if not changed else
                                   max(0.0, 1.0 - len(changed) / max(1, len(orig_facts))))
                         + 0.20 * key_coverage
                         + 0.15 * (1.0 if vague_ref <= vague_orig
                                   else 0.5)
                         + 0.10 * (1.0 if structure_ok else 0.0)
                         + (0.05 if not removed else 0.0)), 6)

    status = "regressed" if regression_score < 0.90 else "unchanged"
    return SemanticVerdict(
        mechanical=scoring.score(refined),
        semantic=semantic,
        regression=round(regression_score, 6),
        status=status,
        judge="deterministic",
        calibrated=True,
        dimensions={
            "meaning_preservation": round(coverage, 6),
            "factual_consistency": round(
                1.0 if not changed else
                max(0.0, 1.0 - len(changed) / max(1, len(orig_facts))), 6),
            "completeness": round(key_coverage, 6),
            "clarity": round(1.0 if vague_ref <= vague_orig else 0.5, 6),
            "contradiction_free": round(
                1.0 if not changed else
                max(0.0, 1.0 - len(changed) / max(1, len(orig_facts))), 6),
            "structure": round(1.0 if structure_ok else 0.0, 6),
        },
        regressions=regressions[:20],
        notes=f"objective={objective[:80]}" if objective else "")


def _vague_count(data: Any) -> int:
    vague = {"tbd", "todo", "n/a", "na", "none", "unknown", "lorem ipsum",
             "xxx", "?", "-", "tba"}
    n = 0
    for _, v in paths.walk_leaves(data):
        if isinstance(v, str) and v.strip().lower() in vague:
            n += 1
    return n


def _same_root_shape(a: Any, b: Any) -> bool:
    if isinstance(a, dict) != isinstance(b, dict):
        return False
    if isinstance(a, list) != isinstance(b, list):
        return False
    return True


# --------------------------------------------------------------- LLM judge
JUDGE_SYSTEM = (
    "You are an INDEPENDENT semantic evaluator. Compare ORIGINAL and "
    "REFINED data for the stated objective. You did NOT produce the "
    "refinement; do not favor it. Score strictly on evidence in the texts; "
    "when unsure, score CONSERVATIVELY (never inflate). Detect regressions "
    "explicitly. Reply with STRICT JSON only: "
    '{"dimensions": {"meaning_preservation": 0-10, "factual_consistency": '
    '0-10, "reasoning_quality": 0-10, "logical_coherence": 0-10, '
    '"completeness": 0-10, "clarity": 0-10, "contradiction_free": 0-10, '
    '"instruction_adherence": 0-10, "technical_preservation": 0-10}, '
    '"overall_improvement": -5 to 5, "regressions": ["each concrete '
    'regression"], "status": "improved"|"unchanged"|"regressed", '
    '"notes": "<=200 chars"} '
    "status=improved ONLY if the refinement genuinely advances the objective "
    "with zero regressions; regressed if meaning, facts, or requirements "
    "were lost or contradicted."
)


class LLMSemanticJudge:
    """Independent semantic judge backed by a chat model. MUST NOT be the
    same model/refiner that produced the refinement — the pipeline enforces
    judge.name != refiner.name. Calibration runs once and is cached;
    uncalibrated judges cannot vote "improved"."""

    is_llm = True

    def __init__(self, refiner, max_chars: int = 20000):
        self.refiner = refiner
        self.max_chars = max_chars
        self.name = f"judge:{refiner.name}"
        self._trusted: bool | None = None

    def ensure_calibrated(self) -> bool:
        if self._trusted is None:
            self._trusted, self._failures = calibrate(self)
        return self._trusted

    def evaluate(self, original: Any, refined: Any,
                 objective: str = "") -> SemanticVerdict:
        user = (f"OBJECTIVE: {objective or '(none given)'}\n\n"
                f"ORIGINAL:\n{paths.canonical(original)[:self.max_chars]}\n\n"
                f"REFINED:\n{paths.canonical(refined)[:self.max_chars]}")
        try:
            parsed, _finish = self.refiner.complete_json(JUDGE_SYSTEM, user)
        except Exception as exc:                     # noqa: BLE001 - judge
            return SemanticVerdict(                  # failure = no verdict
                judge=self.name, calibrated=False,
                notes=f"judge error: {type(exc).__name__}"[:120])
        if not parsed or "dimensions" not in parsed:
            return SemanticVerdict(judge=self.name, calibrated=False,
                                   notes="judge unparseable output")
        dims = {k: max(0, min(10, float(v)))
                for k, v in parsed.get("dimensions", {}).items()
                if isinstance(v, (int, float))}
        if not dims:
            return SemanticVerdict(judge=self.name, calibrated=False,
                                   notes="judge dims missing")
        semantic = round(sum(dims.values()) / (10 * len(dims)), 6)
        regressions = [str(r)[:120]
                       for r in parsed.get("regressions", [])][:20]
        raw_status = str(parsed.get("status", "unchanged")).lower()
        status = raw_status if raw_status in ("improved", "unchanged",
                                              "regressed") else "unchanged"
        regression = round(max(0.0, 1.0 - 0.15 * len(regressions)), 6)
        base = heuristic_semantic_eval(original, refined, objective)
        # deterministic veto: the judge cannot paper over detected loss
        if base.regression < 0.90:
            status = "regressed"
        return SemanticVerdict(
            mechanical=base.mechanical, semantic=semantic,
            regression=min(base.regression, regression),
            status=status, judge=self.name, calibrated=True,
            dimensions={**base.dimensions,
                        **{f"judge_{k}": round(v / 10, 6)
                           for k, v in dims.items()}},
            regressions=list(dict.fromkeys(regressions + base.regressions))[:20],
            notes=str(parsed.get("notes", ""))[:200])


# ------------------------------------------------------------- calibration
#: reference examples with known expected verdicts (repeatable evaluation
#: cases). Every judge must classify these correctly before it is trusted.
CALIBRATION_CASES: list[dict] = [
    {
        "name": "specificity_improvement",
        "original": {"recommendation":
                     "the system utilizes caching mechanisms effectively "
                     "in most scenarios and should be continued"},
        "refined": {"recommendation":
                    "the system uses Redis caching; measured hit rate 87% "
                    "across 1200 requests (2026-11-01 benchmark)"},
        "expected_status": "improved",
    },
    {
        "name": "meaning_loss_regression",
        "original": {"requirement":
                     "all payments must be signed with HMAC-SHA256 and "
                     "replay-protected with a 5 minute nonce window",
                     "timeout_seconds": 30},
        "refined": {"requirement":
                    "payments are signed and replay-protected",
                    "timeout_seconds": 30},
        "expected_status": "regressed",
    },
    {
        "name": "cosmetic_only",
        "original": {"status": "operational  ", "count": 12},
        "refined": {"status": "operational", "count": 12},
        "expected_status": "unchanged",
    },
]


def calibrate(evaluator) -> tuple[bool, list[str]]:
    """Run the reference cases through an evaluator (LLM judge or
    deterministic core). Returns (trusted, failures). An LLM judge must get
    ALL cases right; the deterministic core is trusted unless it MISSES a
    regression (false negative — the dangerous direction)."""
    failures: list[str] = []

    def run(case) -> Any:
        if hasattr(evaluator, "evaluate"):
            return evaluator.evaluate(case["original"], case["refined"])
        return evaluator(case["original"], case["refined"])

    for case in CALIBRATION_CASES:
        v = run(case)
        if getattr(evaluator, "is_llm", False):
            if v.status != case["expected_status"]:
                failures.append(f"{case['name']}: got {v.status}, "
                                f"expected {case['expected_status']}")
        else:
            expected_regressed = case["expected_status"] == "regressed"
            got_regressed = v.status == "regressed"
            if expected_regressed and not got_regressed:
                failures.append(f"{case['name']}: regression MISSED")
    return (not failures), failures


# ------------------------------------------------------------------ facade
def evaluate(original: Any, refined: Any, judge=None,
             objective: str = "", mechanical_before: float | None = None
             ) -> SemanticVerdict:
    """Top-level evaluation. Combines the deterministic core with an
    optional calibrated LLM judge:
      - any detected regression (either side) => status "regressed";
      - "improved" requires a CALIBRATED judge (or a mechanical gain when
        no judge is configured) with zero deterministic regressions."""
    base = heuristic_semantic_eval(original, refined, objective)
    if judge is None:
        base.status = "regressed" if base.regression < 0.90 else (
            "improved" if mechanical_before is not None
            and base.mechanical > mechanical_before + 1e-4 else "unchanged")
        return base
    # trust gate: a judge votes "improved" only after passing calibration
    # against the reference cases (cached on the judge when supported)
    if hasattr(judge, "ensure_calibrated"):
        trusted = judge.ensure_calibrated()
    else:
        trusted, _failures = calibrate(judge)
    verdict = judge.evaluate(original, refined, objective)
    verdict.calibrated = bool(trusted) and bool(verdict.calibrated)
    # fuse: worst status wins; semantic = judge's when calibrated, else base
    fused_status = "regressed"
    if base.regression >= 0.90 and verdict.regression >= 0.90:
        if verdict.calibrated and verdict.status == "improved":
            fused_status = "improved"
        elif verdict.status == "regressed":
            fused_status = "regressed"
        else:
            fused_status = "unchanged"
    return SemanticVerdict(
        mechanical=verdict.mechanical or base.mechanical,
        semantic=verdict.semantic if verdict.calibrated else base.semantic,
        regression=min(base.regression, verdict.regression),
        status=fused_status,
        judge=verdict.judge,
        calibrated=verdict.calibrated,
        dimensions=verdict.dimensions,
        regressions=list(dict.fromkeys(
            verdict.regressions + base.regressions))[:20],
        notes=verdict.notes or base.notes)
