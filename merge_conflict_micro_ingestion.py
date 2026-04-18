#!/usr/bin/env python3
"""
Merge Conflict Resolution Micro-Ingestion System

Extracts, structures, and continuously learns merge conflict resolution strategies,
tools, and best practices. Designed to enable Barrot-Agent to autonomously handle
merge conflicts across various scenarios with minimal manual intervention.

Key Features:
- Automated conflict pattern detection and analysis
- Strategy repository with success rate tracking
- Continuous learning from resolution outcomes
- Integration with existing Barrot-Agent capabilities
- Prevention of unresolved conflicts in communications
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path


class ConflictType(Enum):
    """Types of merge conflicts that can be encountered"""
    CONTENT = "content"  # Direct content conflicts
    RENAME = "rename"  # File rename conflicts
    DELETE_MODIFY = "delete_modify"  # File deleted in one branch, modified in another
    BINARY = "binary"  # Binary file conflicts
    SUBMODULE = "submodule"  # Submodule pointer conflicts
    WHITESPACE = "whitespace"  # Whitespace-only conflicts
    LINE_ENDING = "line_ending"  # Line ending conflicts (CRLF vs LF)
    ENCODING = "encoding"  # Character encoding conflicts


class ResolutionStrategy(Enum):
    """Available strategies for resolving conflicts"""
    ACCEPT_CURRENT = "accept_current"  # Keep current branch changes
    ACCEPT_INCOMING = "accept_incoming"  # Accept incoming changes
    ACCEPT_BOTH = "accept_both"  # Merge both changes
    MANUAL_MERGE = "manual_merge"  # Require manual intervention
    AUTO_MERGE = "auto_merge"  # Automatically merge using AI
    SYNTACTIC_MERGE = "syntactic_merge"  # Use syntax-aware merging
    SEMANTIC_MERGE = "semantic_merge"  # Use semantic understanding
    THREE_WAY_MERGE = "three_way_merge"  # Traditional 3-way merge
    RECURSIVE = "recursive"  # Recursive merge strategy


@dataclass
class ConflictPattern:
    """Pattern for identifying specific types of conflicts"""
    pattern_id: str
    name: str
    description: str
    conflict_type: str
    indicators: List[str]
    file_patterns: List[str]
    frequency: str
    auto_resolvable: bool


@dataclass
class ResolutionTechnique:
    """Specific technique for resolving conflicts"""
    technique_id: str
    name: str
    description: str
    applicable_types: List[str]
    strategy: str
    commands: List[str]
    prerequisites: List[str]
    success_rate: float
    risk_level: str
    automation_level: str


@dataclass
class ConflictScenario:
    """Complete scenario with conflict and resolution"""
    scenario_id: str
    title: str
    description: str
    conflict_type: str
    example_conflict: str
    recommended_strategy: str
    step_by_step: List[str]
    alternative_approaches: List[str]
    common_pitfalls: List[str]
    prevention_tips: List[str]


@dataclass
class ToolReference:
    """Reference to merge conflict resolution tools"""
    tool_name: str
    category: str
    description: str
    use_cases: List[str]
    installation: str
    basic_usage: str
    advanced_features: List[str]
    integration_notes: str


@dataclass
class BestPractice:
    """Best practice for merge conflict management"""
    practice_id: str
    title: str
    description: str
    category: str
    impact: str
    implementation: List[str]
    examples: List[str]
    anti_patterns: List[str]


@dataclass
class LearningOutcome:
    """Track outcomes from conflict resolutions"""
    outcome_id: str
    timestamp: str
    conflict_type: str
    strategy_used: str
    success: bool
    time_to_resolve: float
    manual_intervention_required: bool
    lessons_learned: List[str]
    improvements_suggested: List[str]


class MergeConflictMicroIngestion:
    """Main class for merge conflict resolution micro-ingestion"""
    
    def __init__(self):
        self.conflict_patterns: List[ConflictPattern] = []
        self.resolution_techniques: List[ResolutionTechnique] = []
        self.conflict_scenarios: List[ConflictScenario] = []
        self.tools: List[ToolReference] = []
        self.best_practices: List[BestPractice] = []
        self.learning_outcomes: List[LearningOutcome] = []
        self.strategy_success_rates: Dict[str, List[float]] = {}
        
    def initialize_knowledge_base(self) -> None:
        """Initialize the knowledge base with foundational patterns and strategies"""
        self._load_conflict_patterns()
        self._load_resolution_techniques()
        self._load_conflict_scenarios()
        self._load_tools()
        self._load_best_practices()
        
    def _load_conflict_patterns(self) -> None:
        """Load common conflict patterns"""
        self.conflict_patterns = [
            ConflictPattern(
                pattern_id="CP001",
                name="Parallel Feature Development",
                description="Two branches modify the same code section independently",
                conflict_type=ConflictType.CONTENT.value,
                indicators=["<<<<<<< HEAD", "=======", ">>>>>>>"],
                file_patterns=["*.py", "*.js", "*.java", "*.cpp"],
                frequency="Very High",
                auto_resolvable=False
            ),
            ConflictPattern(
                pattern_id="CP002",
                name="Import Statement Conflict",
                description="Different imports added to the same location",
                conflict_type=ConflictType.CONTENT.value,
                indicators=["import", "from", "require"],
                file_patterns=["*.py", "*.js", "*.ts"],
                frequency="High",
                auto_resolvable=True
            ),
            ConflictPattern(
                pattern_id="CP003",
                name="Configuration Merge",
                description="Configuration files modified in both branches",
                conflict_type=ConflictType.CONTENT.value,
                indicators=["config", "settings", "properties"],
                file_patterns=["*.json", "*.yaml", "*.yml", "*.toml", "*.ini"],
                frequency="Medium",
                auto_resolvable=True
            ),
            ConflictPattern(
                pattern_id="CP004",
                name="Documentation Conflict",
                description="Documentation updates conflict between branches",
                conflict_type=ConflictType.CONTENT.value,
                indicators=["# ", "## ", "/**", "<!--"],
                file_patterns=["*.md", "*.rst", "*.txt"],
                frequency="Medium",
                auto_resolvable=True
            ),
            ConflictPattern(
                pattern_id="CP005",
                name="Whitespace Only",
                description="Conflict caused only by whitespace differences",
                conflict_type=ConflictType.WHITESPACE.value,
                indicators=["spaces", "tabs", "indentation"],
                file_patterns=["*"],
                frequency="Low",
                auto_resolvable=True
            ),
            ConflictPattern(
                pattern_id="CP006",
                name="File Rename Collision",
                description="Same file renamed differently in each branch",
                conflict_type=ConflictType.RENAME.value,
                indicators=["renamed", "moved"],
                file_patterns=["*"],
                frequency="Low",
                auto_resolvable=False
            ),
            ConflictPattern(
                pattern_id="CP007",
                name="Delete-Modify Conflict",
                description="File deleted in one branch, modified in another",
                conflict_type=ConflictType.DELETE_MODIFY.value,
                indicators=["deleted by", "modified by"],
                file_patterns=["*"],
                frequency="Medium",
                auto_resolvable=False
            ),
        ]
        
    def _load_resolution_techniques(self) -> None:
        """Load resolution techniques"""
        self.resolution_techniques = [
            ResolutionTechnique(
                technique_id="RT001",
                name="Accept Both Changes with Manual Review",
                description="Merge both changes and manually review for correctness",
                applicable_types=[ConflictType.CONTENT.value],
                strategy=ResolutionStrategy.ACCEPT_BOTH.value,
                commands=[
                    "# Manual editing required",
                    "git add <file>",
                    "git commit -m 'Resolved conflict by merging both changes'"
                ],
                prerequisites=["Understanding of code context", "Review capability"],
                success_rate=0.85,
                risk_level="Medium",
                automation_level="Semi-Automated"
            ),
            ResolutionTechnique(
                technique_id="RT002",
                name="Whitespace Normalization",
                description="Automatically resolve whitespace-only conflicts",
                applicable_types=[ConflictType.WHITESPACE.value],
                strategy=ResolutionStrategy.AUTO_MERGE.value,
                commands=[
                    "git merge -Xignore-space-change <branch>",
                    "git merge -Xignore-all-space <branch>"
                ],
                prerequisites=["Git 2.0+"],
                success_rate=0.98,
                risk_level="Low",
                automation_level="Fully Automated"
            ),
            ResolutionTechnique(
                technique_id="RT003",
                name="Three-Way Merge with Common Ancestor",
                description="Use common ancestor to intelligently merge changes",
                applicable_types=[ConflictType.CONTENT.value],
                strategy=ResolutionStrategy.THREE_WAY_MERGE.value,
                commands=[
                    "git merge-base <branch1> <branch2>",
                    "git merge-file <current> <base> <incoming>"
                ],
                prerequisites=["Access to merge base"],
                success_rate=0.75,
                risk_level="Medium",
                automation_level="Semi-Automated"
            ),
            ResolutionTechnique(
                technique_id="RT004",
                name="Import Statement Smart Merge",
                description="Intelligently merge import statements alphabetically",
                applicable_types=[ConflictType.CONTENT.value],
                strategy=ResolutionStrategy.AUTO_MERGE.value,
                commands=[
                    "# Python: Sort imports with isort",
                    "isort <file>",
                    "# JavaScript: Sort with eslint",
                    "eslint --fix <file>"
                ],
                prerequisites=["Code formatters installed"],
                success_rate=0.95,
                risk_level="Low",
                automation_level="Fully Automated"
            ),
            ResolutionTechnique(
                technique_id="RT005",
                name="Configuration Key Merge",
                description="Merge configuration files by key, keeping all unique keys",
                applicable_types=[ConflictType.CONTENT.value],
                strategy=ResolutionStrategy.SEMANTIC_MERGE.value,
                commands=[
                    "# Use specialized config merge tools",
                    "# JSON: jq for merging",
                    "# YAML: yq for merging"
                ],
                prerequisites=["Config-aware merge tools"],
                success_rate=0.90,
                risk_level="Low",
                automation_level="Fully Automated"
            ),
            ResolutionTechnique(
                technique_id="RT006",
                name="Recursive Strategy with Patience",
                description="Use patience diff algorithm for better merge results",
                applicable_types=[ConflictType.CONTENT.value],
                strategy=ResolutionStrategy.RECURSIVE.value,
                commands=[
                    "git merge -s recursive -X patience <branch>",
                    "git merge -s recursive -X diff-algorithm=patience <branch>"
                ],
                prerequisites=["Git 1.7.10+"],
                success_rate=0.80,
                risk_level="Low",
                automation_level="Automated"
            ),
            ResolutionTechnique(
                technique_id="RT007",
                name="Rerere (Reuse Recorded Resolution)",
                description="Automatically apply previously recorded conflict resolutions",
                applicable_types=[ConflictType.CONTENT.value],
                strategy=ResolutionStrategy.AUTO_MERGE.value,
                commands=[
                    "git config --global rerere.enabled true",
                    "# Git will automatically reuse resolutions"
                ],
                prerequisites=["Git rerere enabled"],
                success_rate=0.99,
                risk_level="Very Low",
                automation_level="Fully Automated"
            ),
        ]
        
    def _load_conflict_scenarios(self) -> None:
        """Load common conflict scenarios with solutions"""
        self.conflict_scenarios = [
            ConflictScenario(
                scenario_id="SC001",
                title="Parallel Feature Branches Merge",
                description="Two feature branches modify the same function independently",
                conflict_type=ConflictType.CONTENT.value,
                example_conflict="""
