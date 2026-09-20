"""
Barrot V3 — Deterministic quantum-state geometry.

This module provides a minimal, dependency-free representation of a
single qubit in Bloch-vector and density-matrix form.

Design goals:
- deterministic mathematics
- explicit validity constraints
- typed state classification
- reversible representation conversion
- structural invariants suitable for Structural Discovery
- no LLM calls
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Iterable, Tuple


class QubitStateClass(str, Enum):
    PURE = "PURE"
    MIXED = "MIXED"
    INVALID = "INVALID"


@dataclass(frozen=True)
class BlochVector:
    """Three-dimensional Bloch representation r=(x,y,z)."""

    x: float
    y: float
    z: float

    def as_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)

    @property
    def norm_squared(self) -> float:
        return self.x * self.x + self.y * self.y + self.z * self.z

    @property
    def norm(self) -> float:
        return math.sqrt(self.norm_squared)

    def is_valid(self, tolerance: float = 1e-12) -> bool:
        return self.norm_squared <= 1.0 + tolerance


@dataclass(frozen=True)
class DensityMatrix:
    """Hermitian 2x2 qubit density matrix."""

    a: complex
    b: complex
    c: complex
    d: complex

    def trace(self) -> complex:
        return self.a + self.d

    def purity(self) -> float:
        # Tr(rho^2) for a 2x2 matrix. Take .real BEFORE float() --
        # float() cannot accept a complex value even when its imaginary
        # part is exactly zero, which crashed this on every real call.
        result = (
            (self.a * self.a + self.b * self.c)
            + (self.c * self.b + self.d * self.d)
        )
        return float(result.real)


@dataclass(frozen=True)
class QubitStructuralSignature:
    """Deterministic invariants exposed to Structural Discovery."""

    bloch_norm: float
    bloch_norm_squared: float
    purity: float
    state_class: QubitStateClass
    trace: float
    positive_semidefinite: bool


@dataclass(frozen=True)
class QubitState:
    """
    Canonical single-qubit state represented by its Bloch vector.

    Physical validity:
        ||r|| <= 1

    Pure states:
        ||r|| = 1

    Mixed states:
        ||r|| < 1
    """

    bloch: BlochVector
    tolerance: float = 1e-12

    @classmethod
    def from_xyz(
        cls,
        x: float,
        y: float,
        z: float,
        tolerance: float = 1e-12,
    ) -> "QubitState":
        return cls(BlochVector(float(x), float(y), float(z)), tolerance)

    @classmethod
    def from_density_matrix(
        cls,
        matrix: Iterable[Iterable[complex]],
        tolerance: float = 1e-10,
    ) -> "QubitState":
        rows = [list(row) for row in matrix]

        if len(rows) != 2 or any(len(row) != 2 for row in rows):
            raise ValueError("A qubit density matrix must be 2x2.")

        a, b = rows[0]
        c, d = rows[1]

        # Hermiticity.
        if abs(a.imag) > tolerance or abs(d.imag) > tolerance:
            raise ValueError("Density matrix diagonal entries must be real.")

        if abs(b - c.conjugate()) > tolerance:
            raise ValueError("Density matrix must be Hermitian.")

        trace = (a + d).real
        if abs(trace - 1.0) > tolerance:
            raise ValueError("Density matrix trace must equal 1.")

        # Bloch coordinates:
        # rho = 1/2 (I + x*sigma_x + y*sigma_y + z*sigma_z)
        x = 2.0 * b.real
        y = -2.0 * b.imag
        z = (a - d).real

        state = cls.from_xyz(x, y, z, tolerance)

        if not state.is_valid():
            raise ValueError("Density matrix is not positive semidefinite.")

        return state

    def to_density_matrix(self) -> DensityMatrix:
        x, y, z = self.bloch.as_tuple()

        return DensityMatrix(
            a=complex((1.0 + z) / 2.0),
            b=complex((x - 1j * y) / 2.0),
            c=complex((x + 1j * y) / 2.0),
            d=complex((1.0 - z) / 2.0),
        )

    def is_valid(self) -> bool:
        return self.bloch.is_valid(self.tolerance)

    def classify(self) -> QubitStateClass:
        if not self.is_valid():
            return QubitStateClass.INVALID

        if abs(self.bloch.norm_squared - 1.0) <= self.tolerance:
            return QubitStateClass.PURE

        return QubitStateClass.MIXED

    def purity(self) -> float:
        """
        Tr(rho^2) = (1 + ||r||^2) / 2.
        """
        return (1.0 + self.bloch.norm_squared) / 2.0

    def measurement_probability(self, axis: BlochVector) -> float:
        """
        Probability of the +1 outcome for a projective measurement
        along a unit measurement axis.
        """
        if not self.is_valid():
            raise ValueError("Cannot measure an invalid qubit state.")

        if abs(axis.norm - 1.0) > self.tolerance:
            raise ValueError("Measurement axis must be unit length.")

        dot = (
            self.bloch.x * axis.x
            + self.bloch.y * axis.y
            + self.bloch.z * axis.z
        )

        return (1.0 + dot) / 2.0

    def structural_signature(self) -> QubitStructuralSignature:
        matrix = self.to_density_matrix()

        return QubitStructuralSignature(
            bloch_norm=self.bloch.norm,
            bloch_norm_squared=self.bloch.norm_squared,
            purity=self.purity(),
            state_class=self.classify(),
            trace=float(matrix.trace().real),
            positive_semidefinite=self.is_valid(),
        )


def pure_state(theta: float, phi: float) -> QubitState:
    """
    Construct a pure qubit state from Bloch-sphere angles.

    theta: polar angle
    phi: azimuthal angle
    """
    return QubitState.from_xyz(
        math.sin(theta) * math.cos(phi),
        math.sin(theta) * math.sin(phi),
        math.cos(theta),
    )


def maximally_mixed_state() -> QubitState:
    return QubitState.from_xyz(0.0, 0.0, 0.0)
