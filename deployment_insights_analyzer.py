"""
Deployment Insights Analyzer — Barrot Apex Lattice
Analyzes multi-platform deployment performance and extracts optimization insights.

Usage:
    python deployment_insights_analyzer.py [--platform PLATFORM] [--report]

Platforms: huggingface | databricks | all
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_REPO_ROOT = Path(__file__).parent
_APEX = _REPO_ROOT / ".apex_lattice"
_DEPLOY_DIR = _APEX / "deployment_analytics"
_DEPLOY_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Metric loaders
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def load_hf_metrics() -> Dict[str, Any]:
    return _load_json(_DEPLOY_DIR / "hf_performance_metrics.json")


def load_databricks_metrics() -> Dict[str, Any]:
    return _load_json(_DEPLOY_DIR / "databricks_optimization.json")


# ---------------------------------------------------------------------------
# HuggingFace analysis
# ---------------------------------------------------------------------------

def analyze_hf_performance() -> Dict[str, Any]:
    """Extract and analyze Hugging Face deployment performance metrics."""
    metrics = load_hf_metrics()
    if not metrics:
        return {"error": "hf_performance_metrics.json not found"}

    models = metrics.get("model_performance", {})
    deploy_stats = metrics.get("deployment_statistics", {})
    inference_opt = metrics.get("inference_optimization", {})

    # Find best model per task
    best_math = max(models.items(), key=lambda x: x[1].get("mathematical_reasoning_score", 0))
    best_proof = max(models.items(), key=lambda x: x[1].get("proof_verification_score", 0))
    best_latency = min(models.items(), key=lambda x: x[1].get("avg_inference_latency_ms", 9999))

    # Research utilization by problem
    research_apps = metrics.get("research_applications", {})
    most_used = max(research_apps.items(), key=lambda x: x[1].get("successful_computations", 0))
    most_insights = max(research_apps.items(), key=lambda x: x[1].get("novel_insights_generated", 0))

    # Compute weighted research quality score
    total_computations = sum(
        app.get("successful_computations", 0) for app in research_apps.values()
    )
    weighted_quality = (
        sum(
            app.get("avg_response_quality", 0) * app.get("successful_computations", 0)
            for app in research_apps.values()
        )
        / max(total_computations, 1)
    )

    analysis = {
        "platform": "HuggingFace",
        "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        "model_rankings": {
            "best_mathematical_reasoning": {
                "model": best_math[0],
                "score": best_math[1].get("mathematical_reasoning_score"),
            },
            "best_proof_verification": {
                "model": best_proof[0],
                "score": best_proof[1].get("proof_verification_score"),
            },
            "lowest_latency": {
                "model": best_latency[0],
                "latency_ms": best_latency[1].get("avg_inference_latency_ms"),
            },
        },
        "research_utilization": {
            "total_computations": total_computations,
            "weighted_quality_score": round(weighted_quality, 3),
            "most_computed_problem": most_used[0],
            "most_insights_problem": most_insights[0],
            "total_novel_insights": sum(
                app.get("novel_insights_generated", 0) for app in research_apps.values()
            ),
        },
        "deployment_health": {
            "total_api_calls": deploy_stats.get("total_api_calls"),
            "error_rate": deploy_stats.get("error_rate"),
            "uptime_pct": deploy_stats.get("uptime_pct"),
            "peak_concurrent": deploy_stats.get("peak_concurrent_requests"),
        },
        "optimization_status": {
            "quantization": inference_opt.get("quantization", {}).get("method"),
            "latency_reduction_pct": inference_opt.get("quantization", {}).get("latency_reduction_pct"),
            "kv_cache_hit_rate": inference_opt.get("caching", {}).get("cache_hit_rate"),
            "dynamic_batching": inference_opt.get("batching", {}).get("dynamic_batching_enabled"),
        },
        "recommendations": _hf_recommendations(metrics),
    }
    return analysis


def _hf_recommendations(metrics: Dict[str, Any]) -> List[str]:
    """Generate HF optimization recommendations."""
    recs = []
    deploy_stats = metrics.get("deployment_statistics", {})
    inference_opt = metrics.get("inference_optimization", {})

    if deploy_stats.get("error_rate", 0) > 0.02:
        recs.append("Error rate exceeds 2% — investigate timeouts and input validation.")
    if deploy_stats.get("peak_concurrent_requests", 0) > 20:
        recs.append("High peak concurrency — consider horizontal scaling or request queuing.")
    cache_hit = inference_opt.get("caching", {}).get("cache_hit_rate", 0)
    if cache_hit < 0.5:
        recs.append(f"KV cache hit rate {cache_hit:.1%} is below 50% — expand prefix cache pool.")
    if not inference_opt.get("batching", {}).get("dynamic_batching_enabled"):
        recs.append("Enable dynamic batching to reduce padding overhead by ~43%.")
    if not recs:
        recs.append("Platform is well-optimized. Continue monitoring error rate and latency.")
    return recs


# ---------------------------------------------------------------------------
# Databricks analysis
# ---------------------------------------------------------------------------

def analyze_databricks_performance() -> Dict[str, Any]:
    """Extract and analyze Databricks deployment performance metrics."""
    metrics = load_databricks_metrics()
    if not metrics:
        return {"error": "databricks_optimization.json not found"}

    clusters = metrics.get("cluster_configurations", {})
    jobs = metrics.get("job_performance", {})
    opt = metrics.get("optimization_findings", {})
    cost = metrics.get("cost_analysis", {})

    # Job health analysis
    job_health = {}
    for job_name, job_data in jobs.items():
        success_rate = job_data.get("success_rate", 1.0)
        job_health[job_name] = {
            "success_rate": success_rate,
            "health": "healthy" if success_rate >= 0.95 else "degraded" if success_rate >= 0.85 else "critical",
            "avg_duration_min": job_data.get("avg_duration_minutes"),
            "avg_dbu": job_data.get("avg_dbu_consumption"),
        }

    # Cost efficiency
    spend = cost.get("total_spend_usd", 0)
    savings_pct = cost.get("optimization_savings_pct", 0)
    pre_optimization_spend = spend / (1 - savings_pct / 100) if savings_pct < 100 else spend

    # Parallelization efficiency
    par = opt.get("parallelization", {})
    workers = par.get("optimal_worker_count", 1)
    speedup = par.get("speedup_vs_sequential", 1.0)
    ideal_speedup = float(workers)
    efficiency_pct = (speedup / ideal_speedup * 100) if ideal_speedup > 0 else 0

    analysis = {
        "platform": "Databricks",
        "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        "job_health": job_health,
        "cost_efficiency": {
            "total_spend_usd": spend,
            "optimization_savings_pct": savings_pct,
            "pre_optimization_spend_usd": round(pre_optimization_spend, 2),
            "savings_achieved_usd": round(pre_optimization_spend - spend, 2),
            "cost_per_research_cycle_usd": cost.get("cost_per_research_cycle_usd"),
        },
        "parallelization": {
            "optimal_workers": workers,
            "achieved_speedup": speedup,
            "parallel_efficiency_pct": round(efficiency_pct, 1),
            "communication_overhead_pct": par.get("communication_overhead_pct"),
        },
        "storage_optimization": {
            "query_speedup": opt.get("delta_lake_benefits", {}).get("query_speedup"),
            "storage_reduction_pct": opt.get("delta_lake_benefits", {}).get("storage_reduction_pct"),
            "time_travel_days": opt.get("delta_lake_benefits", {}).get("time_travel_days"),
        },
        "ml_tracking": {
            "experiments_tracked": opt.get("mlflow_integration", {}).get("experiments_tracked"),
            "models_registered": opt.get("mlflow_integration", {}).get("models_registered"),
            "best_run_metric": opt.get("mlflow_integration", {}).get("best_run_metric"),
        },
        "recommendations": _databricks_recommendations(metrics),
    }
    return analysis


def _databricks_recommendations(metrics: Dict[str, Any]) -> List[str]:
    """Generate Databricks optimization recommendations."""
    recs = []
    jobs = metrics.get("job_performance", {})
    cost = metrics.get("cost_analysis", {})
    opt = metrics.get("optimization_findings", {})

    for job_name, job_data in jobs.items():
        if job_data.get("success_rate", 1.0) < 0.95:
            recs.append(
                f"Job '{job_name}' success rate {job_data['success_rate']:.1%} "
                "< 95% — review error logs and add retry logic."
            )

    par = opt.get("parallelization", {})
    if par.get("communication_overhead_pct", 0) > 15:
        recs.append("Communication overhead > 15% — consider co-locating shuffle-heavy stages.")

    if cost.get("optimization_savings_pct", 0) < 30:
        recs.append(
            "Cost savings below 30% — expand spot instance usage and off-peak scheduling."
        )

    if not opt.get("delta_lake_benefits", {}).get("acid_transactions"):
        recs.append("Enable Delta Lake ACID transactions for safe concurrent writes.")

    if not recs:
        recs.append("Databricks cluster is well-optimized. Continue monitoring job success rates.")
    return recs


# ---------------------------------------------------------------------------
# Synthesized insights
# ---------------------------------------------------------------------------

def synthesize_cross_platform_insights(
    hf_analysis: Dict[str, Any],
    db_analysis: Dict[str, Any],
) -> Dict[str, Any]:
    """Combine HF and Databricks insights into unified deployment recommendations."""
    synthesis: Dict[str, Any] = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "platforms_analyzed": ["HuggingFace", "Databricks"],
        "unified_recommendations": [],
        "cost_summary": {},
        "research_throughput": {},
    }

    # Combine recommendations
    all_recs: List[str] = []
    all_recs += [f"[HF] {r}" for r in hf_analysis.get("recommendations", [])]
    all_recs += [f"[DB] {r}" for r in db_analysis.get("recommendations", [])]
    synthesis["unified_recommendations"] = all_recs

    # Cost summary
    db_cost = db_analysis.get("cost_efficiency", {})
    synthesis["cost_summary"] = {
        "databricks_total_spend": db_cost.get("total_spend_usd"),
        "databricks_savings": db_cost.get("optimization_savings_pct"),
        "combined_efficiency_score": _compute_efficiency_score(hf_analysis, db_analysis),
    }

    # Research throughput
    hf_research = hf_analysis.get("research_utilization", {})
    synthesis["research_throughput"] = {
        "total_novel_insights": hf_research.get("total_novel_insights"),
        "total_computations_hf": hf_research.get("total_computations"),
        "databricks_parallel_efficiency_pct": db_analysis.get("parallelization", {}).get(
            "parallel_efficiency_pct"
        ),
        "weighted_research_quality": hf_research.get("weighted_quality_score"),
    }

    return synthesis


def _compute_efficiency_score(hf: Dict, db: Dict) -> float:
    """Compute a composite deployment efficiency score 0–1."""
    scores = []
    if (uptime := hf.get("deployment_health", {}).get("uptime_pct")):
        scores.append(uptime / 100)
    if (err := hf.get("deployment_health", {}).get("error_rate")) is not None:
        scores.append(1.0 - min(err * 10, 1.0))
    if (savings := db.get("cost_efficiency", {}).get("optimization_savings_pct")):
        scores.append(savings / 100)
    if (par_eff := db.get("parallelization", {}).get("parallel_efficiency_pct")):
        scores.append(par_eff / 100)
    return round(sum(scores) / len(scores), 3) if scores else 0.0


def save_analysis(analysis: Dict[str, Any], name: str) -> Path:
    """Save an analysis dict as JSON."""
    path = _DEPLOY_DIR / f"{name}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
    path.write_text(json.dumps(analysis, indent=2), encoding="utf-8")
    print(f"  ✓ Saved: {path}")
    return path


def print_analysis_summary(analysis: Dict[str, Any]) -> None:
    """Print a human-readable analysis summary."""
    platform = analysis.get("platform", "Unknown")
    print(f"\n{'='*60}")
    print(f"DEPLOYMENT ANALYSIS: {platform}")
    print(f"Timestamp: {analysis.get('analysis_timestamp', 'N/A')}")
    print(f"{'='*60}")

    if "error" in analysis:
        print(f"ERROR: {analysis['error']}")
        return

    if platform == "HuggingFace":
        health = analysis.get("deployment_health", {})
        print(f"  Uptime:        {health.get('uptime_pct', 'N/A')}%")
        print(f"  Error rate:    {health.get('error_rate', 'N/A')}")
        print(f"  API calls:     {health.get('total_api_calls', 'N/A')}")
        research = analysis.get("research_utilization", {})
        print(f"  Novel insights:{research.get('total_novel_insights', 'N/A')}")
        print(f"  Quality score: {research.get('weighted_quality_score', 'N/A')}")

    elif platform == "Databricks":
        cost = analysis.get("cost_efficiency", {})
        print(f"  Total spend:   ${cost.get('total_spend_usd', 'N/A')}")
        print(f"  Cost savings:  {cost.get('optimization_savings_pct', 'N/A')}%")
        par = analysis.get("parallelization", {})
        print(f"  Parallel eff:  {par.get('parallel_efficiency_pct', 'N/A')}%")
        for job, health in analysis.get("job_health", {}).items():
            emoji = "✓" if health["health"] == "healthy" else "⚠"
            print(f"  {emoji} {job}: {health['health']} ({health['success_rate']:.1%})")

    recs = analysis.get("recommendations", [])
    if recs:
        print("\n  Recommendations:")
        for rec in recs:
            print(f"    • {rec}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Barrot Apex Lattice — Deployment Insights Analyzer")
    parser.add_argument(
        "--platform",
        choices=["huggingface", "databricks", "all"],
        default="all",
        help="Platform to analyze",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Save analysis to JSON files",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("BARROT APEX LATTICE — DEPLOYMENT INSIGHTS ANALYZER")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    if args.platform in ("huggingface", "all"):
        hf_analysis = analyze_hf_performance()
        print_analysis_summary(hf_analysis)
        if args.report:
            save_analysis(hf_analysis, "hf_analysis")

    if args.platform in ("databricks", "all"):
        db_analysis = analyze_databricks_performance()
        print_analysis_summary(db_analysis)
        if args.report:
            save_analysis(db_analysis, "databricks_analysis")

    if args.platform == "all":
        hf_analysis = analyze_hf_performance()
        db_analysis = analyze_databricks_performance()
        synthesis = synthesize_cross_platform_insights(hf_analysis, db_analysis)
        print(f"\n{'='*60}")
        print("UNIFIED CROSS-PLATFORM INSIGHTS")
        print(f"{'='*60}")
        print(f"  Efficiency score: {synthesis['cost_summary'].get('combined_efficiency_score')}")
        print("  Recommendations:")
        for rec in synthesis.get("unified_recommendations", []):
            print(f"    • {rec}")
        if args.report:
            save_analysis(synthesis, "cross_platform_synthesis")

    print("\nDeployment analysis complete.")


if __name__ == "__main__":
    main()
