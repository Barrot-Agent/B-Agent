"""
Quantum Algorithms Module — Barrot Apex Lattice Quantum Engine
Quantum-inspired algorithms for Millennium Prize Problem research.
"""
from __future__ import annotations

import math
import cmath
import random
import itertools
from typing import Callable, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Core quantum state types
# ---------------------------------------------------------------------------

class QuantumState:
    """Represents a normalized quantum state as a complex amplitude vector."""

    def __init__(self, amplitudes: np.ndarray) -> None:
        self.amplitudes = np.asarray(amplitudes, dtype=complex)
        self._normalize()

    def _normalize(self) -> None:
        norm = np.linalg.norm(self.amplitudes)
        if norm > 1e-12:
            self.amplitudes /= norm

    @classmethod
    def zero(cls, n_qubits: int) -> "QuantumState":
        """Create |0...0⟩ state for n_qubits."""
        v = np.zeros(2 ** n_qubits, dtype=complex)
        v[0] = 1.0
        return cls(v)

    @classmethod
    def uniform_superposition(cls, n_qubits: int) -> "QuantumState":
        """Create uniform superposition (H⊗n)|0⟩."""
        size = 2 ** n_qubits
        v = np.ones(size, dtype=complex) / math.sqrt(size)
        return cls(v)

    @property
    def n_qubits(self) -> int:
        return int(math.log2(len(self.amplitudes)))

    def measure(self) -> int:
        """Simulate a projective measurement; returns classical outcome."""
        probs = np.abs(self.amplitudes) ** 2
        probs /= probs.sum()
        return int(np.random.choice(len(probs), p=probs))

    def probabilities(self) -> np.ndarray:
        return np.abs(self.amplitudes) ** 2

    def inner_product(self, other: "QuantumState") -> complex:
        return np.vdot(self.amplitudes, other.amplitudes)

    def fidelity(self, other: "QuantumState") -> float:
        return float(abs(self.inner_product(other)) ** 2)

    def __repr__(self) -> str:
        return f"QuantumState(n_qubits={self.n_qubits})"


# ---------------------------------------------------------------------------
# Quantum gates
# ---------------------------------------------------------------------------

class Gates:
    """Standard quantum gate matrices."""

    @staticmethod
    def hadamard() -> np.ndarray:
        return np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)

    @staticmethod
    def pauli_x() -> np.ndarray:
        return np.array([[0, 1], [1, 0]], dtype=complex)

    @staticmethod
    def pauli_y() -> np.ndarray:
        return np.array([[0, -1j], [1j, 0]], dtype=complex)

    @staticmethod
    def pauli_z() -> np.ndarray:
        return np.array([[1, 0], [0, -1]], dtype=complex)

    @staticmethod
    def phase(theta: float) -> np.ndarray:
        return np.array([[1, 0], [0, cmath.exp(1j * theta)]], dtype=complex)

    @staticmethod
    def rx(theta: float) -> np.ndarray:
        c, s = math.cos(theta / 2), math.sin(theta / 2)
        return np.array([[c, -1j * s], [-1j * s, c]], dtype=complex)

    @staticmethod
    def ry(theta: float) -> np.ndarray:
        c, s = math.cos(theta / 2), math.sin(theta / 2)
        return np.array([[c, -s], [s, c]], dtype=complex)

    @staticmethod
    def rz(theta: float) -> np.ndarray:
        return np.diag([cmath.exp(-1j * theta / 2), cmath.exp(1j * theta / 2)])

    @staticmethod
    def cnot() -> np.ndarray:
        return np.array(
            [[1, 0, 0, 0],
             [0, 1, 0, 0],
             [0, 0, 0, 1],
             [0, 0, 1, 0]],
            dtype=complex,
        )

    @staticmethod
    def tensor(*matrices: np.ndarray) -> np.ndarray:
        result = matrices[0]
        for m in matrices[1:]:
            result = np.kron(result, m)
        return result


# ---------------------------------------------------------------------------
# Grover's algorithm (quantum search)
# ---------------------------------------------------------------------------

def grover_oracle(n: int, targets: List[int]) -> np.ndarray:
    """Build oracle matrix that flips the phase of target states."""
    size = 2 ** n
    diag = np.ones(size, dtype=complex)
    for t in targets:
        diag[t] = -1.0
    return np.diag(diag)


def grover_diffusion(n: int) -> np.ndarray:
    """Grover diffusion operator 2|s⟩⟨s| - I."""
    size = 2 ** n
    s = np.ones(size, dtype=complex) / math.sqrt(size)
    return 2 * np.outer(s, s.conj()) - np.eye(size, dtype=complex)


def grover_search(
    n_qubits: int,
    oracle_targets: List[int],
    n_iterations: Optional[int] = None,
) -> Tuple[int, float]:
    """
    Simulate Grover's search algorithm.

    Returns
    -------
    (best_result, success_probability)
    """
    size = 2 ** n_qubits
    if n_iterations is None:
        m = len(oracle_targets) or 1
        n_iterations = max(1, round(math.pi / 4 * math.sqrt(size / m)))

    state = QuantumState.uniform_superposition(n_qubits)
    oracle = grover_oracle(n_qubits, oracle_targets)
    diffusion = grover_diffusion(n_qubits)

    for _ in range(n_iterations):
        state.amplitudes = oracle @ state.amplitudes
        state.amplitudes = diffusion @ state.amplitudes

    probs = state.probabilities()
    result = int(np.argmax(probs))
    success_prob = float(sum(probs[t] for t in oracle_targets))
    return result, success_prob


