#!/usr/bin/env python3
"""
Example Usage: Merge Conflict Micro-Ingestion System

Demonstrates how to use the merge conflict resolution system to:
1. Initialize the knowledge base
2. Analyze conflicts
3. Get recommendations
4. Record learning outcomes
5. Export knowledge to JSON
"""

from merge_conflict_micro_ingestion import (
    MergeConflictMicroIngestion,
    LearningOutcome,
    ConflictType,
    ResolutionStrategy
)
from datetime import datetime


def example_basic_usage():
    """Example 1: Basic usage - Initialize and export"""
    print("=" * 70)
    print("Example 1: Basic Usage - Initialize and Export Knowledge Base")
    print("=" * 70)
    
    # Initialize the system
    mcmi = MergeConflictMicroIngestion()
    mcmi.initialize_knowledge_base()
    
    print(f"\n✅ Knowledge Base Initialized:")
    print(f"   - {len(mcmi.conflict_patterns)} Conflict Patterns")
    print(f"   - {len(mcmi.resolution_techniques)} Resolution Techniques")
    print(f"   - {len(mcmi.conflict_scenarios)} Scenarios")
    print(f"   - {len(mcmi.tools)} Tools")
    print(f"   - {len(mcmi.best_practices)} Best Practices")
    
    # Export to JSON
    exports = mcmi.export_to_json()
    print(f"\n📤 Exported {len(exports)} JSON files")
    
    return mcmi


def example_conflict_analysis():
    """Example 2: Analyze different types of conflicts"""
    print("\n" + "=" * 70)
    print("Example 2: Conflict Analysis")
    print("=" * 70)
    
    mcmi = MergeConflictMicroIngestion()
    mcmi.initialize_knowledge_base()
    
    # Example conflicts
    conflicts = [
        {
            "name": "Code Conflict",
            "file": "src/calculator.py",
            "content": """
<<<<<<< HEAD
def calculate(a, b):
    return a + b
=======
def calculate(a, b):
    return a * b
>>>>>>> feature/multiply
            """
        },
        {
            "name": "Import Conflict",
            "file": "src/main.py",
            "content": """
<<<<<<< HEAD
import os
import sys
import requests
=======
import os
import sys
import numpy as np
>>>>>>> feature/analysis
            """
        },
        {
            "name": "Config Conflict",
            "file": "config.yaml",
            "content": """
<<<<<<< HEAD
database:
  host: localhost
  port: 5432
=======
database:
  host: db.example.com
  port: 5432
>>>>>>> feature/cloud-db
            """
        }
    ]
    
    for conflict in conflicts:
        print(f"\n🔍 Analyzing: {conflict['name']} in {conflict['file']}")
        analysis = mcmi.analyze_conflict(conflict['content'], conflict['file'])
        
        print(f"   Conflict Type: {analysis['conflict_type']}")
        print(f"   Auto-Resolvable: {analysis['auto_resolvable']}")
        print(f"   Risk Level: {analysis['risk_assessment']}")
        
        if analysis['recommended_technique']:
            tech = analysis['recommended_technique']
            print(f"   Recommended: {tech['name']}")
            print(f"   Success Rate: {tech['success_rate'] * 100:.1f}%")
            print(f"   Automation: {tech['automation_level']}")


def example_get_recommendations():
    """Example 3: Get recommendations for specific conflict types"""
    print("\n" + "=" * 70)
    print("Example 3: Get Recommendations by Conflict Type")
    print("=" * 70)
    
    mcmi = MergeConflictMicroIngestion()
    mcmi.initialize_knowledge_base()
    
    conflict_types = [
        ConflictType.CONTENT.value,
        ConflictType.WHITESPACE.value,
        ConflictType.RENAME.value
    ]
    
    for conflict_type in conflict_types:
        print(f"\n📋 Recommendations for {conflict_type.upper()} conflicts:")
        technique = mcmi.get_recommended_strategy(conflict_type, "example.py")
        
        if technique:
            print(f"   Technique: {technique.name}")
            print(f"   Description: {technique.description}")
            print(f"   Success Rate: {technique.success_rate * 100:.1f}%")
            print(f"   Risk: {technique.risk_level}")
            print(f"   Commands:")
            for cmd in technique.commands[:2]:  # Show first 2 commands
                print(f"     - {cmd}")


