"""
Kaggle Findings Integration — Barrot Apex Lattice
Maps Kaggle competition methodologies to Millennium Prize Problem research.

Usage:
    python kaggle_findings_integration.py [--problem PROBLEM] [--export-dir DIR]
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

_REPO_ROOT = Path(__file__).parent
_APEX = _REPO_ROOT / ".apex_lattice"
_KAGGLE_DIR = _APEX / "kaggle_findings"
_KAGGLE_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Technique registry
# ---------------------------------------------------------------------------

TECHNIQUES: Dict[str, Dict[str, Any]] = {
    "gradient_boosting_ensemble": {
        "description": "XGBoost + LightGBM + CatBoost stacking",
        "problem_relevance": {
            "BSD": 0.91,
            "Hodge": 0.45,
            "Navier_Stokes": 0.52,
            "P_vs_NP": 0.63,
            "Riemann": 0.88,
            "Yang_Mills": 0.41,
        },
        "transfer_method": "Feature engineering from mathematical invariants → rank/zero prediction",
        "sample_complexity": "medium",
        "interpretability": "medium",
    },
    "graph_neural_network": {
        "description": "Message-passing GNNs with attention mechanisms",
        "problem_relevance": {
            "BSD": 0.78,
            "Hodge": 0.82,
            "Navier_Stokes": 0.61,
            "P_vs_NP": 0.95,
            "Riemann": 0.70,
            "Yang_Mills": 0.74,
        },
        "transfer_method": "Graph representation of mathematical structures → structural prediction",
        "sample_complexity": "high",
        "interpretability": "medium",
    },
    "physics_informed_nn": {
        "description": "PINNs with PDE residual loss and adaptive weighting",
        "problem_relevance": {
            "BSD": 0.55,
            "Hodge": 0.48,
            "Navier_Stokes": 0.97,
            "P_vs_NP": 0.39,
            "Riemann": 0.51,
            "Yang_Mills": 0.88,
        },
        "transfer_method": "PDE residual minimization → solution regularity probing",
        "sample_complexity": "low",
        "interpretability": "high",
    },
    "contrastive_learning": {
        "description": "SimCLR + momentum contrastive encoders",
        "problem_relevance": {
            "BSD": 0.67,
            "Hodge": 0.90,
            "Navier_Stokes": 0.58,
            "P_vs_NP": 0.72,
            "Riemann": 0.83,
            "Yang_Mills": 0.69,
        },
        "transfer_method": "Contrastive embeddings → algebraic/topological structure discovery",
        "sample_complexity": "high",
        "interpretability": "low",
    },
    "variational_autoencoder": {
        "description": "β-VAE with discrete and continuous latent codes",
        "problem_relevance": {
            "BSD": 0.74,
            "Hodge": 0.71,
            "Navier_Stokes": 0.65,
            "P_vs_NP": 0.58,
            "Riemann": 0.89,
            "Yang_Mills": 0.62,
        },
        "transfer_method": "Latent distribution → zero/eigenvalue distribution modeling",
        "sample_complexity": "medium",
        "interpretability": "medium",
    },
    "transformer_architecture": {
        "description": "Multi-head attention with learned positional encodings",
        "problem_relevance": {
            "BSD": 0.71,
            "Hodge": 0.76,
            "Navier_Stokes": 0.82,
            "P_vs_NP": 0.84,
            "Riemann": 0.79,
            "Yang_Mills": 0.91,
        },
        "transfer_method": "Sequence attention → gauge field / proof state modeling",
        "sample_complexity": "high",
        "interpretability": "low",
    },
    "topological_data_analysis": {
        "description": "Persistent homology + Mapper algorithm",
        "problem_relevance": {
            "BSD": 0.82,
            "Hodge": 0.88,
            "Navier_Stokes": 0.75,
            "P_vs_NP": 0.79,
            "Riemann": 0.84,
            "Yang_Mills": 0.78,
        },
        "transfer_method": "Topological signatures → shape-based mathematical structure discovery",
        "sample_complexity": "low",
        "interpretability": "high",
    },
    "bayesian_optimization": {
        "description": "GP surrogate + UCB/EI acquisition functions",
        "problem_relevance": {
            "BSD": 0.86,
            "Hodge": 0.72,
            "Navier_Stokes": 0.79,
            "P_vs_NP": 0.67,
            "Riemann": 0.92,
            "Yang_Mills": 0.75,
        },
        "transfer_method": "Efficient black-box optimization → parameter search in mathematical spaces",
        "sample_complexity": "low",
        "interpretability": "high",
    },
    "symbolic_regression": {
        "description": "Genetic programming for formula discovery",
        "problem_relevance": {
            "BSD": 0.88,
            "Hodge": 0.81,
            "Navier_Stokes": 0.76,
            "P_vs_NP": 0.74,
            "Riemann": 0.91,
            "Yang_Mills": 0.80,
        },
        "transfer_method": "Symbolic formula discovery → new conjectural relationships",
        "sample_complexity": "low",
        "interpretability": "high",
    },
}

PROBLEMS: List[str] = ["BSD", "Hodge", "Navier_Stokes", "P_vs_NP", "Riemann", "Yang_Mills"]


# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------

def rank_techniques_for_problem(problem: str) -> List[Dict[str, Any]]:
    """
    Return techniques ranked by relevance score for a given problem.

    Parameters
    ----------
    problem : Name of the Millennium Prize Problem.

    Returns
    -------
    Sorted list of {technique, score, description, transfer_method}.
    """
    if problem not in PROBLEMS:
        raise ValueError(f"Unknown problem '{problem}'. Must be one of {PROBLEMS}.")

    ranked = []
    for name, meta in TECHNIQUES.items():
        score = meta["problem_relevance"].get(problem, 0.0)
        ranked.append({
            "technique": name,
            "score": score,
            "description": meta["description"],
            "transfer_method": meta["transfer_method"],
            "sample_complexity": meta["sample_complexity"],
            "interpretability": meta["interpretability"],
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked


def build_transfer_matrix() -> np.ndarray:
    """Build the full technique × problem transfer score matrix."""
    technique_names = list(TECHNIQUES.keys())
    matrix = np.zeros((len(technique_names), len(PROBLEMS)))
    for i, tech in enumerate(technique_names):
        for j, prob in enumerate(PROBLEMS):
            matrix[i, j] = TECHNIQUES[tech]["problem_relevance"].get(prob, 0.0)
    return matrix


def identify_synergies(threshold: float = 0.80) -> List[Dict[str, Any]]:
    """
    Identify problem pairs with high combined transfer potential.

    Parameters
    ----------
    threshold : Minimum technique score to include in synergy calculation.

    Returns
    -------
    List of synergy records sorted by combined score.
    """
    synergies = []
    for i in range(len(PROBLEMS)):
        for j in range(i + 1, len(PROBLEMS)):
            prob_a, prob_b = PROBLEMS[i], PROBLEMS[j]
            shared_techniques = [
                tech for tech, meta in TECHNIQUES.items()
                if meta["problem_relevance"].get(prob_a, 0) >= threshold
                and meta["problem_relevance"].get(prob_b, 0) >= threshold
            ]
            if shared_techniques:
                avg_score_a = np.mean([
                    TECHNIQUES[t]["problem_relevance"].get(prob_a, 0) for t in shared_techniques
                ])
                avg_score_b = np.mean([
                    TECHNIQUES[t]["problem_relevance"].get(prob_b, 0) for t in shared_techniques
                ])
                synergies.append({
                    "problem_a": prob_a,
                    "problem_b": prob_b,
                    "shared_techniques": shared_techniques,
                    "synergy_score": round(float((avg_score_a + avg_score_b) / 2), 3),
                })

    synergies.sort(key=lambda x: x["synergy_score"], reverse=True)
    return synergies


def generate_hybrid_model_spec(problem: str, n_top: int = 3) -> Dict[str, Any]:
    """
    Generate a hybrid model specification combining the top-N techniques for a problem.

    Parameters
    ----------
    problem : Target Millennium Prize Problem.
    n_top   : Number of top techniques to combine.

    Returns
    -------
    Hybrid model specification dict.
    """
    ranked = rank_techniques_for_problem(problem)[:n_top]
    return {
        "problem": problem,
        "model_name": f"barrot_{problem.lower()}_hybrid_v1",
        "components": [
            {
                "technique": r["technique"],
                "role": "primary" if i == 0 else "auxiliary",
                "weight": round(r["score"] / sum(x["score"] for x in ranked), 3),
                "transfer_method": r["transfer_method"],
            }
            for i, r in enumerate(ranked)
        ],
        "ensemble_strategy": "stacked_generalization",
        "expected_accuracy": round(float(np.mean([r["score"] for r in ranked])) * 0.95, 3),
        "training_data_requirements": {
            "min_samples": 1000,
            "preferred_samples": 10000,
            "validation_strategy": "5-fold cross-validation",
        },
    }


def export_findings(output_dir: Path) -> None:
    """Export all Kaggle integration findings to the apex_lattice directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()

    # Export transfer matrix
    matrix = build_transfer_matrix()
    transfer_data = {
        "generated": ts,
        "techniques": list(TECHNIQUES.keys()),
        "problems": PROBLEMS,
        "matrix": matrix.tolist(),
    }
    (output_dir / "transfer_matrix.json").write_text(
        json.dumps(transfer_data, indent=2), encoding="utf-8"
    )

    # Export synergies
    synergies = identify_synergies(threshold=0.78)
    (output_dir / "problem_synergies.json").write_text(
        json.dumps({"generated": ts, "synergies": synergies}, indent=2), encoding="utf-8"
    )

    # Export hybrid model specs for each problem
    hybrid_specs = {prob: generate_hybrid_model_spec(prob) for prob in PROBLEMS}
    (output_dir / "hybrid_model_specs.json").write_text(
        json.dumps({"generated": ts, "models": hybrid_specs}, indent=2), encoding="utf-8"
    )

    print(f"  ✓ Exported transfer matrix, synergies, and hybrid specs to {output_dir}")


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