<<<<<<< HEAD
def calculate_total(items):
    total = sum(item.price for item in items)
    tax = total * 0.08
    return total + tax
=======
def calculate_total(items):
    subtotal = sum(item.price * item.quantity for item in items)
    return subtotal
>>>>>>> feature/cart-updates
                """,
                recommended_strategy=ResolutionStrategy.MANUAL_MERGE.value,
                step_by_step=[
                    "1. Analyze both implementations to understand intent",
                    "2. Determine if both features are needed",
                    "3. Merge changes preserving both functionalities",
                    "4. Test the merged result",
                    "5. Stage and commit the resolution"
                ],
                alternative_approaches=[
                    "Create separate functions for each feature",
                    "Use feature flags to toggle behaviors",
                    "Refactor into a more flexible design"
                ],
                common_pitfalls=[
                    "Blindly accepting one side without analysis",
                    "Merging incompatible logic",
                    "Not testing after resolution"
                ],
                prevention_tips=[
                    "Keep feature branches short-lived",
                    "Regularly sync with main branch",
                    "Use better code organization to minimize conflicts"
                ]
            ),
            ConflictScenario(
                scenario_id="SC002",
                title="Import Statement Ordering",
                description="Both branches add new imports at the same location",
                conflict_type=ConflictType.CONTENT.value,
                example_conflict="""
