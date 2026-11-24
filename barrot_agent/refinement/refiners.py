"""Deterministic offline refiner adapters for derived-data refinement.

Canonical evidence is immutable. This module performs local deterministic
normalization only; it has no external-provider or network-dispatch path.
"""
from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from . import scoring

REFINE_SYSTEM = (
    "You are a data-refinement worker in a ping-pong refinement loop. "
    "Improve the GIVEN DATA: fix inconsistencies, remove redundancy, fill "
    "gaps with explicit values, drop unsupported claims, keep structure. "
    "Technique over style. Never invent facts. Reply with STRICT JSON only: "
    '{"data": <refined data>, "verdict": "REFINED"|"CONVERGED", "notes": "<=200 chars"} '
    'Use verdict CONVERGED only when no further meaningful refinement is possible.'
)

CRITIQUE_SYSTEM = (
    "You are the critique side of a ping-pong refinement loop. Examine the "
    "GIVEN DATA and the previous refinement. State what is still wrong, "
    "missing, unsupported, or redundant. Reply with STRICT JSON only: "
    '{"critique": "<=400 chars", "verdict": "REFINE"|"CONVERGED"} '
    'Use verdict CONVERGED only if nothing meaningful remains to fix.'
)


@dataclass
class RefinementOutput:
    actor: str
    role: str                 # "refine" | "critique"
    verdict: str              # "REFINED" | "CONVERGED" | "FAILED"
    data: Any = None          # refined data (refine role)
    critique: str = ""        # critique text (critique role)
    notes: str = ""
    meta: dict = field(default_factory=dict)


class Refiner(ABC):
    name: str = "refiner"

    @abstractmethod
    def refine(self, data: Any, critique: str | None) -> RefinementOutput:
        """One refinement pass over data, optionally guided by the other
        side's critique."""

    @abstractmethod
    def critique(self, data: Any) -> RefinementOutput:
        """One critique pass over data (no rewrite)."""


# -------------------------------------------------------------- deterministic
class HeuristicRefiner(Refiner):
    """Deterministic offline refiner. Improves what can be improved
    mechanically and reports CONVERGED exactly when nothing changed —
    a true fixed point, no randomness, no network."""

    def __init__(self, name: str = "heuristic"):
        self.name = name

    @staticmethod
    def _clean_str(s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    def _refine_node(self, node: Any) -> tuple[Any, bool]:
        changed = False
        if isinstance(node, dict):
            out = {}
            for k, v in node.items():
                nv, c = self._refine_node(v)
                out[k] = nv
                changed |= c
            return out, changed
        if isinstance(node, list):
            out = []
            seen = set()
            for item in node:
                ni, c = self._refine_node(item)
                changed |= c
                if isinstance(ni, str) and not ni.strip():
                    changed = True      # drop empty-string items
                    continue
                key = json.dumps(ni, sort_keys=True, ensure_ascii=False) \
                    if isinstance(ni, (dict, list)) else repr(ni)
                if key in seen:
                    changed = True      # dropped duplicate
                    continue
                seen.add(key)
                out.append(ni)
            return out, changed
        if isinstance(node, str):
            cleaned = self._clean_str(node)
            if cleaned != node:
                return cleaned, True
            return node, False
        return node, False

    def refine(self, data: Any, critique: str | None) -> RefinementOutput:
        refined, changed = self._refine_node(data)
        if not changed and scoring.score(refined) >= scoring.score(data) - 1e-9:
            return RefinementOutput(self.name, "refine", "CONVERGED",
                                    data=data, notes="no mechanical improvement left")
        return RefinementOutput(self.name, "refine", "REFINED",
                                data=refined, notes="dedupe/normalize pass")

    def critique(self, data: Any) -> RefinementOutput:
        _, changed = self._refine_node(data)
        issues = []
        bd = scoring.breakdown(data)
        if bd["completeness"] < 1.0:
            issues.append(f"{1.0 - bd['completeness']:.0%} empty leaves")
        if bd["redundancy"] < 1.0:
            issues.append("duplicate list items")
        if bd["consistency"] < 1.0:
            issues.append("conflicting duplicate keys")
        text = "; ".join(issues) or "no mechanical defects detected"
        # CONVERGED == no further MECHANICAL refinement possible. Residual
        # semantic gaps (empty leaves needing facts) are noted for the live
        # models but cannot be fixed deterministically, so they don't block
        # this refiner's fixed point.
        return RefinementOutput(self.name, "critique",
                                "REFINE" if changed else "CONVERGED",
                                critique=text)


def make_model_refiners(*args: Any, **kwargs: Any) -> list[Refiner]:
    """Compatibility shim: external model-provider pools are decommissioned."""
    return []
