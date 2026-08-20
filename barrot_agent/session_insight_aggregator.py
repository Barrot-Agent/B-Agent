#!/usr/bin/env python3
"""
Session Insight Aggregator for Barrot-Ω

This module aggregates insights from all GitHub agent sessions and performs
dynamic cross-analysis and synchronization across all knowledge domains.

Key Features:
- Aggregates insights from GitHub Copilot sessions
- Cross-references with existing knowledge bases
- Performs dynamic pattern recognition
- Continuously synchronizes sporadic domain data
- Extracts full scope insights from all outcomes
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .config import config
from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class SessionInsight:
    """Represents a single insight from a GitHub agent session."""

    session_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_type: str = "github_copilot"  # github_copilot, workflow, manual
    task_description: str = ""
    outcomes: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    domain_tags: List[str] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)
    cross_references: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class CrossAnalysisResult:
    """Result of cross-analysis across multiple sessions."""

    analysis_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    analyzed_sessions: int = 0
    patterns_discovered: List[Dict[str, Any]] = field(default_factory=list)
    domain_connections: Dict[str, List[str]] = field(default_factory=dict)
    synthesis: str = ""
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class SessionInsightDatabase:
    """SQLite database for storing and querying session insights."""

    def __init__(self, db_path: str | Path = "data/session_insights.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    session_type TEXT NOT NULL,
                    task_description TEXT,
                    confidence_score REAL,
                    metadata TEXT
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    insight TEXT NOT NULL,
                    domain_tag TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS outcomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cross_analysis (
                    analysis_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    analyzed_sessions INTEGER,
                    synthesis TEXT,
                    confidence REAL,
                    result TEXT
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS domain_connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain_a TEXT NOT NULL,
                    domain_b TEXT NOT NULL,
                    connection_strength REAL,
                    last_updated TEXT NOT NULL
                )
            """
            )
            # Create indexes for faster queries
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_insights_session ON insights(session_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_insights_domain ON insights(domain_tag)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_sessions_timestamp ON sessions(timestamp)"
            )
            conn.commit()
        logger.info("Session insight database initialized at %s", self.db_path)

    def store_session(self, insight: SessionInsight) -> None:
        """Store a session insight in the database."""
        with sqlite3.connect(self.db_path) as conn:
            # Store session
            conn.execute(
                """
                INSERT OR REPLACE INTO sessions 
                (session_id, timestamp, session_type, task_description, confidence_score, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    insight.session_id,
                    insight.timestamp,
                    insight.session_type,
                    insight.task_description,
                    insight.confidence_score,
                    json.dumps(insight.metadata),
                ),
            )

            # Store insights
            for idx, ins_text in enumerate(insight.insights):
                domain = insight.domain_tags[idx] if idx < len(insight.domain_tags) else ""
                conn.execute(
                    """
                    INSERT INTO insights (session_id, insight, domain_tag, timestamp)
                    VALUES (?, ?, ?, ?)
                """,
                    (insight.session_id, ins_text, domain, insight.timestamp),
                )

            # Store outcomes
            for outcome in insight.outcomes:
                conn.execute(
                    """
                    INSERT INTO outcomes (session_id, outcome, timestamp)
                    VALUES (?, ?, ?)
                """,
                    (insight.session_id, outcome, insight.timestamp),
                )

            conn.commit()
        logger.info("Stored session insight: %s", insight.session_id)

    def get_recent_sessions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent sessions."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM sessions 
                ORDER BY timestamp DESC 
                LIMIT ?
            """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_insights_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Retrieve all insights for a specific domain."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT i.*, s.task_description, s.session_type
                FROM insights i
                JOIN sessions s ON i.session_id = s.session_id
                WHERE i.domain_tag = ?
                ORDER BY i.timestamp DESC
            """,
                (domain,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def store_cross_analysis(self, result: CrossAnalysisResult) -> None:
        """Store cross-analysis results."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cross_analysis 
                (analysis_id, timestamp, analyzed_sessions, synthesis, confidence, result)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    result.analysis_id,
                    result.timestamp,
                    result.analyzed_sessions,
                    result.synthesis,
                    result.confidence,
                    json.dumps(result.to_dict()),
                ),
            )
            conn.commit()
        logger.info("Stored cross-analysis result: %s", result.analysis_id)