def example_record_learning():
    """Example 4: Record learning outcomes from conflict resolutions"""
    print("\n" + "=" * 70)
    print("Example 4: Record Learning Outcomes")
    print("=" * 70)
    
    mcmi = MergeConflictMicroIngestion()
    mcmi.initialize_knowledge_base()
    
    # Simulate resolving several conflicts
    outcomes = [
        LearningOutcome(
            outcome_id="LO001",
            timestamp=datetime.now().isoformat(),
            conflict_type=ConflictType.CONTENT.value,
            strategy_used=ResolutionStrategy.AUTO_MERGE.value,
            success=True,
            time_to_resolve=45.0,
            manual_intervention_required=False,
            lessons_learned=[
                "Import conflicts can be safely auto-merged",
                "Sorting imports prevents future conflicts"
            ],
            improvements_suggested=[
                "Add pre-commit hook for import sorting"
            ]
        ),
        LearningOutcome(
            outcome_id="LO002",
            timestamp=datetime.now().isoformat(),
            conflict_type=ConflictType.CONTENT.value,
            strategy_used=ResolutionStrategy.MANUAL_MERGE.value,
            success=True,
            time_to_resolve=300.0,
            manual_intervention_required=True,
            lessons_learned=[
                "Complex logic conflicts require understanding both implementations",
                "Testing is critical after manual merge"
            ],
            improvements_suggested=[
                "Better code organization to minimize overlapping changes",
                "More frequent syncing with main branch"
            ]
        ),
        LearningOutcome(
            outcome_id="LO003",
            timestamp=datetime.now().isoformat(),
            conflict_type=ConflictType.WHITESPACE.value,
            strategy_used=ResolutionStrategy.AUTO_MERGE.value,
            success=True,
            time_to_resolve=5.0,
            manual_intervention_required=False,
            lessons_learned=[
                "Whitespace conflicts trivially resolved with ignore flags"
            ],
            improvements_suggested=[
                "Enforce consistent formatting with pre-commit hooks"
            ]
        )
    ]
    
    for outcome in outcomes:
        mcmi.record_learning_outcome(outcome)
        print(f"\n✅ Recorded: {outcome.outcome_id}")
        print(f"   Type: {outcome.conflict_type}")
        print(f"   Strategy: {outcome.strategy_used}")
        print(f"   Success: {outcome.success}")
        print(f"   Time: {outcome.time_to_resolve:.1f}s")
        print(f"   Manual Required: {outcome.manual_intervention_required}")
    
    print(f"\n📊 Total outcomes recorded: {len(mcmi.learning_outcomes)}")
    
    # Show success rates
    print("\n📈 Strategy Success Rates:")
    for strategy, outcomes in mcmi.strategy_success_rates.items():
        if outcomes:
            success_rate = sum(outcomes) / len(outcomes)
            print(f"   {strategy}: {success_rate * 100:.1f}% (n={len(outcomes)})")


def example_best_practices_review():
    """Example 5: Review best practices"""
    print("\n" + "=" * 70)
    print("Example 5: Review Best Practices")
    print("=" * 70)
    
    mcmi = MergeConflictMicroIngestion()
    mcmi.initialize_knowledge_base()
    
    categories = {}
    for practice in mcmi.best_practices:
        if practice.category not in categories:
            categories[practice.category] = []
        categories[practice.category].append(practice)
    
    for category, practices in categories.items():
        print(f"\n📚 {category.upper()} Practices:")
        for practice in practices:
            print(f"\n   {practice.title}")
            print(f"   Impact: {practice.impact}")
            print(f"   {practice.description}")


def example_tools_catalog():
    """Example 6: Browse available tools"""
    print("\n" + "=" * 70)
    print("Example 6: Available Tools Catalog")
    print("=" * 70)
    
    mcmi = MergeConflictMicroIngestion()
    mcmi.initialize_knowledge_base()
    
    categories = {}
    for tool in mcmi.tools:
        if tool.category not in categories:
            categories[tool.category] = []
        categories[tool.category].append(tool)
    
    for category, tools in categories.items():
        print(f"\n🔧 {category}:")
        for tool in tools:
            print(f"\n   {tool.tool_name}")
            print(f"   {tool.description}")
            print(f"   Use cases: {', '.join(tool.use_cases[:2])}")


def example_continuous_improvement():
    """Example 7: Demonstrate continuous improvement loop"""
    print("\n" + "=" * 70)
    print("Example 7: Continuous Improvement Loop")
    print("=" * 70)
    
    mcmi = MergeConflictMicroIngestion()
    mcmi.initialize_knowledge_base()
    
    print("\n🔄 Continuous Improvement Process:")
    print("\n1. Detect Conflict")
    print("   ↓")
    print("2. Analyze Pattern")
    print("   ↓")
    print("3. Get Recommendation")
    print("   ↓")
    print("4. Apply Strategy")
    print("   ↓")
    print("5. Record Outcome")
    print("   ↓")
    print("6. Update Success Rates")
    print("   ↓")
    print("7. Improve Future Recommendations")
    print("   ↓")
    print("8. Prevent Future Conflicts")
    
    print("\n💡 System Features:")
    features = [
        "Automated conflict pattern detection",
        "Strategy success rate tracking",
        "Continuous learning from outcomes",
        "Best practice recommendations",
        "Tool integration guidance",
        "Risk assessment for each resolution",
        "Automated vs manual decision making",
        "Prevention-focused insights"
    ]
    
    for feature in features:
        print(f"   ✓ {feature}")
    
    print("\n🎯 Integration with Barrot-Agent:")
    integrations = [
        "Automatically detects conflicts in GitHub PRs",
        "Applies learned strategies without manual intervention",
        "Prevents unresolved conflicts from appearing in communications",
        "Continuously improves resolution accuracy",
        "Tracks metrics for system performance",
        "Exports knowledge for version control",
        "Provides transparency in resolution decisions"
    ]
    
    for integration in integrations:
        print(f"   ✓ {integration}")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("🦜 MERGE CONFLICT MICRO-INGESTION SYSTEM")
    print("    Comprehensive Examples and Usage Patterns")
    print("=" * 70)
    
    # Run examples
    example_basic_usage()
    example_conflict_analysis()
    example_get_recommendations()
    example_record_learning()
    example_best_practices_review()
    example_tools_catalog()
    example_continuous_improvement()
    
    print("\n" + "=" * 70)
    print("✨ Examples Complete!")
    print("=" * 70)
    print("\n📖 For more information, see:")
    print("   - merge_conflict_micro_ingestion.py (main module)")
    print("   - merge_conflict_knowledge_report.md (generated report)")
    print("   - *.json files (exported knowledge base)")
    print("\n🦜 Barrot-Agent: Continuously learning to resolve conflicts! ✨")


if __name__ == "__main__":
    main()
