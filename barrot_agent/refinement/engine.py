"""Optional ping-pong refinement for explicitly classified derived data.

Refinement is deterministic and offline. Canonical evidence is immutable;
external-provider dispatch has been removed.

Semantics (Barrot standing orders): refinement efforts ping-pong dynamically
between models until the data can be refined NO FURTHER — a measured fixed
point, not a feeling:

  round i:   actor[i % n]   REFINES data   (guided by the other side's critique)
  round i:   actor[(i+1)%n] CRITIQUES      (verdict REFINE or CONVERGED)
  round i+1: roles swap — the critic now refines, the refiner now critiques.

"Cannot be refined further" is declared by two independent signals:
  - model_consensus: the refiner returned CONVERGED and the critic returned
    CONVERGED, with no accepted data change for `patience` half-rounds;
  - score_plateau (objective backstop): the deterministic quality score
    (scoring.py) has not moved for `patience` consecutive ping halves —
    when the measurement says nothing improves anymore, byte-churn is not
    refinement, and the loop stops no matter how eager the models are.

Rewrite acceptance: a ping's output replaces the data only when the score
does not regress. Non-improving-but-different outputs count as unstable and
feed the plateau counter, they are not silent data loss.

Safety: hard max_rounds cap; a FAILED model pass doesn't advance the data —
the paddle rotates to the next model in the pool within the same pass, and
refiners retry transient API errors with backoff; only an exhausted pool
stops the run (stop_reason=pool_exhausted).

Every round is appended to a JSONL ledger (provenance, repo convention).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from . import scoring
from .refiners import HeuristicRefiner, Refiner

DEFAULT_EPSILON = 1e-4       # score is rounded to 6dp; below this = no change
DEFAULT_PATIENCE = 2         # stable half-rounds required before plateau/consensus
DEFAULT_MAX_ROUNDS = 12
DEFAULT_LEDGER = Path("ping-pongings/knowledge-base/refinement_log.jsonl")
REFINABLE_DATA_CLASSES = frozenset({
    "derived_summary", "public_derived_summary", "public_documentation", "public_research_note",
})
IMMUTABLE_DATA_CLASSES = frozenset({
    "raw_source", "source_receipt", "feature_snapshot", "feature_store",
    "event_timeline", "forecast_ledger", "market_data", "credentials",
    "secrets", "user_private",
})


@dataclass
class RoundRecord:
    round: int
    actor: str
    role: str
    score_before: float
    score_after: float
    delta: float
    verdict: str
    notes: str = ""

    def to_dict(self) -> dict:
        return {**self.__dict__}


@dataclass
class RefinementReport:
    converged: bool
    stop_reason: str            # model_consensus | score_plateau | max_rounds | pool_exhausted
    rounds: int
    score_start: float
    score_end: float
    data: Any
    history: list[RoundRecord] = field(default_factory=list)
    models_used: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "converged": self.converged,
            "stop_reason": self.stop_reason,
            "rounds": self.rounds,
            "score_start": self.score_start,
            "score_end": self.score_end,
            "score_gain": round(self.score_end - self.score_start, 6),
            "models_used": self.models_used,
            "history": [r.to_dict() for r in self.history],
        }


class PingPongRefiner:
    """Alternating-model refinement until measured fixed point."""

    def __init__(self, refiners: Iterable[Refiner],
                 epsilon: float = DEFAULT_EPSILON,
                 max_rounds: int = DEFAULT_MAX_ROUNDS,
                 patience: int = DEFAULT_PATIENCE,
                 ledger: Path | str | None = DEFAULT_LEDGER,
                 data_classification: str = "unknown"):
        self.refiners: list[Refiner] = list(refiners)
        if not self.refiners:
            raise ValueError("PingPongRefiner needs at least one refiner")
        if data_classification not in REFINABLE_DATA_CLASSES:
            raise ValueError("unknown or immutable data classification cannot be refined")
        self.data_classification = data_classification
        self.epsilon = epsilon
        self.max_rounds = max_rounds
        self.patience = patience
        self.ledger = Path(ledger) if ledger else None

    # ------------------------------------------------------------------ ledger
    def _log(self, record: dict) -> None:
        if self.ledger is None:
            return
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    # ------------------------------------------------------------------- loop
    def run(self, data: Any, context: str = "") -> RefinementReport:
        n = len(self.refiners)
        score_start = scoring.score(data)
        history: list[RoundRecord] = []
        models_used: list[str] = []
        stable_streak = 0       # consecutive halves without an accepted change
        plateau = 0             # consecutive ping halves with a flat measured score
        stop_reason = "max_rounds"
        converged = False
        round_no = 0

        while round_no < self.max_rounds:
            # ping-pong pairing: round r starts at refiner[r % n]; if that
            # actor fails, the paddle rotates to the next model in the pool.
            # The critic is the next model after the successful actor, so
            # roles keep swapping every round.
            prev_critic_verdict = next(
                (h.verdict for h in reversed(history) if h.role == "critique"), None)

            # ---- ping: refine (dynamic: rotate through the pool on failure) ----
            s_before = scoring.score(data)
            critique_in = (history[-1].notes or None) \
                if history and history[-1].role == "critique" else None
            out = None
            actor_idx = round_no % n
            for pool_try in range(n):
                actor_idx = (round_no + pool_try) % n
                actor = self.refiners[actor_idx]
                if actor.name not in models_used:
                    models_used.append(actor.name)
                out = actor.refine(data, critique_in)
                if out.verdict != "FAILED" and out.data is not None:
                    break
                # this actor is down; log it, hand the paddle to the next model
                history.append(RoundRecord(round_no, actor.name, "refine",
                                           s_before, s_before, 0.0, "FAILED",
                                           out.notes))
                self._log(self._ledger_row(round_no, actor, "refine",
                                           s_before, s_before, "FAILED", out.notes))
            if out is None or out.verdict == "FAILED" or out.data is None:
                # every model in the pool failed this ping — circuit breaker
                stop_reason = "pool_exhausted"
                break
            critic = self.refiners[(actor_idx + 1) % n]
            if critic.name not in models_used:
                models_used.append(critic.name)
            s_after = scoring.score(out.data)
            accepted = (out.data != data) and s_after >= s_before
            if accepted:
                data = out.data
                stable_streak = 0
            else:
                stable_streak += 1
            history.append(RoundRecord(round_no, actor.name, "refine",
                                       s_before, scoring.score(data),
                                       round(s_after - s_before, 6),
                                       out.verdict, out.notes))
            self._log(self._ledger_row(round_no, actor, "refine",
                                       s_before, s_after, out.verdict, out.notes))
            if (out.verdict == "CONVERGED"
                    and stable_streak >= self.patience
                    and prev_critic_verdict == "CONVERGED"):
                # signal 1 — model_consensus: both sides declare done and the
                # data has stopped changing
                stop_reason = "model_consensus"
                converged = True
                break
            if s_after - s_before > self.epsilon:
                plateau = 0             # real, measurable improvement
            else:
                plateau += 1
                if plateau >= self.patience:
                    # signal 2 — score_plateau: the objective backstop. The
                    # deterministic score is flat, so cosmetic byte-churn is
                    # not refinement; stop regardless of model enthusiasm.
                    stop_reason = "score_plateau"
                    converged = True
                    break

            # ---- pong: critique ----
            s_mid = scoring.score(data)
            cout = critic.critique(data)
            cverdict = cout.verdict if cout.verdict != "FAILED" else "FAILED"
            history.append(RoundRecord(round_no, critic.name, "critique",
                                       s_mid, scoring.score(data), 0.0,
                                       cverdict, cout.critique))
            self._log(self._ledger_row(round_no, critic, "critique",
                                       s_mid, scoring.score(data), cverdict,
                                       cout.critique))
            if cverdict == "CONVERGED" and stable_streak >= self.patience \
                    and out.verdict == "CONVERGED":
                # signal 1 — model_consensus, detected on the pong side
                stop_reason = "model_consensus"
                converged = True
                break
            round_no += 1

        if not converged and round_no >= self.max_rounds:
            stop_reason = "max_rounds"

        score_end = scoring.score(data)
        return RefinementReport(
            converged=converged,
            stop_reason=stop_reason,
            rounds=len({h.round for h in history}),
            score_start=score_start,
            score_end=score_end,
            data=data,
            history=history,
            models_used=models_used,
        )

    @staticmethod
    def _ledger_row(round_no: int, refiner: Refiner, role: str,
                    s_before: float, s_after: float, verdict: str,
                    notes: str) -> dict:
        return {
            "ts": datetime.now(timezone.utc).isoformat(),
            "round": round_no,
            "actor": refiner.name,
            "role": role,
            "score_before": s_before,
            "score_after": s_after,
            "delta": round(s_after - s_before, 6),
            "verdict": verdict,
            "notes": (notes or "")[:200],
        }


# ------------------------------------------------------- derived-data helper
def refine_data(
    data: Any, refiners: Iterable[Refiner] | None = None, context: str = "",
    ledger: Path | str | None = DEFAULT_LEDGER, *,
    data_classification: str = "unknown", allow_external: bool = False, **kwargs,
) -> RefinementReport:
    """Refine explicitly classified derived data; never raw evidence."""
    if data_classification not in REFINABLE_DATA_CLASSES:
        raise ValueError("unknown or immutable data classification cannot be refined")
    if refiners is None:
        refiners = [HeuristicRefiner(), HeuristicRefiner("heuristic-2")]
    refiners = list(refiners)
    if not refiners or not all(isinstance(r, Refiner) for r in refiners):
        raise TypeError("refiners must be a non-empty iterable of Refiner instances")
    if allow_external:
        raise PermissionError("external refinement providers are decommissioned")
    return PingPongRefiner(
        refiners, ledger=ledger, data_classification=data_classification, **kwargs
    ).run(data, context=context)


def refine_json_file(
    path: Path | str, out_path: Path | str | None = None,
    refiners: Iterable[Refiner] | None = None,
    ledger: Path | str | None = DEFAULT_LEDGER, *,
    data_classification: str = "unknown", allow_external: bool = False,
) -> RefinementReport:
    """Refine a classified derived-data JSON document, never canonical evidence."""
    if allow_external:
        raise PermissionError("external refinement providers are decommissioned")
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    report = refine_data(data, refiners=refiners, context=f"file:{path}", ledger=ledger,
                         data_classification=data_classification)
    dest = Path(out_path) if out_path else path
    dest.write_text(json.dumps(report.data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report