# ---------------------------------------------------------------------------
# Quantum Fourier Transform
# ---------------------------------------------------------------------------

def qft_matrix(n: int) -> np.ndarray:
    """Build the QFT matrix for n qubits (size 2^n × 2^n)."""
    size = 2 ** n
    omega = cmath.exp(2j * math.pi / size)
    return np.array(
        [[omega ** (j * k) for k in range(size)] for j in range(size)],
        dtype=complex,
    ) / math.sqrt(size)


def apply_qft(state: QuantumState) -> QuantumState:
    """Apply the Quantum Fourier Transform to a state."""
    n = state.n_qubits
    qft = qft_matrix(n)
    return QuantumState(qft @ state.amplitudes)


def apply_inverse_qft(state: QuantumState) -> QuantumState:
    """Apply the inverse QFT."""
    n = state.n_qubits
    qft = qft_matrix(n)
    return QuantumState(qft.conj().T @ state.amplitudes)


# ---------------------------------------------------------------------------
# Quantum phase estimation
# ---------------------------------------------------------------------------

def quantum_phase_estimation(
    unitary_eigenvalue: complex,
    n_precision_qubits: int = 8,
) -> float:
    """
    Simulate QPE to estimate the phase φ of eigenvalue e^{2πiφ}.

    Parameters
    ----------
    unitary_eigenvalue : e^{2πiφ}
    n_precision_qubits : bits of precision

    Returns
    -------
    Estimated phase φ ∈ [0, 1)
    """
    phi = cmath.phase(unitary_eigenvalue) / (2 * math.pi)
    phi = phi % 1.0

    # Simulate with controlled precision and shot noise
    size = 2 ** n_precision_qubits
    amplitudes = np.zeros(size, dtype=complex)
    # Build peaked distribution around true phase
    true_bin = int(phi * size)
    for k in range(size):
        diff = (k - true_bin) % size
        if diff > size // 2:
            diff -= size
        amplitudes[k] = 1.0 / (1.0 + diff ** 2) if diff != 0 else 1.0

    state = QuantumState(amplitudes)
    measured = state.measure()
    return measured / size


# ---------------------------------------------------------------------------
# QAOA (Quantum Approximate Optimisation Algorithm)
# ---------------------------------------------------------------------------

class QAOALayer:
    """Single QAOA layer with problem Hamiltonian and mixer."""

    def __init__(self, gamma: float, beta: float) -> None:
        self.gamma = gamma
        self.beta = beta

    def apply_problem_hamiltonian(
        self, amplitudes: np.ndarray, cost_values: np.ndarray
    ) -> np.ndarray:
        """Phase-encode cost function: e^{-iγC}|x⟩."""
        phases = np.exp(-1j * self.gamma * cost_values)
        return phases * amplitudes

    def apply_mixer(self, amplitudes: np.ndarray, n_qubits: int) -> np.ndarray:
        """Apply X-mixer: e^{-iβB} where B = Σ X_i (approx)."""
        # Approximate mixer via first-order expansion for small beta
        size = 2 ** n_qubits
        mixed = (1 - 1j * self.beta) * amplitudes
        # Bitflip contribution
        for i in range(n_qubits):
            flipped = np.zeros(size, dtype=complex)
            for idx in range(size):
                flipped[idx ^ (1 << i)] += amplitudes[idx]
            mixed += (-1j * self.beta) * flipped
        norm = np.linalg.norm(mixed)
        return mixed / norm if norm > 1e-12 else mixed


def qaoa_optimize(
    cost_function: Callable[[int], float],
    n_qubits: int,
    n_layers: int = 3,
    n_shots: int = 1000,
) -> Tuple[int, float]:
    """
    Run QAOA to minimize cost_function over n_qubits binary strings.

    Returns
    -------
    (best_bitstring, best_cost)
    """
    size = 2 ** n_qubits
    cost_values = np.array([cost_function(x) for x in range(size)])

    # Random initial parameters
    rng = np.random.default_rng(42)
    gammas = rng.uniform(0, math.pi, n_layers)
    betas = rng.uniform(0, math.pi / 2, n_layers)

    amplitudes = np.ones(size, dtype=complex) / math.sqrt(size)

    for gamma, beta in zip(gammas, betas):
        layer = QAOALayer(gamma, beta)
        amplitudes = layer.apply_problem_hamiltonian(amplitudes, cost_values)
        amplitudes = layer.apply_mixer(amplitudes, n_qubits)

    state = QuantumState(amplitudes)
    counts: dict[int, int] = {}
    for _ in range(n_shots):
        m = state.measure()
        counts[m] = counts.get(m, 0) + 1

    best = min(counts, key=lambda x: cost_function(x))
    return best, cost_function(best)


# ---------------------------------------------------------------------------
# Amplitude amplification (generalization of Grover)
# ---------------------------------------------------------------------------

def amplitude_amplification(
    state: QuantumState,
    good_indices: List[int],
    n_steps: int = 1,
) -> QuantumState:
    """
    Generic amplitude amplification targeting good_indices.
    """
    n = state.n_qubits
    oracle = grover_oracle(n, good_indices)
    diffusion = grover_diffusion(n)
    amplitudes = state.amplitudes.copy()
    for _ in range(n_steps):
        amplitudes = oracle @ amplitudes
        amplitudes = diffusion @ amplitudes
    return QuantumState(amplitudes)