class SessionInsightAggregator:
    """
    Aggregates insights from all GitHub agent sessions and performs
    dynamic cross-analysis.
    """

    def __init__(
        self,
        db_path: str | Path = "data/session_insights.db",
        knowledge_base_dir: str | Path = "ping-pongings/knowledge-base",
    ):
        self.db = SessionInsightDatabase(db_path)
        self.kb_dir = Path(knowledge_base_dir)
        self.domains = self._discover_domains()
        logger.info(
            "SessionInsightAggregator initialized with %d domains", len(self.domains)
        )

    def _discover_domains(self) -> Set[str]:
        """Discover available knowledge domains from the knowledge base."""
        domains = set()
        if self.kb_dir.exists():
            for file in self.kb_dir.glob("*.jsonl"):
                # Extract domain from filename
                domain = file.stem.replace("_log", "").replace("_", " ")
                domains.add(domain)
        return domains

    def ingest_github_session(
        self,
        session_id: str,
        task: str,
        outcomes: List[str],
        insights: List[str],
        files_changed: List[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> SessionInsight:
        """
        Ingest a GitHub Copilot session and extract insights.

        Args:
            session_id: Unique identifier for the session
            task: Task description
            outcomes: List of outcomes from the session
            insights: List of insights extracted
            files_changed: List of files modified
            metadata: Additional metadata

        Returns:
            SessionInsight object
        """
        # Analyze task and outcomes to determine domain tags
        domain_tags = self._classify_domains(task, outcomes, insights)

        session = SessionInsight(
            session_id=session_id,
            session_type="github_copilot",
            task_description=task,
            outcomes=outcomes,
            insights=insights,
            domain_tags=domain_tags,
            related_files=files_changed or [],
            confidence_score=self._calculate_confidence(outcomes, insights),
            metadata=metadata or {},
        )

        self.db.store_session(session)
        logger.info("Ingested GitHub session: %s", session_id)
        return session

    def _classify_domains(
        self, task: str, outcomes: List[str], insights: List[str]
    ) -> List[str]:
        """Classify which domains are relevant to this session."""
        text = f"{task} {' '.join(outcomes)} {' '.join(insights)}".lower()
        relevant_domains = []

        # Domain keyword mapping
        domain_keywords = {
            "xrp": ["xrp", "ripple", "crypto", "liquidity"],
            "monetization": ["revenue", "monetization", "payment", "subscription"],
            "agi": ["agi", "intelligence", "reasoning", "cognitive"],
            "workflow": ["workflow", "automation", "github actions", "ci/cd"],
            "merge_conflict": ["merge", "conflict", "git", "resolution"],
            "millennium_problems": ["millennium", "mathematical", "theorem"],
            "character_capability": ["character", "capability", "persona"],
            "barrot_memory": ["memory", "learning", "feedback", "recursive"],
            "frontier": ["frontier", "research", "innovation"],
            "webmcp": ["webmcp", "web", "mcp", "sandbox"],
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in text for keyword in keywords):
                relevant_domains.append(domain)

        # Default to general if no specific domain found
        if not relevant_domains:
            relevant_domains.append("general")

        return relevant_domains

    def _calculate_confidence(self, outcomes: List[str], insights: List[str]) -> float:
        """Calculate confidence score based on outcomes and insights."""
        if not outcomes and not insights:
            return 0.0

        # More outcomes and insights = higher confidence
        outcome_score = min(len(outcomes) * 0.2, 0.5)
        insight_score = min(len(insights) * 0.15, 0.5)

        return min(outcome_score + insight_score, 1.0)

    def cross_analyze_sessions(
        self, session_window: int = 100, min_confidence: float = 0.3
    ) -> CrossAnalysisResult:
        """
        Perform cross-analysis across recent sessions to discover patterns
        and connections between domains.

        Args:
            session_window: Number of recent sessions to analyze
            min_confidence: Minimum confidence threshold for analysis

        Returns:
            CrossAnalysisResult with discovered patterns
        """
        sessions = self.db.get_recent_sessions(limit=session_window)

        # Filter by confidence
        sessions = [s for s in sessions if s.get("confidence_score", 0) >= min_confidence]

        if not sessions:
            return CrossAnalysisResult(
                analysis_id=f"cross_analysis_{datetime.now(timezone.utc).isoformat()}",
                analyzed_sessions=0,
                synthesis="No sessions available for analysis",
            )

        # Discover patterns
        patterns = self._discover_patterns(sessions)

        # Discover domain connections
        domain_connections = self._discover_domain_connections(sessions)

        # Generate synthesis
        synthesis = self._synthesize_insights(sessions, patterns, domain_connections)

        # Generate recommendations
        recommendations = self._generate_recommendations(patterns, domain_connections)

        result = CrossAnalysisResult(
            analysis_id=f"cross_analysis_{datetime.now(timezone.utc).isoformat()}",
            analyzed_sessions=len(sessions),
            patterns_discovered=patterns,
            domain_connections=domain_connections,
            synthesis=synthesis,
            recommendations=recommendations,
            confidence=self._calculate_analysis_confidence(sessions, patterns),
        )

        self.db.store_cross_analysis(result)
        logger.info(
            "Cross-analysis complete: %d sessions, %d patterns",
            len(sessions),
            len(patterns),
        )
        return result

    def _discover_patterns(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Discover patterns across sessions."""
        patterns = []

        # Pattern 1: Recurring task types
        task_freq = {}
        for session in sessions:
            task_type = self._extract_task_type(session.get("task_description", ""))
            task_freq[task_type] = task_freq.get(task_type, 0) + 1

        for task_type, count in task_freq.items():
            if count >= 3:  # Threshold for pattern
                patterns.append(
                    {
                        "pattern_type": "recurring_task",
                        "description": f"Recurring task type: {task_type}",
                        "frequency": count,
                        "confidence": min(count / len(sessions), 1.0),
                    }
                )

        # Pattern 2: Common domain combinations
        domain_combos = {}
        for session in sessions:
            metadata = json.loads(session.get("metadata", "{}"))
            domains = tuple(sorted(metadata.get("domains", [])))
            if len(domains) > 1:
                domain_combos[domains] = domain_combos.get(domains, 0) + 1

        for combo, count in domain_combos.items():
            if count >= 2:
                patterns.append(
                    {
                        "pattern_type": "domain_combination",
                        "description": f"Domains often combined: {', '.join(combo)}",
                        "frequency": count,
                        "confidence": min(count / len(sessions), 1.0),
                    }
                )

        return patterns

    def _extract_task_type(self, task_description: str) -> str:
        """Extract high-level task type from description."""
        task_lower = task_description.lower()

        if "fix" in task_lower or "bug" in task_lower:
            return "bug_fix"
        elif "add" in task_lower or "implement" in task_lower or "create" in task_lower:
            return "feature_addition"
        elif "refactor" in task_lower or "improve" in task_lower:
            return "refactoring"
        elif "test" in task_lower:
            return "testing"
        elif "doc" in task_lower or "documentation" in task_lower:
            return "documentation"
        else:
            return "general"

    def _discover_domain_connections(
        self, sessions: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Discover connections between different domains."""
        connections = {}

        for domain in self.domains:
            domain_insights = self.db.get_insights_by_domain(domain)
            connected = set()

            # Look for cross-references in insights
            for insight in domain_insights:
                for other_domain in self.domains:
                    if other_domain != domain and other_domain in insight.get("insight", "").lower():
                        connected.add(other_domain)

            if connected:
                connections[domain] = list(connected)

        return connections

    def _synthesize_insights(
        self,
        sessions: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]],
        connections: Dict[str, List[str]],
    ) -> str:
        """Generate a synthesis of insights across all sessions."""
        synthesis_parts = []

        synthesis_parts.append(f"Analyzed {len(sessions)} recent GitHub agent sessions.")

        if patterns:
            synthesis_parts.append(
                f"\nDiscovered {len(patterns)} behavioral patterns:"
            )
            for pattern in patterns[:5]:  # Top 5 patterns
                synthesis_parts.append(
                    f"- {pattern['description']} (confidence: {pattern['confidence']:.2f})"
                )

        if connections:
            synthesis_parts.append(f"\nIdentified {len(connections)} domain connections:")
            for domain, linked in list(connections.items())[:5]:
                synthesis_parts.append(f"- {domain} → {', '.join(linked)}")

        return "\n".join(synthesis_parts)

    def _generate_recommendations(
        self, patterns: List[Dict[str, Any]], connections: Dict[str, List[str]]
    ) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []

        # Recommend automation for recurring tasks
        recurring_tasks = [p for p in patterns if p["pattern_type"] == "recurring_task"]
        if recurring_tasks:
            recommendations.append(
                "Consider automating recurring tasks through GitHub Actions workflows"
            )

        # Recommend knowledge integration for connected domains
        if len(connections) >= 3:
            recommendations.append(
                "Develop cross-domain knowledge integration to leverage discovered connections"
            )

        # Recommend focused learning on frequent domains
        domain_freq = {}
        for domain, linked in connections.items():
            domain_freq[domain] = domain_freq.get(domain, 0) + len(linked)

        if domain_freq:
            top_domain = max(domain_freq.items(), key=lambda x: x[1])[0]
            recommendations.append(
                f"Prioritize deep learning in {top_domain} domain for maximum impact"
            )

        return recommendations

    def _calculate_analysis_confidence(
        self, sessions: List[Dict[str, Any]], patterns: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence in the cross-analysis."""
        if not sessions:
            return 0.0

        # Base confidence on number of sessions and patterns
        session_score = min(len(sessions) / 50, 0.5)  # Max 0.5 at 50+ sessions
        pattern_score = min(len(patterns) / 10, 0.5)  # Max 0.5 at 10+ patterns

        return min(session_score + pattern_score, 1.0)

    def synchronize_knowledge_bases(self) -> Dict[str, Any]:
        """
        Synchronize insights across all knowledge bases in the repository.
        This ensures all sporadic domain data is cross-referenced and connected.

        Returns:
            Summary of synchronization results
        """
        sync_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "domains_synchronized": 0,
            "insights_integrated": 0,
            "new_connections": 0,
        }

        # Scan all knowledge base files
        if not self.kb_dir.exists():
            logger.warning("Knowledge base directory not found: %s", self.kb_dir)
            return sync_results

        for jsonl_file in self.kb_dir.glob("*.jsonl"):
            domain = jsonl_file.stem.replace("_log", "")
            insights_count = self._integrate_knowledge_file(jsonl_file, domain)
            sync_results["insights_integrated"] += insights_count
            sync_results["domains_synchronized"] += 1

        # Perform cross-analysis after synchronization
        analysis = self.cross_analyze_sessions()
        sync_results["new_connections"] = len(analysis.domain_connections)

        logger.info(
            "Knowledge base synchronization complete: %d domains, %d insights",
            sync_results["domains_synchronized"],
            sync_results["insights_integrated"],
        )

        return sync_results

    def _integrate_knowledge_file(self, file_path: Path, domain: str) -> int:
        """Integrate insights from a knowledge base JSONL file."""
        insights_count = 0

        try:
            with open(file_path, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            # Extract insight from entry
                            insight_text = self._extract_insight_from_entry(entry, domain)
                            if insight_text:
                                # Create a synthetic session for this knowledge entry
                                session_id = f"{domain}_{entry.get('timestamp', 'unknown')}"
                                session = SessionInsight(
                                    session_id=session_id,
                                    session_type="knowledge_base",
                                    task_description=f"Knowledge integration from {domain}",
                                    outcomes=[],
                                    insights=[insight_text],
                                    domain_tags=[domain],
                                    confidence_score=0.7,
                                    metadata={"source_file": str(file_path), "domain": domain},
                                )
                                self.db.store_session(session)
                                insights_count += 1
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error("Error integrating knowledge file %s: %s", file_path, e)

        return insights_count

    def _extract_insight_from_entry(self, entry: Dict[str, Any], domain: str) -> Optional[str]:
        """Extract meaningful insight from a knowledge base entry."""
        # Different domains have different structures
        if domain == "barrot_memory":
            return entry.get("answer", entry.get("content", ""))
        elif domain == "frontier":
            return entry.get("summary", entry.get("title", ""))
        elif domain == "semantic_memory":
            return entry.get("content", entry.get("text", ""))
        elif "log" in domain:
            # Generic log entry
            return entry.get("summary", entry.get("message", entry.get("content", "")))
        else:
            # Try common fields
            return entry.get("summary", entry.get("description", entry.get("insight", "")))

    def generate_insight_report(self, output_file: str | Path = None) -> Dict[str, Any]:
        """
        Generate a comprehensive report of all aggregated insights.

        Args:
            output_file: Optional path to save the report

        Returns:
            Report dictionary
        """
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_sessions": 0,
            "total_insights": 0,
            "domains": {},
            "recent_analysis": {},
            "recommendations": [],
        }

        # Get session count
        sessions = self.db.get_recent_sessions(limit=1000)
        report["total_sessions"] = len(sessions)

        # Get insights per domain
        for domain in self.domains:
            insights = self.db.get_insights_by_domain(domain)
            report["domains"][domain] = {
                "insight_count": len(insights),
                "recent_insights": [i.get("insight", "") for i in insights[:5]],
            }
            report["total_insights"] += len(insights)

        # Get latest cross-analysis
        analysis = self.cross_analyze_sessions()
        report["recent_analysis"] = {
            "patterns": len(analysis.patterns_discovered),
            "connections": len(analysis.domain_connections),
            "synthesis": analysis.synthesis,
        }
        report["recommendations"] = analysis.recommendations

        # Save if output file provided
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)
            logger.info("Insight report saved to %s", output_path)

        return report


def main():
    """Main entry point for session insight aggregation."""
    aggregator = SessionInsightAggregator()

    # Synchronize all knowledge bases
    logger.info("Starting knowledge base synchronization...")
    sync_results = aggregator.synchronize_knowledge_bases()
    print(f"Synchronization complete: {json.dumps(sync_results, indent=2)}")

    # Perform cross-analysis
    logger.info("Performing cross-session analysis...")
    analysis = aggregator.cross_analyze_sessions()
    print(f"\nCross-Analysis Results:")
    print(f"Sessions analyzed: {analysis.analyzed_sessions}")
    print(f"Patterns discovered: {len(analysis.patterns_discovered)}")
    print(f"\nSynthesis:\n{analysis.synthesis}")
    print(f"\nRecommendations:")
    for rec in analysis.recommendations:
        print(f"- {rec}")

    # Generate comprehensive report
    logger.info("Generating insight report...")
    report = aggregator.generate_insight_report(
        "ping-pongings/knowledge-base/session_insight_report.json"
    )
    print(f"\nReport generated with {report['total_insights']} total insights")


if __name__ == "__main__":
    main()