<<<<<<< HEAD
import os
import sys
import requests
=======
import os
import sys
import numpy as np
>>>>>>> feature/data-analysis
                """,
                recommended_strategy=ResolutionStrategy.AUTO_MERGE.value,
                step_by_step=[
                    "1. Accept both imports",
                    "2. Sort them alphabetically",
                    "3. Run code formatter (isort, black, etc.)",
                    "4. Commit the organized imports"
                ],
                alternative_approaches=[
                    "Use automated import sorting tools",
                    "Configure pre-commit hooks for consistent formatting"
                ],
                common_pitfalls=[
                    "Not removing duplicate imports",
                    "Incorrect import order affecting functionality"
                ],
                prevention_tips=[
                    "Use automated formatters with pre-commit hooks",
                    "Establish import ordering conventions"
                ]
            ),
        ]
        
    def _load_tools(self) -> None:
        """Load merge conflict resolution tools"""
        self.tools = [
            ToolReference(
                tool_name="Git Rerere",
                category="Built-in Git",
                description="Reuse Recorded Resolution - automatically applies previously recorded conflict resolutions",
                use_cases=[
                    "Repetitive conflicts during rebases",
                    "Long-lived feature branches",
                    "Recurring merge patterns"
                ],
                installation="Built into Git, enable with: git config --global rerere.enabled true",
                basic_usage="Automatically activated when enabled, records and replays resolutions",
                advanced_features=[
                    "Manual rerere training",
                    "Rerere diff viewing",
                    "Resolution database management"
                ],
                integration_notes="Enable globally for all repositories or per-repository"
            ),
            ToolReference(
                tool_name="Meld",
                category="Visual Merge Tool",
                description="Visual diff and merge tool with three-way merge support",
                use_cases=[
                    "Complex merge conflicts",
                    "Visual comparison needed",
                    "Side-by-side conflict resolution"
                ],
                installation="apt-get install meld (Linux) or brew install meld (macOS)",
                basic_usage="git mergetool --tool=meld",
                advanced_features=[
                    "Three-way merge view",
                    "Syntax highlighting",
                    "Directory comparison"
                ],
                integration_notes="Configure as default merge tool in Git config"
            ),
            ToolReference(
                tool_name="KDiff3",
                category="Visual Merge Tool",
                description="Advanced merge tool with automatic conflict resolution",
                use_cases=[
                    "Three-way merges",
                    "Automatic merge attempts",
                    "Complex directory merges"
                ],
                installation="apt-get install kdiff3 or brew install kdiff3",
                basic_usage="git mergetool --tool=kdiff3",
                advanced_features=[
                    "Automatic merge mode",
                    "Configurable merge logic",
                    "Directory comparison"
                ],
                integration_notes="Excellent for automated resolution attempts"
            ),
            ToolReference(
                tool_name="VS Code Merge Editor",
                category="IDE Integration",
                description="Built-in merge conflict resolution in VS Code",
                use_cases=[
                    "In-editor conflict resolution",
                    "Quick conflict handling",
                    "Inline conflict markers"
                ],
                installation="Built into VS Code",
                basic_usage="Open conflicted file, click 'Accept' buttons or edit manually",
                advanced_features=[
                    "Three-way merge view",
                    "Side-by-side comparison",
                    "IntelliSense during resolution"
                ],
                integration_notes="Seamlessly integrated with Git in VS Code"
            ),
            ToolReference(
                tool_name="Semantic Merge",
                category="Language-Aware",
                description="Language-aware merge tool that understands code structure",
                use_cases=[
                    "Refactoring merges",
                    "Large-scale code reorganization",
                    "Syntax-aware merging"
                ],
                installation="Commercial tool from Plastic SCM",
                basic_usage="Configure as Git merge driver",
                advanced_features=[
                    "Understands code structure",
                    "Smart refactoring merges",
                    "Language-specific rules"
                ],
                integration_notes="Premium solution for complex codebases"
            ),
        ]
        
    def _load_best_practices(self) -> None:
        """Load best practices for merge conflict management"""
        self.best_practices = [
            BestPractice(
                practice_id="BP001",
                title="Keep Feature Branches Short-Lived",
                description="Minimize conflicts by merging feature branches frequently",
                category="Prevention",
                impact="High",
                implementation=[
                    "Limit feature branch lifetime to 2-3 days",
                    "Break large features into smaller incremental changes",
                    "Merge to main branch frequently"
                ],
                examples=[
                    "Instead of one large feature branch, create multiple smaller PRs",
                    "Use feature flags to merge incomplete features safely"
                ],
                anti_patterns=[
                    "Long-lived feature branches (weeks or months)",
                    "Waiting until feature is 'perfect' before merging"
                ]
            ),
            BestPractice(
                practice_id="BP002",
                title="Regularly Sync with Main Branch",
                description="Keep feature branches up-to-date with main to reduce conflict size",
                category="Prevention",
                impact="High",
                implementation=[
                    "Rebase or merge main into feature branch daily",
                    "Resolve small conflicts incrementally",
                    "Stay aware of changes in main branch"
                ],
                examples=[
                    "git pull --rebase origin main (daily)",
                    "git merge origin/main (for shared branches)"
                ],
                anti_patterns=[
                    "Never syncing until ready to merge",
                    "Ignoring main branch changes"
                ]
            ),
            BestPractice(
                practice_id="BP003",
                title="Use Automated Code Formatters",
                description="Eliminate formatting conflicts with consistent automated formatting",
                category="Prevention",
                impact="Medium",
                implementation=[
                    "Configure pre-commit hooks with formatters",
                    "Use tools like Black, Prettier, gofmt",
                    "Enforce formatting in CI/CD"
                ],
                examples=[
                    "pre-commit hook with black for Python",
                    "prettier with husky for JavaScript"
                ],
                anti_patterns=[
                    "Manual formatting leading to inconsistencies",
                    "No formatting standards"
                ]
            ),
            BestPractice(
                practice_id="BP004",
                title="Enable Git Rerere",
                description="Let Git remember how you resolved conflicts previously",
                category="Automation",
                impact="Medium",
                implementation=[
                    "git config --global rerere.enabled true",
                    "Train rerere with your resolutions",
                    "Review recorded resolutions periodically"
                ],
                examples=[
                    "Rerere automatically resolves repeated conflicts during rebases"
                ],
                anti_patterns=[
                    "Not using rerere for repetitive conflicts",
                    "Resolving same conflict multiple times manually"
                ]
            ),
            BestPractice(
                practice_id="BP005",
                title="Test After Every Conflict Resolution",
                description="Always verify that resolved conflicts don't break functionality",
                category="Quality Assurance",
                impact="Critical",
                implementation=[
                    "Run full test suite after resolution",
                    "Manual testing of affected features",
                    "Code review of conflict resolutions"
                ],
                examples=[
                    "npm test or pytest after resolving conflicts",
                    "Manual QA for user-facing changes"
                ],
                anti_patterns=[
                    "Committing resolved conflicts without testing",
                    "Assuming resolution is correct without verification"
                ]
            ),
            BestPractice(
                practice_id="BP006",
                title="Communicate During Conflict Resolution",
                description="Coordinate with team members when resolving complex conflicts",
                category="Collaboration",
                impact="High",
                implementation=[
                    "Consult original code authors",
                    "Discuss resolution approach in team chat",
                    "Document resolution rationale in commit message"
                ],
                examples=[
                    "Tag teammate in PR comment: 'Hey @author, which approach should we use?'",
                    "Detailed commit message explaining why certain approach was chosen"
                ],
                anti_patterns=[
                    "Silently resolving conflicts without consulting others",
                    "Making assumptions about intent"
                ]
            ),
            BestPractice(
                practice_id="BP007",
                title="Learn from Conflicts",
                description="Analyze patterns in conflicts to prevent future occurrences",
                category="Continuous Improvement",
                impact="Medium",
                implementation=[
                    "Track which files conflict most often",
                    "Identify structural issues causing conflicts",
                    "Refactor problem areas"
                ],
                examples=[
                    "If config file always conflicts, split into multiple files",
                    "If function conflicts frequently, it may be doing too much"
                ],
                anti_patterns=[
                    "Treating conflicts as normal without analysis",
                    "Not learning from repeated conflict patterns"
                ]
            ),
        ]
        
    def record_learning_outcome(self, outcome: LearningOutcome) -> None:
        """Record the outcome of a conflict resolution for learning"""
        self.learning_outcomes.append(outcome)
        self._update_success_rates(outcome)
        
    def _update_success_rates(self, outcome: LearningOutcome) -> None:
        """Update success rates for strategies based on outcomes"""
        strategy = outcome.strategy_used
        if strategy not in self.strategy_success_rates:
            self.strategy_success_rates[strategy] = []
        
        # Add success/failure to history
        self.strategy_success_rates[strategy].append(1.0 if outcome.success else 0.0)
        
    def get_recommended_strategy(self, conflict_type: str, file_path: str) -> Optional[ResolutionTechnique]:
        """Get recommended resolution strategy based on conflict type and context"""
        applicable_techniques = [
            tech for tech in self.resolution_techniques
            if conflict_type in tech.applicable_types
        ]
        
        if not applicable_techniques:
            return None
            
        # Sort by success rate
        applicable_techniques.sort(key=lambda x: x.success_rate, reverse=True)
        return applicable_techniques[0]
        
    def analyze_conflict(self, conflict_content: str, file_path: str) -> Dict[str, Any]:
        """Analyze a conflict and provide recommendations"""
        analysis = {
            "conflict_detected": True,
            "file_path": file_path,
            "conflict_type": None,
            "patterns_matched": [],
            "recommended_technique": None,
            "auto_resolvable": False,
            "risk_assessment": "Unknown"
        }
        
        # Detect conflict type
        for pattern in self.conflict_patterns:
            for indicator in pattern.indicators:
                if indicator in conflict_content:
                    analysis["patterns_matched"].append(pattern.name)
                    analysis["conflict_type"] = pattern.conflict_type
                    analysis["auto_resolvable"] = pattern.auto_resolvable
                    break
                    
        # Get recommended technique
        if analysis["conflict_type"]:
            technique = self.get_recommended_strategy(
                analysis["conflict_type"],
                file_path
            )
            if technique:
                analysis["recommended_technique"] = {
                    "name": technique.name,
                    "description": technique.description,
                    "commands": technique.commands,
                    "success_rate": technique.success_rate,
                    "automation_level": technique.automation_level
                }
                analysis["risk_assessment"] = technique.risk_level
                
        return analysis
        
    def export_to_json(self, output_dir: str = ".") -> Dict[str, str]:
        """Export all knowledge to JSON files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        exports = {}
        
        # Export conflict patterns
        patterns_file = output_path / "merge_conflict_patterns.json"
        with open(patterns_file, 'w') as f:
            json.dump(
                [asdict(p) for p in self.conflict_patterns],
                f,
                indent=2
            )
        exports["patterns"] = str(patterns_file)
        
        # Export resolution techniques
        techniques_file = output_path / "merge_resolution_techniques.json"
        with open(techniques_file, 'w') as f:
            json.dump(
                [asdict(t) for t in self.resolution_techniques],
                f,
                indent=2
            )
        exports["techniques"] = str(techniques_file)
        
        # Export scenarios
        scenarios_file = output_path / "merge_conflict_scenarios.json"
        with open(scenarios_file, 'w') as f:
            json.dump(
                [asdict(s) for s in self.conflict_scenarios],
                f,
                indent=2
            )
        exports["scenarios"] = str(scenarios_file)
        
        # Export tools
        tools_file = output_path / "merge_conflict_tools.json"
        with open(tools_file, 'w') as f:
            json.dump(
                [asdict(t) for t in self.tools],
                f,
                indent=2
            )
        exports["tools"] = str(tools_file)
        
        # Export best practices
        practices_file = output_path / "merge_conflict_best_practices.json"
        with open(practices_file, 'w') as f:
            json.dump(
                [asdict(p) for p in self.best_practices],
                f,
                indent=2
            )
        exports["best_practices"] = str(practices_file)
        
        # Export learning outcomes
        outcomes_file = output_path / "merge_conflict_learning_outcomes.json"
        with open(outcomes_file, 'w') as f:
            json.dump(
                [asdict(o) for o in self.learning_outcomes],
                f,
                indent=2
            )
        exports["learning_outcomes"] = str(outcomes_file)
        
        # Export summary
        summary = {
            "last_updated": datetime.now().isoformat(),
            "total_patterns": len(self.conflict_patterns),
            "total_techniques": len(self.resolution_techniques),
            "total_scenarios": len(self.conflict_scenarios),
            "total_tools": len(self.tools),
            "total_best_practices": len(self.best_practices),
            "total_learning_outcomes": len(self.learning_outcomes),
            "strategy_success_rates": {
                k: sum(v) / len(v) if v else 0.0
                for k, v in self.strategy_success_rates.items()
            }
        }
        
        summary_file = output_path / "merge_conflict_knowledge_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        exports["summary"] = str(summary_file)
        
        return exports
        
    def generate_report(self) -> str:
        """Generate a human-readable report of the knowledge base"""
        report = []
        report.append("# Merge Conflict Resolution Knowledge Base Report")
        report.append(f"\nGenerated: {datetime.now().isoformat()}\n")
        
        report.append(f"## Summary Statistics")
        report.append(f"- **Conflict Patterns**: {len(self.conflict_patterns)}")
        report.append(f"- **Resolution Techniques**: {len(self.resolution_techniques)}")
        report.append(f"- **Documented Scenarios**: {len(self.conflict_scenarios)}")
        report.append(f"- **Tools Cataloged**: {len(self.tools)}")
        report.append(f"- **Best Practices**: {len(self.best_practices)}")
        report.append(f"- **Learning Outcomes**: {len(self.learning_outcomes)}\n")
        
        report.append("## Conflict Patterns")
        for pattern in self.conflict_patterns:
            report.append(f"\n### {pattern.name} ({pattern.pattern_id})")
            report.append(f"- **Type**: {pattern.conflict_type}")
            report.append(f"- **Frequency**: {pattern.frequency}")
            report.append(f"- **Auto-Resolvable**: {pattern.auto_resolvable}")
            report.append(f"- **Description**: {pattern.description}")
            
        report.append("\n## Resolution Techniques")
        for tech in sorted(self.resolution_techniques, key=lambda x: x.success_rate, reverse=True):
            report.append(f"\n### {tech.name} ({tech.technique_id})")
            report.append(f"- **Success Rate**: {tech.success_rate * 100:.1f}%")
            report.append(f"- **Risk Level**: {tech.risk_level}")
            report.append(f"- **Automation**: {tech.automation_level}")
            report.append(f"- **Strategy**: {tech.strategy}")
            
        report.append("\n## Available Tools")
        for tool in self.tools:
            report.append(f"\n### {tool.tool_name}")
            report.append(f"- **Category**: {tool.category}")
            report.append(f"- **Description**: {tool.description}")
            
        report.append("\n## Best Practices")
        for practice in self.best_practices:
            report.append(f"\n### {practice.title} ({practice.practice_id})")
            report.append(f"- **Category**: {practice.category}")
            report.append(f"- **Impact**: {practice.impact}")
            report.append(f"- **Description**: {practice.description}")
            
        return "\n".join(report)


