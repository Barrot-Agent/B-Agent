"""Deterministic hype filter for video, podcast and TED-talk ingestion.

Implements the five checks recorded in
``docs/VIDEO_EXTRACTION_2026-11-15.md`` (lines 173-179):

1. ``benchmark_caveat``  - the benchmark's own caveat must survive the framing.
2. ``harness_disclosure`` - scores must name the harness/scaffold that produced them.
3. ``cost_and_budget``   - claims must report cost or token/latency budget, not only accuracy.
4. ``funding_vs_intent`` - funding may be stated as fact; intent must not be.
5. ``beneficiary``       - emotional framing must name who benefits from it.

A media record that fails two or more applicable checks is tagged ``HYPE`` and is
refused by :func:`barrot_agent.infinite_ingest.refiner.refine_capability`.

This is a lexical auditor, not a fact-checker.  It reads the transcript for the
presence or absence of disconfirming language.  ``HypeCheck.reason`` always says
which evidence produced the verdict, and ``evidence`` returns the matched spans so
a human can review the call.  It never rewrites or summarises the source.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

HYPE_THRESHOLD = 2
HYPE_TAG = "HYPE"
PASS_TAG = "OK"

MEDIA_KINDS = frozenset(
    {"video", "youtube", "podcast", "ted", "tedtalk", "ted_talk", "audiobook", "transcript"}
)


# --------------------------------------------------------------------------- #
# pattern helpers
# --------------------------------------------------------------------------- #


def _compile(*patterns: str) -> re.Pattern[str]:
    """Compile alternatives into one case-insensitive pattern."""
    return re.compile("|".join(f"(?:{p})" for p in patterns), re.IGNORECASE)


def _norm(text: str) -> str:
    """Collapse whitespace and lowercase, preserving word boundaries."""
    return " ".join((text or "").split()).lower()


def _find(pattern: re.Pattern[str], text: str, limit: int = 3) -> list[str]:
    """Unique matched spans, in order of appearance."""
    out: list[str] = []
    for match in pattern.finditer(text):
        span = " ".join(match.group(0).split())
        if span and span not in out:
            out.append(span)
        if len(out) >= limit:
            break
    return out


_SENTENCE = re.compile(r"[^.!?]+[.!?]?")


def _sentence_at(text: str, position: int) -> str:
    """Sentence containing ``position`` (approximate, punctuation based)."""
    for match in _SENTENCE.finditer(text):
        if match.start() <= position < match.end():
            return match.group(0)
    return text


# --------------------------------------------------------------------------- #
# vocabularies
# --------------------------------------------------------------------------- #

_SCORE_CLAIM = _compile(
    r"\b\d+(?:\.\d+)?\s?%",
    r"\bbenchmarks?\b",
    r"\bleaderboards?\b",
    r"\bstate[- ]of[- ]the[- ]art\b",
    r"\bsota\b",
    r"\bbest average score\b",
    r"\boutperforms?\b",
    r"\boutperformed\b",
)

_OVERCLAIM = _compile(
    r"\bagi is here\b",
    r"\bwe(?:'ve| have) entered agi\b",
    r"\bentered the agi era\b",
    r"\bwe are (?:now )?in the agi era\b",
    r"\bofficially (?:agi|artificial general intelligence)\b",
    r"\bsolved (?:ai |artificial )?(?:memory|reasoning|intelligence|language)\b",
    r"\bsuperhuman\b",
    r"\bhuman[- ]level\b",
    r"\bbeats? (?:the )?humans?\b",
    r"\bthe hard part is over\b",
    r"\bgame over\b",
    r"\bgeneral intelligence (?:is|has) (?:arrived|been achieved)\b",
)

_CAVEAT = _compile(
    r"\bnot proof\b",
    r"\bisn't proof\b",
    r"\bdoesn't prove\b",
    r"\bdoes not prove\b",
    r"\bno proof\b",
    r"\bcaveats?\b",
    r"\bfine print\b",
    r"\bdoesn't mean\b",
    r"\bdoes not mean\b",
    r"\blimited to\b",
    r"\bnarrow\b",
    r"\bclosed (?:rule|world|environment)",
    r"\btoy (?:task|example|benchmark)\b",
    r"\bsynthetic\b",
    r"\bpreliminary\b",
    r"\bjust a research\b",
    r"\bsmall sample\b",
    r"\bmy tests were\b",
    r"\bmy test was\b",
    r"\bdoesn't generali[sz]e\b",
    r"\bdoes not generali[sz]e\b",
    r"\bnext test\b",
    r"\bnot a general\b",
    r"\bhold(?:s|ing)? up\b",
    r"\breproduced\b",
    r"\bput (?:it|this) to the test\b",
    r"\bown tests?\b",
    r"\bfailed\b",
    r"\bwrong\b",
    r"\bhallucinat\w*",
)

_HARNESS = _compile(
    r"\bharness\b",
    r"\bscaffold\w*",
    r"\bsetup\b",
    r"\bsystem prompt\b",
    r"\bown tests?\b",
    r"\bown data\b",
    r"\bcustom data\b",
    r"\bmy tests?\b",
    r"\btested (?:it|this)\b",
    r"\breproduced\b",
    r"\bprovider adapter\b",
    r"\bstandard harness\b",
    r"\bsemi[- ]private\b",
    r"\bprivate (?:set|split)\b",
    r"\bpublic (?:set|split)\b",
    r"\benvironment\b",
    r"\btool use\b",
    r"\bcontext window\b",
    r"\b(?:chain|train) of thought\b",
    r"\bbarebones\b",
    r"\bcustom tools?\b",
)

_PERF_CLAIM = _compile(
    r"\b\d+(?:\.\d+)?\s?%",
    r"\bscores?\b",
    r"\bfaster\b",
    r"\bspeed\b",
    r"\bstate[- ]of[- ]the[- ]art\b",
    r"\bbeats?\b",
    r"\boutperforms?\b",
    r"\bbest average\b",
    r"\bmore accurate\b",
    r"\baccuracy\b",
)

_BUDGET = _compile(
    r"\$",
    r"\bcosts?\b",
    r"\bpric(?:e|ing)\b",
    r"\bcheaper\b",
    r"\bexpensive\b",
    r"\btokens?\b",
    r"\bbudget\b",
    r"\blatency\b",
    r"\b\d+(?:\.\d+)?\s*(?:seconds?|secs?|ms|milliseconds?|minutes?|hours?)\b",
    r"\bgpus?\b",
    r"\b[hb]\d{3}\b",
    r"\bcompute\b",
    r"\bflops\b",
    r"\bper task\b",
    r"\bruntime\b",
)

_FUNDING = _compile(
    r"\bfunded\b",
    r"\bfunding\b",
    r"\bfunds?\b",
    r"\bgrant\b",
    r"\binvestors?\b",
    r"\bbacked by\b",
    r"\bmoney behind\b",
    r"\bdonors?\b",
    r"\bphilanthrop\w*",
    r"\blobby\w*",
    r"\bpaid by\b",
    r"\bbankrolled\b",
)

_INTENT_ASSERT = _compile(
    r"\bpsyop\b",
    r"\bbuilt to (?:make|scare|frighten|push|drive)\b",
    r"\bdesigned to (?:make|scare|frighten|push|drive)\b",
    r"\bengineered to\b",
    r"\bmanufactured\b",
    r"\bcoordinated campaign\b",
    r"\bastroturf\w*",
    r"\bpaid to\b",
    r"\bthey want you to\b",
    r"\bthe whole point (?:is|was)\b",
    r"\bdeliberately\b",
)

_HEDGE = _compile(
    r"\bmay\b",
    r"\bmight\b",
    r"\bcould\b",
    r"\bpossibly\b",
    r"\bappears? to\b",
    r"\bseems? to\b",
    r"\ballegedly\b",
    r"\breportedly\b",
    r"\bunclear\b",
    r"\bi think\b",
    r"\bin my opinion\b",
    r"\bcan'?t prove\b",
    r"\bcannot prove\b",
    r"\bunverified\b",
)

_EMOTION = _compile(
    r"\bshocking\b",
    r"\binsane\b",
    r"\bunbelievable\b",
    r"\byou won't believe\b",
    r"\bchills\b",
    r"\bterrified\b",
    r"\bterrifying\b",
    r"\bnightmare\b",
    r"\bdestroyed\b",
    r"\bobliterated\b",
    r"\bgame over\b",
    r"\bunstoppable\b",
    r"\bsecret\b",
    r"\bthey don't want you to know\b",
    r"\bwake up\b",
    r"\bscam\b",
    r"\bpsyop\b",
    r"\brevolution\b",
    r"\bscared\b",
    r"\bfear\b",
    r"\blie[sd]?\b",
    r"\bagi is here\b",
)

_STAKE = _compile(
    r"\bmy (?:free )?(?:guide|course|book|program|product|newsletter)\b",
    r"\bwe sell\b",
    r"\bi sell\b",
    r"\bsponsors?\b",
    r"\bsponsored\b",
    r"\baffiliate\b",
    r"\bconsulting\b",
    r"\bbenefits?\b",
    r"\bwho benefits\b",
    r"\binvestors?\b",
    r"\bfunded by\b",
    r"\bfunding\b",
    r"\bsign up\b",
    r"\bbusiness\b",
    r"\bempire\b",
    r"\bcustomers?\b",
)


# --------------------------------------------------------------------------- #
# data model
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class HypeCheck:
    """Result of one check.

    Attributes:
        name: Stable identifier, e.g. ``"benchmark_caveat"``.
        label: Human-readable name.
        applicable: Whether the check had anything to examine.
        passed: ``True``/``False`` when applicable, ``None`` otherwise.
        reason: One line explaining the verdict.
        evidence: Matched spans that produced the verdict.
    """

    name: str
    label: str
    applicable: bool
    passed: bool | None
    reason: str
    evidence: tuple[str, ...] = ()

    @property
    def failed(self) -> bool:
        """Whether this check counts against the record."""
        return self.applicable and self.passed is False

    def as_dict(self) -> dict:
        """JSON-safe representation."""
        return {
            "name": self.name,
            "label": self.label,
            "applicable": self.applicable,
            "passed": self.passed,
            "failed": self.failed,
            "reason": self.reason,
            "evidence": list(self.evidence),
        }


@dataclass(frozen=True)
class HypeVerdict:
    """Aggregate result for one media record.

    Attributes:
        checks: All five check results, in fixed order.
        source: URL or local path of the audited record.
        title: Record title, when known.
        kind: Source kind (video, podcast, ted, ...).
    """

    checks: tuple[HypeCheck, ...] = ()
    source: str = ""
    title: str = ""
    kind: str = "video"

    @property
    def failures(self) -> int:
        """Number of applicable checks that failed."""
        return sum(1 for check in self.checks if check.failed)

    @property
    def applicable(self) -> int:
        """Number of checks that had evidence to examine."""
        return sum(1 for check in self.checks if check.applicable)

    @property
    def is_hype(self) -> bool:
        """``True`` when two or more applicable checks failed."""
        return self.failures >= HYPE_THRESHOLD

    @property
    def tag(self) -> str:
        """``HYPE`` or ``OK``."""
        return HYPE_TAG if self.is_hype else PASS_TAG

    @property
    def failed_names(self) -> tuple[str, ...]:
        """Names of the failed checks."""
        return tuple(check.name for check in self.checks if check.failed)

    @property
    def refinement_blocked(self) -> bool:
        """HYPE records must never refine a capability."""
        return self.is_hype

    def get(self, name: str) -> HypeCheck | None:
        """Look up one check by name."""
        for check in self.checks:
            if check.name == name:
                return check
        return None

    def summary(self) -> str:
        """One-line human summary."""
        failed = ", ".join(self.failed_names) or "none"
        return (
            f"{self.tag}: {self.failures}/{self.applicable} applicable checks failed "
            f"(failed: {failed})"
        )

    def to_dict(self) -> dict:
        """JSON-safe representation, suitable for ingestion logs."""
        return {
            "tag": self.tag,
            "is_hype": self.is_hype,
            "failures": self.failures,
            "applicable": self.applicable,
            "threshold": HYPE_THRESHOLD,
            "failed_checks": list(self.failed_names),
            "source": self.source,
            "title": self.title,
            "kind": self.kind,
            "refinement_blocked": self.refinement_blocked,
            "checks": [check.as_dict() for check in self.checks],
        }


def _na(name: str, label: str, reason: str) -> HypeCheck:
    return HypeCheck(
        name=name, label=label, applicable=False, passed=None, reason=reason, evidence=()
    )


def _result(
    name: str,
    label: str,
    passed: bool,
    reason: str,
    evidence: Sequence[str] = (),
) -> HypeCheck:
    return HypeCheck(
        name=name,
        label=label,
        applicable=True,
        passed=passed,
        reason=reason,
        evidence=tuple(evidence),
    )


# --------------------------------------------------------------------------- #
# the five checks
# --------------------------------------------------------------------------- #


def check_benchmark_caveat(text: str) -> HypeCheck:
    """Check 1: is the benchmark's own limitation left intact?

    A caveat that is quoted and then overridden by an absolute conclusion counts
    as a failure: the speaker used the caveat as decoration, not as a limit.
    """
    norm = _norm(text)
    claims = _find(_SCORE_CLAIM, norm)
    overclaims = _find(_OVERCLAIM, norm)
    caveats = _find(_CAVEAT, norm)
    label = "benchmark caveat"
    if not claims and not overclaims:
        return _na("benchmark_caveat", label, "no benchmark claim to audit")
    if overclaims and caveats:
        return _result(
            "benchmark_caveat",
            label,
            False,
            "absolute claim overrides the benchmark's own caveat",
            overclaims + caveats,
        )
    if overclaims:
        return _result(
            "benchmark_caveat",
            label,
            False,
            "absolute claim with no benchmark caveat",
            overclaims,
        )
    if caveats:
        return _result(
            "benchmark_caveat", label, True, "benchmark limitation acknowledged", caveats
        )
    return _result(
        "benchmark_caveat",
        label,
        False,
        "scores quoted without any stated limitation",
        claims,
    )


def check_harness_disclosure(text: str) -> HypeCheck:
    """Check 2: are scores attributed to a named harness or evaluation setup?"""
    norm = _norm(text)
    scores = _find(_SCORE_CLAIM, norm)
    label = "harness disclosure"
    if not scores:
        return _na("harness_disclosure", label, "no score or benchmark quoted")
    harness = _find(_HARNESS, norm)
    if harness:
        return _result(
            "harness_disclosure",
            label,
            True,
            "evaluation setup named",
            harness,
        )
    return _result(
        "harness_disclosure",
        label,
        False,
        "score quoted without naming the harness or setup",
        scores,
    )


def check_cost_and_budget(text: str) -> HypeCheck:
    """Check 3: is cost, token, latency or compute budget reported?"""
    norm = _norm(text)
    label = "cost and budget"
    claims = _find(_PERF_CLAIM, norm)
    if not claims:
        return _na("cost_and_budget", label, "no performance claim to audit")
    budget = _find(_BUDGET, norm)
    if budget:
        return _result("cost_and_budget", label, True, "cost or budget reported", budget)
    return _result(
        "cost_and_budget",
        label,
        False,
        "accuracy claimed without cost, token or latency budget",
        claims,
    )


def check_funding_vs_intent(text: str) -> HypeCheck:
    """Check 4: is funding stated as fact while intent is asserted as proven?

    Hedged intent ("might be", "allegedly") is not counted; the check targets
    sentences that state motive as established fact.
    """
    norm = _norm(text)
    label = "funding vs intent"
    funding = _find(_FUNDING, norm)
    if not funding:
        return _na("funding_vs_intent", label, "no funding claim to audit")

    asserted: list[str] = []
    hedged: list[str] = []
    for match in _INTENT_ASSERT.finditer(norm):
        sentence = _sentence_at(norm, match.start())
        span = " ".join(match.group(0).split())
        if _HEDGE.search(sentence):
            hedged.append(span)
        else:
            asserted.append(span)

    if asserted:
        return _result(
            "funding_vs_intent",
            label,
            False,
            "motive asserted as fact from funding evidence",
            asserted + funding,
        )
    if hedged:
        return _result(
            "funding_vs_intent",
            label,
            True,
            "funding separated from an explicitly hedged motive",
            hedged + funding,
        )
    return _result(
        "funding_vs_intent",
        label,
        True,
        "funding stated as a fact with no motive inferred",
        funding,
    )


def check_beneficiary(text: str) -> HypeCheck:
    """Check 5: does emotional framing name who benefits from it?"""
    norm = _norm(text)
    label = "beneficiary"
    emotion = _find(_EMOTION, norm)
    if not emotion:
        return _na("beneficiary", label, "no emotional framing detected")
    stake = _find(_STAKE, norm)
    if stake:
        return _result("beneficiary", label, True, "stake or beneficiary named", stake)
    return _result(
        "beneficiary",
        label,
        False,
        "emotional framing with no beneficiary or stake named",
        emotion,
    )


CHECKS = (
    check_benchmark_caveat,
    check_harness_disclosure,
    check_cost_and_budget,
    check_funding_vs_intent,
    check_beneficiary,
)


# --------------------------------------------------------------------------- #
# entry points
# --------------------------------------------------------------------------- #


def is_media_kind(kind: str) -> bool:
    """Whether a source kind must pass the hype filter before ingestion."""
    return (kind or "").strip().lower() in MEDIA_KINDS


def run_hype_filter(
    text: str,
    *,
    title: str = "",
    source: str = "",
    kind: str = "video",
) -> HypeVerdict:
    """Run all five checks over a media transcript.

    Args:
        text: Transcript or article text.
        title: Record title; audited together with the body because the title
            carries the framing.
        source: URL or path recorded in the verdict.
        kind: Source kind.

    Returns:
        A :class:`HypeVerdict`. Two or more failed checks set ``tag == "HYPE"``.

    Raises:
        ValueError: If ``kind`` is a media kind and the text is blank.
    """
    body = (text or "").strip()
    if not body and is_media_kind(kind):
        raise ValueError("cannot audit an empty transcript")
    audited = f"{title}. {body}" if title else body
    checks = tuple(check(audited) for check in CHECKS)
    return HypeVerdict(checks=checks, source=source, title=title, kind=kind)


def enforce_gate(
    *,
    kind: str,
    text: str,
    title: str = "",
    source: str = "",
) -> HypeVerdict | None:
    """Mandatory gate for ingestion.

    Returns ``None`` for non-media sources, otherwise the verdict. Callers must
    treat ``verdict.refinement_blocked`` as a hard stop for capability refinement.
    """
    if not is_media_kind(kind):
        return None
    return run_hype_filter(text, title=title, source=source, kind=kind)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI: ``python -m barrot_agent.hype_filter --file transcript.txt``."""
    parser = argparse.ArgumentParser(description="Audit a media transcript for hype.")
    parser.add_argument("--file", required=True, help="transcript or article file")
    parser.add_argument("--title", default="", help="record title")
    parser.add_argument("--source", default="", help="URL or path")
    parser.add_argument("--kind", default="video", help="video | podcast | ted | audiobook")
    parser.add_argument("--json", action="store_true", help="print the full verdict as JSON")
    args = parser.parse_args(argv)

    text = Path(args.file).read_text(encoding="utf-8", errors="ignore")
    verdict = run_hype_filter(text, title=args.title, source=args.source, kind=args.kind)
    if args.json:
        print(json.dumps(verdict.to_dict(), indent=2))
    else:
        print(verdict.summary())
        for check in verdict.checks:
            state = "skip" if not check.applicable else ("ok" if check.passed else "FAIL")
            print(f"  [{state:4}] {check.name}: {check.reason}")
            if check.evidence:
                print(f"         evidence: {', '.join(check.evidence)}")
    return 1 if verdict.is_hype else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
