"""
Sandbox Enhanced — Barrot Apex Lattice Master Orchestration System
Unifies all analyses, quantum computations, and report generation.

Usage:
    python sandbox_enhanced.py [--mode MODE] [--output DIR]

Modes: analyze | report | quantum | full
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(_REPO_ROOT))

from kaggle_findings_integration import (  # noqa: E402
    rank_techniques_for_problem,
    identify_synergies,
    generate_hybrid_model_spec,
    export_findings as export_kaggle_findings,
    PROBLEMS,
)
from deployment_insights_analyzer import (  # noqa: E402
    analyze_hf_performance,
    analyze_databricks_performance,
    synthesize_cross_platform_insights,
)
from generate_findings_report import (  # noqa: E402
    load_all_findings,
    generate_markdown_report,
    generate_json_report,
    generate_html_report,
)

_APEX = _REPO_ROOT / ".apex_lattice"
_REPORTS_DIR = _APEX / "reports"
_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

_LOG_FILES: Dict[str, Path] = {
    "BSD": _APEX / "BSD.log",
    "Hodge": _APEX / "Hodge.log",
    "Navier_Stokes": _APEX / "Navier_Stokes.log",
    "P_vs_NP": _APEX / "P_vs_NP.log",
    "Poincare": _APEX / "Poincare.log",
    "Riemann": _APEX / "Riemann.log",
    "Yang_Mills": _APEX / "Yang_Mills.log",
}


# ---------------------------------------------------------------------------
# Log file readers / analyzers
# ---------------------------------------------------------------------------

def count_rounds(log_text: str) -> int:
    """Count the number of analysis rounds in a log file."""
    return log_text.count("--- ROUND")


def extract_key_insights(log_text: str, max_insights: int = 5) -> List[str]:
    """Extract key insight sentences from a log file using simple heuristics."""
    key_phrases = [
        "key insight", "novel", "breakthrough", "finding", "result",
        "conjecture", "proven", "implies", "suggests", "demonstrates",
    ]
    sentences: List[str] = []
    for para in log_text.split("\n"):
        para = para.strip()
        if len(para) < 40 or len(para) > 300:
            continue
        if any(kp in para.lower() for kp in key_phrases):
            sentences.append(para)
    # Deduplicate and truncate
    seen: set[str] = set()
    unique: List[str] = []
    for s in sentences:
        key = s[:60].lower()
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique[:max_insights]


def analyze_all_logs() -> Dict[str, Any]:
    """Load and analyze all 7 Millennium Problem log files."""
    results: Dict[str, Any] = {}
    for name, path in _LOG_FILES.items():
        if not path.exists():
            results[name] = {"status": "log_missing"}
            continue
        text = path.read_text(encoding="utf-8")
        results[name] = {
            "status": "SOLVED" if name == "Poincare" else "Open",
            "log_size_bytes": path.stat().st_size,
            "total_rounds": count_rounds(text),
            "key_insights": extract_key_insights(text),
            "word_count": len(text.split()),
        }
    return results


# ---------------------------------------------------------------------------
# Quantum engine runner (optional; requires numpy)
# ---------------------------------------------------------------------------

def run_quantum_engine() -> Optional[Dict[str, Any]]:
    """Run the quantum lattice engine if available."""
    try:
        import quantum_lattice_engine as qle  # type: ignore[import]
        return qle.run_full_engine()
    except ImportError:
        # quantum_lattice_engine not importable as module from current path? Try direct exec
        try:
            engine_path = _REPO_ROOT / "quantum_lattice_engine.py"
            if not engine_path.exists():
                return {"error": "quantum_lattice_engine.py not found"}
            import importlib.util
            spec = importlib.util.spec_from_file_location("quantum_lattice_engine", engine_path)
            mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
            sys.modules["quantum_lattice_engine"] = mod
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
            return mod.run_full_engine()
        except Exception as exc:  # noqa: BLE001
            return {"error": f"Quantum engine unavailable: {exc}"}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


# ---------------------------------------------------------------------------
# Full orchestration
# ---------------------------------------------------------------------------

def run_full_analysis() -> Dict[str, Any]:
    """
    Run a complete analysis cycle:
    1. Analyze all 7 problem logs
    2. Load Kaggle integration findings
    3. Load deployment analytics
    4. Run quantum lattice engine
    5. Synthesize cross-platform insights
    6. Generate all report formats
    """
    start = time.time()
    ts = datetime.now(timezone.utc).isoformat()

    print(f"\n{'='*65}")
    print("BARROT APEX LATTICE — ENHANCED SANDBOX ORCHESTRATION SYSTEM")
    print(f"Timestamp: {ts}")
    print(f"{'='*65}")

    orchestration: Dict[str, Any] = {
        "session_id": ts,
        "mode": "full",
        "results": {},
    }

    # Phase 1: Log analysis
    print("\n[Phase 1/5] Analyzing Millennium Problem logs...")
    log_analysis = analyze_all_logs()
    orchestration["results"]["log_analysis"] = log_analysis
    for name, data in log_analysis.items():
        rounds = data.get("total_rounds", "N/A")
        insights = len(data.get("key_insights", []))
        print(f"  {name:<20} rounds={rounds:<4} insights={insights}")

    # Phase 2: Kaggle integration
    print("\n[Phase 2/5] Loading Kaggle competition findings...")
    kaggle_dir = _APEX / "kaggle_findings"
    export_kaggle_findings(kaggle_dir)
    synergies = identify_synergies()
    orchestration["results"]["kaggle"] = {
        "synergies_found": len(synergies),
        "top_synergy": synergies[0] if synergies else None,
    }
    print(f"  ✓ {len(synergies)} cross-problem synergies identified")
    print(f"  ✓ Top synergy: {synergies[0]['problem_a']} ↔ {synergies[0]['problem_b']}" if synergies else "")

    # Phase 3: Deployment analytics
    print("\n[Phase 3/5] Analyzing deployment metrics...")
    hf_analysis = analyze_hf_performance()
    db_analysis = analyze_databricks_performance()
    synthesis = synthesize_cross_platform_insights(hf_analysis, db_analysis)
    orchestration["results"]["deployment"] = {
        "hf_uptime": hf_analysis.get("deployment_health", {}).get("uptime_pct"),
        "hf_quality_score": hf_analysis.get("research_utilization", {}).get("weighted_quality_score"),
        "db_cost_savings_pct": db_analysis.get("cost_efficiency", {}).get("optimization_savings_pct"),
        "efficiency_score": synthesis.get("cost_summary", {}).get("combined_efficiency_score"),
    }
    eff = synthesis.get("cost_summary", {}).get("combined_efficiency_score", "N/A")
    print(f"  ✓ Combined efficiency score: {eff}")

    # Phase 4: Quantum engine
    print("\n[Phase 4/5] Running quantum lattice engine...")
    qe_results = run_quantum_engine()
    orchestration["results"]["quantum_engine"] = qe_results
    if qe_results and "error" not in qe_results:
        print(f"  ✓ Completed in {qe_results.get('elapsed_seconds', 'N/A')}s")
        # Save for report loader
        qe_out = _REPORTS_DIR / f"quantum_engine_results_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        qe_out.write_text(json.dumps(qe_results, indent=2, default=str), encoding="utf-8")
    else:
        print(f"  ⚠ Quantum engine: {qe_results.get('error', 'unknown error') if qe_results else 'no results'}")

    # Phase 5: Report generation
    print("\n[Phase 5/5] Generating comprehensive reports...")
    findings = load_all_findings()
    report_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    generated_reports: List[str] = []

    md_content = generate_markdown_report(findings)
    md_path = _REPORTS_DIR / f"findings_report_{report_timestamp}.md"
    md_path.write_text(md_content, encoding="utf-8")
    (_REPORTS_DIR / "unified_findings_report.md").write_text(md_content, encoding="utf-8")
    generated_reports.append(str(md_path))

    json_content = generate_json_report(findings)
    json_path = _REPORTS_DIR / f"findings_report_{report_timestamp}.json"
    json_path.write_text(json.dumps(json_content, indent=2), encoding="utf-8")
    generated_reports.append(str(json_path))

    html_content = generate_html_report(findings)
    html_path = _REPORTS_DIR / f"findings_report_{report_timestamp}.html"
    html_path.write_text(html_content, encoding="utf-8")
    generated_reports.append(str(html_path))

    orchestration["results"]["reports_generated"] = generated_reports
    print(f"  ✓ {len(generated_reports)} reports generated")

    elapsed = round(time.time() - start, 2)
    orchestration["elapsed_seconds"] = elapsed

    # Print summary
    print(f"\n{'='*65}")
    print("ORCHESTRATION COMPLETE")
    print(f"Total time: {elapsed}s")
    print(f"Problems analyzed: 7")
    print(f"Reports generated: {len(generated_reports)}")
    print(f"{'='*65}\n")

    return orchestration


def run_quick_report() -> None:
    """Generate reports without running the quantum engine."""
    print("Generating quick findings report...")
    findings = load_all_findings()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    for fmt, gen_fn, ext in [
        ("markdown", generate_markdown_report, "md"),
        ("json", generate_json_report, "json"),
        ("html", generate_html_report, "html"),
    ]:
        content = gen_fn(findings)
        if fmt == "json":
            content = json.dumps(content, indent=2)
        path = _REPORTS_DIR / f"findings_report_{ts}.{ext}"
        path.write_text(content, encoding="utf-8")
        print(f"  ✓ {fmt.upper()} report: {path}")

    print("\nQuick report generation complete.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Barrot Apex Lattice — Enhanced Sandbox Orchestration System"
    )
    parser.add_argument(
        "--mode",
        choices=["analyze", "report", "quantum", "full"],
        default="full",
        help=(
            "analyze: log analysis only | "
            "report: report generation only | "
            "quantum: quantum engine only | "
            "full: complete orchestration"
        ),
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory for orchestration results JSON",
    )
    args = parser.parse_args()

    if args.mode == "analyze":
        results = analyze_all_logs()
        print(json.dumps(results, indent=2, default=str))

    elif args.mode == "report":
        run_quick_report()

    elif args.mode == "quantum":
        qe_results = run_quantum_engine()
        if qe_results:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            out = _REPORTS_DIR / f"quantum_engine_results_{ts}.json"
            out.write_text(json.dumps(qe_results, indent=2, default=str), encoding="utf-8")
            print(f"Quantum engine results saved to: {out}")

    else:  # full
        orchestration = run_full_analysis()
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                json.dumps(orchestration, indent=2, default=str), encoding="utf-8"
            )
            print(f"Orchestration results saved to: {out_path}")


if __name__ == "__main__":
    main()
