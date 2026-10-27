#!/usr/bin/env python3
"""Epigenetic reprogramming optimization engine."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Iterable, List, Sequence


@dataclass(frozen=True)
class YamanakaFactorModel:
    """Represents behavior and safety profile of a Yamanaka factor."""

    name: str
    efficacy: float
    risk: float


@dataclass
class ReprogrammingProtocol:
    """Defines a protocol with on/off timing and factors."""

    factors: List[str]
    on_days: int
    off_days: int
    cycles: int
    target_cell_type: str


class FactorInteractionMatrix:
    """Models synergy between reprogramming factors."""

    def __init__(self, pairwise_scores: Dict[str, float] | None = None) -> None:
        if pairwise_scores is None:
            pairwise_scores = {
                "Oct4|Sox2": 0.35,
                "Oct4|Klf4": 0.22,
                "Sox2|Klf4": 0.25,
                "Klf4|c-Myc": 0.18,
                "Oct4|c-Myc": 0.12,
                "Sox2|c-Myc": 0.14,
            }
        self.pairwise_scores = pairwise_scores

    def synergy(self, factors: Sequence[str]) -> float:
        total = 0.0
        for left, right in combinations(sorted(factors), 2):
            total += self.pairwise_scores.get(f"{left}|{right}", 0.0)
        return round(total, 3)


class SafetyAnalyzer:
    """Predicts protocol risk and identifies mitigation suggestions."""

    def assess(
        self, protocol: ReprogrammingProtocol, factors: Dict[str, YamanakaFactorModel]
    ) -> Dict[str, float | str | bool]:
        risk = sum(factors[name].risk for name in protocol.factors if name in factors)
        exposure = protocol.on_days * protocol.cycles
        composite = risk * (1 + exposure / 100.0)
        return {
            "risk_score": round(composite, 3),
            "safe": composite < 5.0,
            "recommendation": "transient_expression" if composite >= 5.0 else "current_schedule_ok",
        }


class CellTypeOptimizer:
    """Optimizes factors and timing for specific cell types."""

    _CELL_TYPE_PRIORS: Dict[str, Dict[str, float]] = {
        "brain": {"Oct4": 1.1, "Sox2": 1.25, "Klf4": 0.95, "c-Myc": 0.75},
        "muscle": {"Oct4": 1.0, "Sox2": 0.9, "Klf4": 1.1, "c-Myc": 0.8},
        "eye": {"Oct4": 1.2, "Sox2": 1.2, "Klf4": 0.85, "c-Myc": 0.7},
        "skin": {"Oct4": 0.95, "Sox2": 0.9, "Klf4": 1.2, "c-Myc": 0.7},
    }

    def score_factor_set(self, cell_type: str, factors: Iterable[str]) -> float:
        priors = self._CELL_TYPE_PRIORS.get(cell_type, self._CELL_TYPE_PRIORS["skin"])
        return round(sum(priors.get(factor, 0.8) for factor in factors), 3)


class EpigeneticReprogrammingEngine:
    """Multi-objective optimization balancing efficacy and safety."""

    def __init__(self) -> None:
        self.factors: Dict[str, YamanakaFactorModel] = {
            "Oct4": YamanakaFactorModel("Oct4", efficacy=1.3, risk=1.0),
            "Sox2": YamanakaFactorModel("Sox2", efficacy=1.25, risk=0.9),
            "Klf4": YamanakaFactorModel("Klf4", efficacy=1.05, risk=0.8),
            "c-Myc": YamanakaFactorModel("c-Myc", efficacy=1.4, risk=1.9),
        }
        self.interactions = FactorInteractionMatrix()
        self.safety = SafetyAnalyzer()
        self.cell_optimizer = CellTypeOptimizer()

    def optimize_protocol(self, target_cell_type: str, max_risk: float = 5.0) -> Dict[str, object]:
        candidates: List[Dict[str, object]] = []
        factor_names = list(self.factors.keys())

        for count in range(2, len(factor_names) + 1):
            for factor_set in combinations(factor_names, count):
                protocol = ReprogrammingProtocol(
                    factors=list(factor_set),
                    on_days=4,
                    off_days=10,
                    cycles=6,
                    target_cell_type=target_cell_type,
                )
                safety_result = self.safety.assess(protocol, self.factors)
                if float(safety_result["risk_score"]) > max_risk:
                    continue

                efficacy = (
                    sum(self.factors[name].efficacy for name in factor_set)
                    + self.interactions.synergy(factor_set)
                    + self.cell_optimizer.score_factor_set(target_cell_type, factor_set)
                )
                objective = efficacy / max(float(safety_result["risk_score"]), 0.1)
                candidates.append(
                    {
                        "protocol": protocol,
                        "efficacy_score": round(efficacy, 3),
                        "objective_score": round(objective, 3),
                        "safety": safety_result,
                    }
                )

        if not candidates:
            raise ValueError("No protocol candidates satisfied the safety threshold")

        best = sorted(candidates, key=lambda item: item["objective_score"], reverse=True)[0]
        return {
            "target_cell_type": target_cell_type,
            "best_protocol": best["protocol"],
            "objective_score": best["objective_score"],
            "safety": best["safety"],
            "candidate_count": len(candidates),
        }
