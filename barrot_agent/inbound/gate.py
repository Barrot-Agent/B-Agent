"""Authority gate for commands arriving from outside the operator.

Sean runs several frontier models alongside this agent. Any of them can produce
text that looks like an instruction. This module is the boundary: text from a
model is *data that proposes work*, never authority that grants it.

What it does, in order:

    classify    who sent it. Only OPERATOR can approve an exception.
    policy      scan for actions that are denied outright, or need approval.
    transmute   restate the command as requirement + gaps + conflicts.
    refine      re-run transmutation on its own output, bounded, until the
                requirement set stops changing.
    sandbox     produce a plan. It never executes anything.

Three properties are deliberate and tested:

    refinement cannot launder permission
        policy runs on every pass, and the verdict is the intersection. A
        command that was denied on pass 1 stays denied on pass 3, even if the
        refined text no longer contains the offending phrase.

    recursion is bounded
        "refine indefinitely" is refused. A refinement loop with no fixed point
        either never executes or diverges, and a model re-reading its own input
        can amplify an injected instruction. The cap is 3 passes.

    nothing here executes
        the sandbox returns a plan and a verdict. Execution stays with the
        normal tools, under the normal rules.

No network imports. No subprocess. No file writes.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum

MAX_PASSES = 3
DEFAULT_PASSES = 2

# A refinement pass that changes fewer requirements than this is treated as
# converged. It is a count, not a distance: the loop is deterministic, so the
# requirement set either changes or it does not.
CONVERGENCE_DELTA = 0


class Source(str, Enum):
    OPERATOR = "OPERATOR"
    FRONTIER_MODEL = "FRONTIER_MODEL"
    RETRIEVED_TEXT = "RETRIEVED_TEXT"
    UNKNOWN = "UNKNOWN"


class Severity(str, Enum):
    ALLOW = "ALLOW"
    APPROVE = "APPROVE"
    DENY = "DENY"


@dataclass(frozen=True)
class Rule:
    code: str
    severity: Severity
    pattern: re.Pattern[str]
    why: str


def _r(code: str, severity: Severity, pattern: str, why: str) -> Rule:
    return Rule(code, severity, re.compile(pattern, re.IGNORECASE), why)


# Fail-closed by design. A prohibition such as "never push to main" will also
# match: inbound commands are imperatives, so a prohibition arriving as a command
# is already out of place. The cost of a false positive is one clarification; the
# cost of a false negative is a pushed secret.
RULES: tuple[Rule, ...] = (
    _r("SECRET_READ", Severity.DENY,
       r"\b(read|print|cat|echo|show|dump|send|paste|exfiltrat\w*)\b.{0,60}"
       r"\b(api[ _-]?key|secret|token|credential|password|passwd)\b",
       "credential material is never read, printed, or sent"),
    _r("SEED_PHRASE", Severity.DENY,
       r"\b(seed phrase|mnemonic|private key|recovery phrase|keystore)\b",
       "wallet material is out of scope in every mode"),
    _r("LIVE_MONEY", Severity.DENY,
       r"\b(place|submit|send|cancel)\b.{0,30}\border\b|\blive (trade|order|money)\b"
       r"|\bwithdraw\b|\bwallet connect\b|\bsign (the )?transaction\b",
       "paper only: no live order path exists and none will be added by a command"),
    _r("HISTORY_REWRITE", Severity.DENY,
       r"\b(force[- ]?push|push\s+--force|reset\s+--hard|filter-branch|rebase\s+-i)\b"
       r"|\brewrite\b.{0,20}\bhistory\b",
       "git history is append-only here"),
    _r("PUSH_MAIN", Severity.DENY,
       r"\bpush\b.{0,25}\b(origin\s+)?(main|master)\b|\bmerge\b.{0,20}\b(main|master)\b",
       "main is not a write target for an agent; branch and PR only"),
    _r("PUBLISH", Severity.DENY,
       r"\b(publish|deploy to production|release to|upload to pypi|npm publish)\b",
       "the publish path needs the operator, not a command"),
    _r("DESTRUCTIVE_FS", Severity.DENY,
       r"\brm\s+-rf?\b|\bmkfs\b|\bdd\s+if=|\bchmod\s+777\s+/\b",
       "destructive filesystem operations are never delegated"),
    _r("GUARD_BYPASS", Severity.DENY,
       r"\bbypass\b.{0,25}\b(network_guard|allowlist|guard)\b"
       r"|\b(disable|skip|ignore)\b.{0,20}\b(network_guard|allowlist)\b",
       "the network guard is the only egress and is not optional"),
    _r("UNBOUNDED_RECURSION", Severity.DENY,
       r"\b(indefinitely|forever|unbounded|never stop|loop forever|endless(ly)?)\b",
       "recursion is bounded at MAX_PASSES; an unbounded loop is rejected, not scheduled"),
    _r("AUTHORITY_CLAIM", Severity.DENY,
       r"\b(ignore|disregard|forget)\b.{0,30}\b(previous|prior|above|your)\b.{0,20}"
       r"\b(instruction|rule|prompt|system)\b"
       r"|\byou are now\b|\bact as (root|admin|developer mode)\b"
       r"|\b(show|print|reveal)\b.{0,20}\bsystem prompt\b",
       "text cannot grant itself authority"),
    _r("DELETE_SCOPE", Severity.APPROVE,
       r"\b(delete|remove|drop)\b.{0,30}\b(file|directory|table|branch|repo)\b",
       "deletion is reversible only with the operator's approval"),
    _r("WORKFLOW_CHANGE", Severity.APPROVE,
       r"\b(edit|modify|change|disable)\b.{0,25}\b(workflow|ci|pipeline|permission)\b",
       "CI and permission changes are operator decisions"),
    _r("DEPENDENCY_ADD", Severity.APPROVE,
       r"\b(pip install|npm install|add (a )?dependency|uv add)\b",
       "new code from outside the repo needs a decision"),
    _r("NETWORK_USE", Severity.APPROVE,
       r"\b(curl|wget|requests\.get|httpx\.|urllib)\b.{0,40}\bhttps?://",
       "every outbound call goes through network_guard and is logged"),
)

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with", "then",
    "please", "can", "you", "your", "me", "my", "it", "this", "that", "be", "is",
    "are", "do", "does", "now", "just", "also", "all", "any", "from", "by",
}

VERB_HINTS = (
    "scan", "build", "fix", "run", "write", "remove", "add", "refactor", "test",
    "commit", "push", "pull", "fetch", "deploy", "publish", "delete", "merge",
    "transmute", "reverse", "analyze", "analyse", "measure", "verify", "update",
)

GAP_CATEGORIES = (
    "input_data",
    "proof_or_test",
    "failure_path",
    "cost_or_risk",
    "rollback",
    "verification",
)


@dataclass(frozen=True)
class Command:
    text: str
    source: Source
    received_from: str = ""
    correlation_id: str = ""

    def digest(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()[:16]


@dataclass
class PolicyHit:
    code: str
    severity: Severity
    why: str
    match: str


@dataclass
class Transmutation:
    pass_number: int
    original: str
    requirement: str
    gaps: tuple[str, ...]
    conflicts: tuple[str, ...]
    normalised: str
    digest: str


@dataclass
class Refinement:
    """The result of a bounded refinement run.

    `capped` and `clamped` are different facts and conflating them was a bug the
    tests caught: `capped` means the loop hit its limit without a fixed point,
    `clamped` means the caller asked for more passes than the hard maximum and
    was silently given fewer. The second one must be visible.
    """

    passes: list[Transmutation]
    converged: bool
    capped: bool
    clamped: bool
    requested: int
    limit: int


@dataclass
class Verdict:
    allowed: bool
    executed: bool
    severity: Severity
    hits: list[PolicyHit] = field(default_factory=list)
    approval_needed: list[str] = field(default_factory=list)
    passes: list[Transmutation] = field(default_factory=list)
    converged: bool = False
    capped: bool = False
    clamped: bool = False
    source: Source = Source.UNKNOWN
    plan: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    def summary(self) -> str:
        head = self.severity.value
        if self.executed:
            return head  # cannot happen; kept so the invariant is visible
        return f"{head} (not executed)"


# --- policy -------------------------------------------------------------------


def scan(text: str) -> list[PolicyHit]:
    hits: list[PolicyHit] = []
    for rule in RULES:
        match = rule.pattern.search(text)
        if match:
            hits.append(PolicyHit(rule.code, rule.severity, rule.why, match.group(0)[:80]))
    return hits


def worst(hits: list[PolicyHit]) -> Severity:
    if any(h.severity is Severity.DENY for h in hits):
        return Severity.DENY
    if any(h.severity is Severity.APPROVE for h in hits):
        return Severity.APPROVE
    return Severity.ALLOW


# --- transmutation ------------------------------------------------------------


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9_]+", text.lower()) if t not in STOPWORDS]


def _requirement(text: str) -> str:
    """Restate as an imperative requirement, deterministically.

    This is not a language model rewrite. It extracts the verb and the object and
    drops courtesy filler, so the same input always produces the same output.
    """
    tokens = _tokens(text)
    if not tokens:
        return "nothing to do: the command contains no actionable token"
    verb = next((t for t in tokens if t in VERB_HINTS), tokens[0])
    rest = [t for t in tokens if t != verb]
    obj = " ".join(rest[:8]) if rest else "the repository"
    return f"{verb} {obj}"


def _gaps(text: str, tokens: list[str]) -> tuple[str, ...]:
    """Which of the six gap categories the command leaves unanswered."""
    lowered = text.lower()
    gaps: list[str] = []
    if not re.search(
        r"\.(csv|json|jsonl|md|py|yaml|yml|txt|log)\b|https?://|\bsnapshot\b", lowered
    ):
        gaps.append("input_data")
    if not re.search(r"\btest|pytest|assert|verify|measur|benchmark\b", lowered):
        gaps.append("proof_or_test")
    if not re.search(r"\bif\b|\bfail|error|fallback|abort|otherwis\b", lowered):
        gaps.append("failure_path")
    if not re.search(r"\bcost|risk|budget|rate|limit\b", lowered):
        gaps.append("cost_or_risk")
    if not re.search(r"\brevert|rollback|git checkout|undo|restore\b", lowered):
        gaps.append("rollback")
    if not re.search(r"\b(check|confirm|verify|assert|prove|reproduc)|pytest\b", lowered):
        gaps.append("verification")
    if not tokens:
        return GAP_CATEGORIES
    return tuple(gaps)


def _conflicts(text: str, hits: list[PolicyHit]) -> tuple[str, ...]:
    out = []
    if any(h.severity is Severity.DENY for h in hits):
        out.append("the command asks for an action the hard policy denies")
    if re.search(r"\b(indefinitely|forever|unbounded|never stop|loop forever)\b", text, re.I):
        out.append("unbounded recursion requested; bounded execution is the only safe reading")
    if re.search(r"\b(ignore|disregard)\b", text, re.I):
        out.append("the command asks to drop standing rules, which no source can authorise")
    return tuple(out)


def transmute(text: str, pass_number: int = 1, base: str | None = None) -> Transmutation:
    """Transmute one pass.

    `base` is the request as received. The requirement and the gap list are
    always measured against it, never against `text` when `text` is an earlier
    pass's own output. This is not a detail: the normalised form names the gaps
    it could not answer, so re-measuring against it counts the word "rollback"
    as evidence that a rollback exists. That would close six gaps with no
    answer behind any of them.
    """
    source = base if base is not None else text
    hits = scan(text)
    tokens = _tokens(source)
    gaps = _gaps(source, tokens)
    requirement = _requirement(source)
    conflicts = _conflicts(text, hits)
    # The normalised form is the requirement plus the gap list, so the next pass
    # sees a complete statement and can converge instead of inventing new work.
    normalised = requirement
    if gaps:
        normalised += ". unresolved: " + ", ".join(gaps)
    return Transmutation(
        pass_number=pass_number,
        original=text,
        requirement=requirement,
        gaps=gaps,
        conflicts=conflicts,
        normalised=normalised,
        digest=hashlib.sha256(normalised.encode("utf-8")).hexdigest()[:16],
    )


def refine(text: str, max_passes: int = DEFAULT_PASSES) -> Refinement:
    """Run the loop to a fixed point, or to the hard maximum, whichever is first.

    Both stop conditions are reported. A caller who asks for 999 passes gets 3
    and is told so (`clamped`), because a silent clamp is how an unbounded
    request looks like it succeeded.

    The fixed point arrives on pass 2 by construction. The gate receives no new
    information between passes, so a loop that keeps changing its own
    requirement is not refining anything - it is inventing work. Pass 2 exists
    to prove pass 1 was stable; if the two signatures ever differ, that is a
    determinism bug and it is reported as non-convergence instead of hidden.
    """
    requested = int(max_passes)
    passes: list[Transmutation] = []
    if requested < 1:
        return Refinement([], False, True, False, requested, 0)
    limit = min(requested, MAX_PASSES)
    clamped = requested > MAX_PASSES
    previous: tuple[str, tuple[str, ...]] | None = None
    for number in range(1, limit + 1):
        result = transmute(text, number, base=text)
        signature = (result.requirement, result.gaps)
        passes.append(result)
        if previous is not None and _delta(previous, signature) <= CONVERGENCE_DELTA:
            return Refinement(passes, True, False, clamped, requested, limit)
        previous = signature
    return Refinement(passes, False, True, clamped, requested, limit)


def _delta(a: tuple[str, tuple[str, ...]], b: tuple[str, tuple[str, ...]]) -> int:
    """Symmetric difference size between two requirement signatures."""
    same_req = 0 if a[0] == b[0] else 1
    same_gaps = len(set(a[1]) ^ set(b[1]))
    return same_req + same_gaps


# --- the gate -----------------------------------------------------------------


def _plan(passes: list[Transmutation]) -> list[str]:
    if not passes:
        return []
    final = passes[-1]
    steps = [f"1. restate as requirement: {final.requirement}"]
    for index, gap in enumerate(final.gaps, start=2):
        steps.append(f"{index}. resolve {gap} before acting")
    steps.append(f"{len(steps) + 1}. produce evidence for every claim, or mark it UNRESOLVED")
    return steps


def gate(command: Command, max_passes: int = DEFAULT_PASSES) -> Verdict:
    """Classify, transmute with bounded refinement, and return a plan.

    Never executes. `allowed` means "the operator may proceed"; `executed` is
    always False, and that is asserted in the tests.
    """
    original_hits = scan(command.text)
    run = refine(command.text, max_passes=max_passes)
    passes = run.passes

    # Policy runs on every pass. The verdict is the union of all passes, so a
    # refinement that removes the phrase cannot remove the finding.
    all_hits: list[PolicyHit] = list(original_hits)
    for p in passes:
        for hit in scan(p.normalised):
            if not any(h.code == hit.code for h in all_hits):
                all_hits.append(hit)

    severity = worst(all_hits)
    reasons: list[str] = []
    if severity is Severity.DENY:
        reasons = [f"{h.code}: {h.why}" for h in all_hits if h.severity is Severity.DENY]
        allowed = False
    elif severity is Severity.APPROVE:
        reasons = [f"{h.code}: {h.why}" for h in all_hits if h.severity is Severity.APPROVE]
        allowed = command.source is Source.OPERATOR
        if not allowed:
            reasons.append(
                f"source {command.source.value} cannot approve: only the operator can"
            )
    else:
        allowed = True

    if run.capped:
        reasons.append("recursion cap reached without convergence; result is a plan, not a loop")
    if run.clamped:
        reasons.append(
            f"requested {run.requested} passes, clamped to the hard maximum of {run.limit}"
        )

    return Verdict(
        allowed=allowed,
        executed=False,
        severity=severity,
        hits=all_hits,
        approval_needed=sorted({h.code for h in all_hits if h.severity is Severity.APPROVE}),
        passes=passes,
        converged=run.converged,
        capped=run.capped,
        clamped=run.clamped,
        source=command.source,
        plan=_plan(passes),
        reasons=reasons,
    )


def render(verdict: Verdict) -> str:
    lines = [
        f"source      {verdict.source.value}",
        f"verdict     {verdict.summary()}",
        f"refinement  {len(verdict.passes)} passes, converged={verdict.converged}, "
        f"capped={verdict.capped}, clamped={verdict.clamped}",
    ]
    for p in verdict.passes:
        lines.append(f"  pass {p.pass_number}: {p.requirement}  gaps={list(p.gaps)}")
    for step in verdict.plan:
        lines.append(f"  plan {step}")
    for reason in verdict.reasons:
        lines.append(f"  reason {reason}")
    return "\n".join(lines)
