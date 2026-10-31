#!/usr/bin/env python3
"""
Example: Recursive Feedback Loop with Kimi 3

This example demonstrates how to run Barrot's recursive feedback loop
using Kimi 3 for paradigm-shifting insights and continuous self-improvement.

Setup:
    1. Set environment variable: KIMI__API_KEY=your_kimi_api_key
    2. Set environment variable: KIMI__ENABLED=true
    3. Run: python examples/example_recursive_feedback.py

The loop will:
    - Analyze current system state
    - Generate paradigm-shifting insights via Kimi 3
    - Absorb and apply feedback recursively
    - Refine infrastructure dynamically
    - Continue until convergence or max iterations
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from barrot_agent import RecursiveFeedbackLoop
from barrot_agent.config import FeedbackLoopConfig, KimiConfig
from barrot_agent.kimi_integration import KimiClient


def main():
    """Run the recursive feedback loop example."""
    print("=" * 70)
    print("BARROT-Ω RECURSIVE FEEDBACK LOOP")
    print("Kimi 3 Integration for Paradigm-Shifting Self-Improvement")
    print("=" * 70)
    print()

    # Check if Kimi is configured
    kimi_config = KimiConfig()
    if not kimi_config.api_key:
        print("⚠️  Kimi API key not configured!")
        print("   Set KIMI__API_KEY environment variable to enable Kimi 3 integration.")
        print("   Continuing with placeholder feedback...")
        print()
    else:
        print("✓ Kimi 3 integration configured")
        print(f"  Model: {kimi_config.model_name}")
        print(f"  API Base: {kimi_config.api_base}")
        print()

    # Configure feedback loop
    loop_config = FeedbackLoopConfig(
        max_iterations=int(os.getenv("MAX_ITERATIONS", "50")),
        convergence_threshold=float(os.getenv("CONVERGENCE_THRESHOLD", "0.90")),
        improvement_window=5,
        enable_auto_refinement=True,
        refinement_interval=10,
    )

    print("Feedback Loop Configuration:")
    print(f"  Max Iterations: {loop_config.max_iterations}")
    print(f"  Convergence Threshold: {loop_config.convergence_threshold}")
    print(f"  Improvement Window: {loop_config.improvement_window}")
    print(f"  Auto Refinement: {loop_config.enable_auto_refinement}")
    print(f"  Refinement Interval: {loop_config.refinement_interval}")
    print()

    # Define improvement goals
    improvement_goals = [
        "Maximize infrastructure coverage and capability",
        "Discover paradigm-shifting architectural improvements",
        "Accelerate convergence through meta-optimizations",
        "Optimize resource utilization and efficiency",
        "Enhance recursive self-improvement mechanisms",
        "Identify and fill critical infrastructure gaps",
        "Improve feedback quality and insight diversity",
        "Strengthen cross-domain pattern recognition",
    ]

    print("Improvement Goals:")
    for i, goal in enumerate(improvement_goals, 1):
        print(f"  {i}. {goal}")
    print()

    # Create and run feedback loop
    try:
        loop = RecursiveFeedbackLoop(
            loop_config=loop_config,
            kimi_client=KimiClient(kimi_config),
            output_dir="feedback_loops",
        )

        print("Starting recursive feedback loop...")
        print("=" * 70)
        print()

        report = loop.run(improvement_goals=improvement_goals)

        print()
        print("=" * 70)
        print("FEEDBACK LOOP RESULTS")
        print("=" * 70)
        print(f"Total Iterations: {report.total_iterations}")
        print(f"Converged: {'Yes' if report.converged else 'No'}")
        print(f"Final Convergence: {report.final_convergence:.3f}")
        print(f"Total Improvements: {report.total_improvements}")
        print(f"Paradigm Shifts Discovered: {report.paradigm_shifts_discovered}")
        print(f"Infrastructure Refinements: {report.infrastructure_refinements}")
        print()

        print("Recent Iterations:")
        for iteration in report.iterations[-5:]:
            print(f"  Iteration {iteration.iteration}:")
            print(f"    Score: {iteration.improvement_score:.3f}")
            print(f"    Convergence: {iteration.convergence_metric:.3f}")
            print(f"    Insights: {len(iteration.absorbed_insights)}")
            print(f"    Improvements: {len(iteration.applied_improvements)}")
            print()

        print("Report saved to feedback_loops/ directory")

    except KeyboardInterrupt:
        print()
        print("⚠️  Loop interrupted by user")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