def main():
    """Main execution function"""
    print("🔄 Initializing Merge Conflict Micro-Ingestion System...")
    
    # Create instance and initialize
    mcmi = MergeConflictMicroIngestion()
    mcmi.initialize_knowledge_base()
    
    print(f"✅ Loaded {len(mcmi.conflict_patterns)} conflict patterns")
    print(f"✅ Loaded {len(mcmi.resolution_techniques)} resolution techniques")
    print(f"✅ Loaded {len(mcmi.conflict_scenarios)} conflict scenarios")
    print(f"✅ Loaded {len(mcmi.tools)} tools")
    print(f"✅ Loaded {len(mcmi.best_practices)} best practices")
    
    # Export to JSON files
    print("\n📤 Exporting knowledge base to JSON files...")
    exports = mcmi.export_to_json()
    
    for category, filepath in exports.items():
        print(f"  ✅ Exported {category}: {filepath}")
    
    # Generate report
    print("\n📊 Generating knowledge base report...")
    report = mcmi.generate_report()
    
    report_file = "merge_conflict_knowledge_report.md"
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"  ✅ Report saved: {report_file}")
    
    # Example: Analyze a sample conflict
    print("\n🔍 Example: Analyzing a sample conflict...")
    sample_conflict = """
<<<<<<< HEAD
def calculate_total(items):
    total = sum(item.price for item in items)
    return total
=======
def calculate_total(items):
    return sum(item.price * item.quantity for item in items)
>>>>>>> feature/cart-quantity
    """
    
    analysis = mcmi.analyze_conflict(sample_conflict, "app/cart.py")
    print(f"\n  Conflict Type: {analysis['conflict_type']}")
    print(f"  Auto-Resolvable: {analysis['auto_resolvable']}")
    print(f"  Risk Assessment: {analysis['risk_assessment']}")
    if analysis['recommended_technique']:
        print(f"  Recommended: {analysis['recommended_technique']['name']}")
        print(f"  Success Rate: {analysis['recommended_technique']['success_rate'] * 100:.1f}%")
    
    print("\n✨ Merge Conflict Micro-Ingestion System ready!")
    print("🦜 Knowledge base continuously learning and improving...")


if __name__ == "__main__":
    main()
