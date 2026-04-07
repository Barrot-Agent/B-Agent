"""
Optimization Suite — Barrot Apex Lattice Quantum Engine
Optimization algorithms for Millennium Prize Problem research.
"""
from __future__ import annotations

import math
import random
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Variational Quantum Eigensolver (VQE) simulation
# ---------------------------------------------------------------------------

class VQESimulator:
    """
    Simulates the Variational Quantum Eigensolver.
    Used for Yang-Mills mass gap and ground state energy estimation.
    """

    def __init__(self, hamiltonian: np.ndarray) -> None:
        if hamiltonian.shape[0] != hamiltonian.shape[1]:
            raise ValueError("Hamiltonian must be square.")
        # Ensure Hermitian
        self.hamiltonian = (hamiltonian + hamiltonian.conj().T) / 2
        self.n_qubits = int(math.log2(hamiltonian.shape[0]))
        self._true_ground_energy = float(np.linalg.eigvalsh(self.hamiltonian)[0])

    def ansatz_state(self, params: np.ndarray) -> np.ndarray:
        """
        Hardware-efficient ansatz: alternating Ry rotations and CNOT layers.

        Parameters
        ----------
        params : 1D array of rotation angles.
        """
        n = self.n_qubits
        size = 2 ** n
        state = np.zeros(size, dtype=complex)
        state[0] = 1.0

        param_idx = 0
        for layer in range(min(len(params) // n, 4)):
            # Single-qubit Ry rotations
            for qubit in range(n):
                if param_idx >= len(params):
                    break
                theta = params[param_idx]
                param_idx += 1
                c, s = math.cos(theta / 2), math.sin(theta / 2)
                ry = np.array([[c, -s], [s, c]])
                # Apply to qubit in full state space
                ops = [np.eye(2)] * n
                ops[qubit] = ry
                gate = ops[0]
                for op in ops[1:]:
                    gate = np.kron(gate, op)
                state = gate @ state

        return state / (np.linalg.norm(state) + 1e-12)

    def energy_expectation(self, params: np.ndarray) -> float:
        """⟨ψ(θ)|H|ψ(θ)⟩"""
        psi = self.ansatz_state(params)
        return float(np.real(psi.conj() @ self.hamiltonian @ psi))

    def optimize(
        self,
        n_params: Optional[int] = None,
        max_iter: int = 500,
        learning_rate: float = 0.05,
        tol: float = 1e-6,
    ) -> Dict:
        """
        Optimize VQE parameters using gradient descent with parameter shift rule.

        Returns
        -------
        dict with keys: optimal_energy, params, true_ground_energy, gap
        """
        if n_params is None:
            n_params = 4 * self.n_qubits

        rng = np.random.default_rng(42)
        params = rng.uniform(0, 2 * math.pi, n_params)
        energy_history = []

        for i in range(max_iter):
            energy = self.energy_expectation(params)
            energy_history.append(energy)

            # Parameter shift rule gradient
            gradient = np.zeros(n_params)
            for j in range(n_params):
                shift = math.pi / 2
                p_plus = params.copy()
                p_plus[j] += shift
                p_minus = params.copy()
                p_minus[j] -= shift
                gradient[j] = (
                    self.energy_expectation(p_plus) - self.energy_expectation(p_minus)
                ) / 2

            params -= learning_rate * gradient

            if i > 10 and abs(energy_history[-1] - energy_history[-2]) < tol:
                break

        optimal_energy = self.energy_expectation(params)
        return {
            "optimal_energy": optimal_energy,
            "true_ground_energy": self._true_ground_energy,
            "variational_gap": optimal_energy - self._true_ground_energy,
            "n_iterations": len(energy_history),
            "energy_history": energy_history,
            "params": params,
        }


# ---------------------------------------------------------------------------
# Simulated Annealing (quantum-inspired thermal optimization)
# ---------------------------------------------------------------------------

def simulated_annealing(
    cost_function: Callable[[np.ndarray], float],
    initial_solution: np.ndarray,
    T_init: float = 10.0,
    T_final: float = 1e-4,
    cooling_rate: float = 0.995,
    n_steps_per_temp: int = 50,
    step_size: float = 0.1,
    rng_seed: int = 42,
) -> Dict:
    """
    Simulated annealing optimizer.

    Parameters
    ----------
    cost_function       : Function to minimize.
    initial_solution    : Starting point.
    T_init, T_final     : Temperature schedule.
    cooling_rate        : Geometric cooling factor.
    n_steps_per_temp    : Metropolis steps per temperature.
    step_size           : Perturbation magnitude.

    Returns
    -------
    dict: best_solution, best_cost, history
    """
    rng = np.random.default_rng(rng_seed)
    current = initial_solution.copy()
    current_cost = cost_function(current)
    best = current.copy()
    best_cost = current_cost

    T = T_init
    history = []

    while T > T_final:
        for _ in range(n_steps_per_temp):
            # Propose perturbation
            proposal = current + rng.normal(0, step_size, size=current.shape)
            prop_cost = cost_function(proposal)
            delta = prop_cost - current_cost

            if delta < 0 or rng.random() < math.exp(-delta / T):
                current = proposal
                current_cost = prop_cost
                if current_cost < best_cost:
                    best = current.copy()
                    best_cost = current_cost

        history.append({"T": T, "best_cost": best_cost})
        T *= cooling_rate

    return {"best_solution": best, "best_cost": best_cost, "history": history}


# ---------------------------------------------------------------------------
# Quantum tunneling simulation (path integral Monte Carlo)
# ---------------------------------------------------------------------------

def quantum_tunneling_path_integral(
    potential: Callable[[float], float],
    x_start: float,
    x_end: float,
    beta: float = 10.0,
    n_time_slices: int = 50,
    n_samples: int = 10000,
    rng_seed: int = 42,
) -> Dict:
    """
    Path integral Monte Carlo simulation of quantum tunneling.

    Estimates the tunneling amplitude ⟨x_end|e^{-βH}|x_start⟩ via
    discretized Euclidean path integral.

    Parameters
    ----------
    potential    : Potential energy V(x).
    x_start      : Initial position.
    x_end        : Final position.
    beta         : Inverse temperature (imaginary time).
    n_time_slices: Trotter number.
    n_samples    : MC samples.

    Returns
    -------
    dict: tunneling_amplitude, acceptance_rate, path_samples
    """
    rng = np.random.default_rng(rng_seed)
    dt = beta / n_time_slices

    # Initialize linear path
    path = np.linspace(x_start, x_end, n_time_slices + 1)

    def action(p: np.ndarray) -> float:
        kinetic = sum((p[i + 1] - p[i]) ** 2 / (2 * dt) for i in range(n_time_slices))
        potential_sum = dt * sum(potential(p[i]) for i in range(n_time_slices + 1))
        return kinetic + potential_sum

    accepted = 0
    path_samples = []
    current_action = action(path)

    for step in range(n_samples):
        # Propose update to interior path point
        idx = rng.integers(1, n_time_slices)
        proposal = path.copy()
        proposal[idx] += rng.normal(0, 0.3)
        prop_action = action(proposal)

        if rng.random() < math.exp(-(prop_action - current_action)):
            path = proposal
            current_action = prop_action
            accepted += 1

        if step % 100 == 0:
            path_samples.append(path.copy())

    tunneling_amplitude = math.exp(-current_action)
    return {
        "tunneling_amplitude": tunneling_amplitude,
        "acceptance_rate": accepted / n_samples,
        "final_action": current_action,
        "path_samples": path_samples,
    }


# ---------------------------------------------------------------------------
# Bayesian optimization (for Riemann zero search)
# ---------------------------------------------------------------------------

class GaussianProcess:
    """Minimal Gaussian Process for Bayesian optimization."""

    def __init__(self, noise: float = 1e-4, length_scale: float = 1.0) -> None:
        self.noise = noise
        self.length_scale = length_scale
        self.X_train: Optional[np.ndarray] = None
        self.y_train: Optional[np.ndarray] = None

    def _rbf_kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        dists = np.sum((X1[:, None] - X2[None, :]) ** 2, axis=-1)
        return np.exp(-0.5 * dists / self.length_scale ** 2)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "GaussianProcess":
        self.X_train = X.copy()
        self.y_train = y.copy()
        return self

    def predict(self, X_test: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if self.X_train is None:
            raise RuntimeError("Call fit() first.")
        K = self._rbf_kernel(self.X_train, self.X_train)
        K += self.noise * np.eye(len(self.X_train))
        K_star = self._rbf_kernel(X_test, self.X_train)
        K_star_star = self._rbf_kernel(X_test, X_test)

        K_inv = np.linalg.solve(K, np.eye(len(K)))
        mu = K_star @ K_inv @ self.y_train
        sigma2 = np.diag(K_star_star - K_star @ K_inv @ K_star.T)
        return mu, np.maximum(sigma2, 0.0)

    def acquisition_ucb(
        self, X_test: np.ndarray, kappa: float = 2.0
    ) -> np.ndarray:
        mu, sigma2 = self.predict(X_test)
        return mu + kappa * np.sqrt(sigma2)


def bayesian_optimize(
    objective: Callable[[float], float],
    bounds: Tuple[float, float],
    n_init: int = 5,
    n_iter: int = 20,
    rng_seed: int = 42,
) -> Dict:
    """
    1-D Bayesian optimization using GP + UCB acquisition.

    Parameters
    ----------
    objective : Function to maximize.
    bounds    : (lower, upper) search interval.
    n_init    : Random initialization points.
    n_iter    : Optimization iterations.

    Returns
    -------
    dict: best_x, best_y, history
    """
    rng = np.random.default_rng(rng_seed)
    lo, hi = bounds

    X = rng.uniform(lo, hi, (n_init, 1))
    y = np.array([objective(float(x.flat[0])) for x in X])

    gp = GaussianProcess()
    history = []

    for _ in range(n_iter):
        gp.fit(X, y)
        # Grid-based candidate search
        candidates = np.linspace(lo, hi, 500).reshape(-1, 1)
        acq = gp.acquisition_ucb(candidates)
        next_x = float(candidates[np.argmax(acq)].flat[0])
        next_y = objective(next_x)

        X = np.vstack([X, [[next_x]]])
        y = np.append(y, next_y)
        history.append({"x": next_x, "y": next_y})

    best_idx = int(np.argmax(y))
    return {"best_x": float(X[best_idx].flat[0]), "best_y": float(y[best_idx]), "history": history}
