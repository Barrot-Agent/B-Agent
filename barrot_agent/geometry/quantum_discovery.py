"""
Barrot V3 — Quantum Structural Discovery Adapter.

Bridges the deterministic QubitState model into the existing
StructuralDiscoveryCore without introducing an LLM dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .quantum import QubitState, QubitStateClass


@dataclass(frozen=True)
class QuantumDiscoveryResult:
    """Stable result exposed to higher-level Barrot reasoning."""

    state: QubitState
    state_class: QubitStateClass
    invariants: dict[str, float | bool | str]
    valid: bool


class QubitStructuralDiscovery:

    def register_with_core(self, core, state, representation_id="qubit_state"):
        """
        Register this deterministic quantum representation with the existing
        StructuralDiscoveryCore.

        The bridge deliberately keeps the quantum-specific calculations in
        this adapter and hands only normalized representation/signature data
        to the generic Geometry core.
        """
        from .structural_discovery import Constraint, FeasibilityState

        result = self.analyze(state)
        payload = self.representation_payload(state)

        # StructuralDiscoveryCore owns Representation construction.
        # The Core generates its own representation identifier.
        representation = core.register_representation(
            payload["domain"],
            payload["kind"],
            payload["data"],
            None,
        )

        # Feed the deterministic quantum invariants into the generic Core.
        # The representation payload contains the Bloch vector, so the
        # constraint is evaluated against that normalized representation.
        invariant_fns = {
            name: (
                lambda rep, name=name: result.invariants[name]
            )
            for name in result.invariants
        }

        def bloch_ball_constraint(rep):
            vector = rep.data["bloch_vector"]
            x, y, z = vector
            return (x * x + y * y + z * z) <= 1.0 + state.tolerance

        constraints = [
            Constraint(
                name="bloch_ball",
                predicate=bloch_ball_constraint,
            )
        ]

        signature = core.compute_signature(
            representation,
            invariant_fns,
            constraints,
        )

        return {
            "representation": representation,
            "signature": signature,
            "analysis": result,
            "feasibility": (
                FeasibilityState.VALID
                if result.valid
                else FeasibilityState.INVALID
            ),
            "representation_id": representation_id,
        }

    """
    Deterministic structural analyzer for a single qubit.

    The adapter deliberately keeps quantum-specific mathematics here
    while exposing generic structural concepts:
      representation
      constraints
      invariants
      feasibility
    """

    DOMAIN = "quantum"
    KIND = "qubit_bloch"

    def analyze(self, state: QubitState) -> QuantumDiscoveryResult:
        signature = state.structural_signature()

        invariants: dict[str, float | bool | str] = {
            "bloch_norm": signature.bloch_norm,
            "bloch_norm_squared": signature.bloch_norm_squared,
            "purity": signature.purity,
            "trace": signature.trace,
            "positive_semidefinite": signature.positive_semidefinite,
            "state_class": signature.state_class.value,
            "constraint": "||r|| <= 1",
        }

        return QuantumDiscoveryResult(
            state=state,
            state_class=signature.state_class,
            invariants=invariants,
            valid=state.is_valid(),
        )

    def representation_payload(self, state: QubitState) -> dict[str, Any]:
        """
        Produce the generic representation payload expected by
        Structural Discovery-style consumers.
        """
        result = self.analyze(state)

        return {
            "domain": self.DOMAIN,
            "kind": self.KIND,
            "data": {
                "bloch_vector": state.bloch.as_tuple(),
                "state_class": result.state_class.value,
                "density_matrix": {
                    "a": state.to_density_matrix().a,
                    "b": state.to_density_matrix().b,
                    "c": state.to_density_matrix().c,
                    "d": state.to_density_matrix().d,
                },
            },
            "constraints": [
                {
                    "name": "bloch_ball",
                    "condition": "||r|| <= 1",
                    "satisfied": result.valid,
                },
                {
                    "name": "unit_trace",
                    "condition": "Tr(rho) = 1",
                    "satisfied": abs(
                        float(state.to_density_matrix().trace().real) - 1.0
                    ) <= state.tolerance,
                },
            ],
            "invariants": result.invariants,
            "evidence": {
                "state": "COMPUTED",
                "invariants": "DERIVED",
                "provenance": "barrot_agent.geometry.quantum",
            },
        }

    def structural_signature(self, state: QubitState) -> dict[str, Any]:
        """
        Return a generic structural signature suitable for comparison
        with other representations.
        """
        result = self.analyze(state)

        return {
            "domain": self.DOMAIN,
            "kind": self.KIND,
            "feasibility": "VALID" if result.valid else "INVALID",
            "invariants": result.invariants,
            "provenance_note": (
                "Deterministic qubit Bloch representation; "
                "invariants computed from the state representation."
            ),
        }