def print_problem_recommendations(problem: str) -> None:
    """Print technique recommendations for a problem."""
    ranked = rank_techniques_for_problem(problem)
    print(f"\n{'='*60}")
    print(f"TOP TECHNIQUE RECOMMENDATIONS FOR: {problem}")
    print(f"{'='*60}")
    for i, rec in enumerate(ranked[:5], 1):
        print(f"{i}. {rec['technique'].replace('_', ' ').title()}")
        print(f"   Score:       {rec['score']:.2f}")
        print(f"   Description: {rec['description']}")
        print(f"   Transfer:    {rec['transfer_method']}")
        print()


def print_synergy_report() -> None:
    """Print top problem synergies."""
    synergies = identify_synergies()
    print(f"\n{'='*60}")
    print("TOP CROSS-PROBLEM SYNERGIES")
    print(f"{'='*60}")
    for s in synergies[:5]:
        print(
            f"{s['problem_a']} ↔ {s['problem_b']}: "
            f"score={s['synergy_score']:.3f}, "
            f"shared={', '.join(s['shared_techniques'][:2])}"
            f"{'...' if len(s['shared_techniques']) > 2 else ''}"
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Barrot Apex Lattice — Kaggle Findings Integration")
    parser.add_argument(
        "--problem",
        choices=PROBLEMS + ["all"],
        default="all",
        help="Analyze a specific problem or all",
    )
    parser.add_argument(
        "--export-dir",
        type=str,
        default=str(_KAGGLE_DIR),
        help="Directory to export findings",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("BARROT APEX LATTICE — KAGGLE FINDINGS INTEGRATION")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    if args.problem == "all":
        for prob in PROBLEMS:
            print_problem_recommendations(prob)
        print_synergy_report()
    else:
        print_problem_recommendations(args.problem)
        spec = generate_hybrid_model_spec(args.problem)
        print(f"\nHybrid Model Spec: {json.dumps(spec, indent=2)}")

    # Export findings
    export_findings(Path(args.export_dir))
    print("\nKaggle integration analysis complete.")


if __name__ == "__main__":
    main()
