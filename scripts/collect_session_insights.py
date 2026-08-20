#!/usr/bin/env python3
"""
Script to collect GitHub Copilot session insights and feed them into
the session insight aggregator.

This script can be called at the end of GitHub Copilot sessions to
automatically capture and store insights.
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from barrot_agent.logger import get_logger
from barrot_agent.session_insight_aggregator import SessionInsightAggregator

logger = get_logger(__name__)


def collect_from_git_history(repo_path: str = ".", limit: int = 10) -> None:
    """
    Collect insights from recent git commits.

    Args:
        repo_path: Path to git repository
        limit: Number of commits to analyze
    """
    import subprocess

    try:
        # Get recent commits
        result = subprocess.run(
            ["git", "log", f"-{limit}", "--pretty=format:%H|%s|%b", "--no-merges"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )

        aggregator = SessionInsightAggregator()

        for line in result.stdout.split("\n"):
            if not line.strip():
                continue

            parts = line.split("|", 2)
            if len(parts) < 2:
                continue

            commit_hash = parts[0]
            commit_msg = parts[1]
            commit_body = parts[2] if len(parts) > 2 else ""

            # Get files changed in this commit
            files_result = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            files_changed = [f.strip() for f in files_result.stdout.split("\n") if f.strip()]

            # Extract outcomes and insights from commit
            outcomes = [f"Modified {len(files_changed)} files"]
            insights = []

            if commit_body:
                # Parse insights from commit body
                for line in commit_body.split("\n"):
                    line = line.strip()
                    if line.startswith("- ") or line.startswith("* "):
                        insights.append(line[2:])

            # Ingest the session
            session = aggregator.ingest_github_session(
                session_id=f"git_{commit_hash[:8]}",
                task=commit_msg,
                outcomes=outcomes,
                insights=insights if insights else [commit_msg],
                files_changed=files_changed,
                metadata={
                    "commit_hash": commit_hash,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

            logger.info(
                "Collected session from commit %s: %s", commit_hash[:8], commit_msg
            )

        print(f"Successfully collected insights from {limit} recent commits")

    except subprocess.CalledProcessError as e:
        logger.error("Error collecting from git history: %s", e)
        print(f"Error: {e}")
        sys.exit(1)


def collect_manual_session(
    task: str,
    outcomes: List[str],
    insights: List[str],
    files: Optional[List[str]] = None,
) -> None:
    """
    Manually collect a session insight.

    Args:
        task: Task description
        outcomes: List of outcomes
        insights: List of insights
        files: Optional list of files changed
    """
    aggregator = SessionInsightAggregator()

    session_id = f"manual_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    session = aggregator.ingest_github_session(
        session_id=session_id,
        task=task,
        outcomes=outcomes,
        insights=insights,
        files_changed=files or [],
        metadata={"collected_at": datetime.now(timezone.utc).isoformat()},
    )

    print(f"Session collected: {session_id}")
    print(f"Task: {task}")
    print(f"Outcomes: {len(outcomes)}")
    print(f"Insights: {len(insights)}")
    print(f"Domains: {', '.join(session.domain_tags)}")


def run_full_aggregation() -> None:
    """Run full aggregation and analysis."""
    aggregator = SessionInsightAggregator()

    print("Starting full session insight aggregation...")

    # Synchronize knowledge bases
    print("\n1. Synchronizing knowledge bases...")
    sync_results = aggregator.synchronize_knowledge_bases()
    print(f"   - Domains synchronized: {sync_results['domains_synchronized']}")
    print(f"   - Insights integrated: {sync_results['insights_integrated']}")
    print(f"   - New connections: {sync_results['new_connections']}")

    # Perform cross-analysis
    print("\n2. Performing cross-session analysis...")
    analysis = aggregator.cross_analyze_sessions()
    print(f"   - Sessions analyzed: {analysis.analyzed_sessions}")
    print(f"   - Patterns discovered: {len(analysis.patterns_discovered)}")
    print(f"   - Domain connections: {len(analysis.domain_connections)}")

    # Generate report
    print("\n3. Generating comprehensive report...")
    report = aggregator.generate_insight_report(
        "ping-pongings/knowledge-base/session_insight_report.json"
    )
    print(f"   - Total sessions: {report['total_sessions']}")
    print(f"   - Total insights: {report['total_insights']}")

    print("\n=== SYNTHESIS ===")
    print(analysis.synthesis)

    if analysis.recommendations:
        print("\n=== RECOMMENDATIONS ===")
        for i, rec in enumerate(analysis.recommendations, 1):
            print(f"{i}. {rec}")

    print("\nAggregation complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Collect GitHub Copilot session insights for Barrot"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Git history collection
    git_parser = subparsers.add_parser("git", help="Collect from git commit history")
    git_parser.add_argument(
        "--limit", type=int, default=10, help="Number of commits to analyze"
    )
    git_parser.add_argument(
        "--repo", type=str, default=".", help="Path to git repository"
    )

    # Manual session collection
    manual_parser = subparsers.add_parser("manual", help="Manually collect a session")
    manual_parser.add_argument("--task", required=True, help="Task description")
    manual_parser.add_argument(
        "--outcomes", nargs="+", required=True, help="List of outcomes"
    )
    manual_parser.add_argument(
        "--insights", nargs="+", required=True, help="List of insights"
    )
    manual_parser.add_argument("--files", nargs="*", help="List of files changed")

    # Full aggregation
    subparsers.add_parser("aggregate", help="Run full aggregation and analysis")

    args = parser.parse_args()

    if args.command == "git":
        collect_from_git_history(args.repo, args.limit)
    elif args.command == "manual":
        collect_manual_session(args.task, args.outcomes, args.insights, args.files)
    elif args.command == "aggregate":
        run_full_aggregation()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
