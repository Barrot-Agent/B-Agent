#!/usr/bin/env python3
"""
Example Usage: Millennium Problems Micro-Ingestion Data

Demonstrates how to work with the micro-ingested JSON data for various use cases:
- Pandas DataFrame analysis
- Search queries
- Priority-based filtering
- Taxonomy navigation
"""

import json
from typing import List, Dict, Any


def load_json(filename: str) -> Any:
    """Load JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def example_1_overview_analysis():
    """Example 1: Analyze problems overview with basic filtering"""
    print("=" * 80)
    print("EXAMPLE 1: Problems Overview Analysis")
    print("=" * 80)
    
    overview = load_json('millennium_problems_overview.json')
    
    print(f"\nTotal Problems: {len(overview)}")
    print("\n📊 Status Distribution:")
    open_problems = [p for p in overview if p['status'] == 'Open']
    solved_problems = [p for p in overview if 'SOLVED' in p['status']]
    print(f"  - Open: {len(open_problems)}")
    print(f"  - Solved: {len(solved_problems)}")
    
    print("\n🎯 AI Applicability Distribution:")
    for level in ['High', 'Medium', 'Low', 'N/A']:
        problems = [p for p in overview if level in p['ai_applicability']]
        if problems:
            print(f"  - {level}: {len(problems)}")
            for p in problems:
                print(f"    • {p['name']}")


def example_2_search_by_tag():
    """Example 2: Search problems by tag"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Search by Tag")
    print("=" * 80)
    
    summaries = load_json('millennium_problems_search_summaries.json')
    
    def find_by_tag(tag: str) -> List[tuple]:
        results = []
        for problem, data in summaries.items():
            if tag in data.get('search_tags', []):
                results.append((problem, data))
        return results
    
    # Search for cryptography-related problems
    print("\n🔍 Problems related to 'cryptography':")
    crypto = find_by_tag('cryptography')
    for name, data in crypto:
        print(f"  • {name.replace('_', ' ').title()}")
        print(f"    - AI Relevance: {data.get('ai_relevance', 'N/A')}")
        print(f"    - Tags: {', '.join(data.get('search_tags', []))}")
    
    # Search for optimization-related problems
    print("\n🔍 Problems related to 'optimization':")
    opt = find_by_tag('optimization')
    for name, data in opt:
        print(f"  • {name.replace('_', ' ').title()}")
        print(f"    - Impact: {data.get('impact', 'N/A')}")


def example_3_priority_based_filtering():
    """Example 3: Filter by strategic priority"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Priority-Based Resource Allocation")
    print("=" * 80)
    
    # Load complete ingestion to get priorities
    # Since we excluded timestamped files, we'll work with the static files
    taxonomy = load_json('millennium_problems_taxonomy.json')
    overview = load_json('millennium_problems_overview.json')
    
    print("\n🎯 High-Priority Problems (Focus First):")
    # Use AI applicability as proxy since priorities are in main file
    high_ai = [p for p in overview if p['ai_applicability'] == 'High']
    for p in high_ai:
        print(f"  • {p['name']}")
        print(f"    - Status: {p['status']}")
        print(f"    - Progress: {p['progress']}")


def example_4_domain_navigation():
    """Example 4: Navigate by mathematical domain"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Mathematical Domain Navigation")
    print("=" * 80)
    
    taxonomy = load_json('millennium_problems_taxonomy.json')
    
    print("\n📚 Problems by Mathematical Domain:")
    domains = taxonomy['by_mathematical_domain']
    for domain, problems in domains.items():
        if problems:
            print(f"\n  {domain.replace('_', ' ').title()}:")
            for p in problems:
                print(f"    • {p}")


def example_5_detailed_problem_access():
    """Example 5: Access detailed problem information"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Detailed Problem Information")
    print("=" * 80)
    
    # Load P vs NP details
    pvsnp = load_json('millennium_problem_1_p_vs_np_problem.json')
    
    print("\n🔬 P vs NP Problem - Detailed Analysis:")
    print(f"\nProblem Statement:")
    print(f"  {pvsnp['problem_statement']}")
    
    print(f"\nOfficial Status: {pvsnp['official_status']}")
    print(f"AI/ML Relevance: {pvsnp['ai_ml_relevance']}")
    
    print(f"\nWhy It Matters for AI ({len(pvsnp['why_matters_for_ai'])} reasons):")
    for i, reason in enumerate(pvsnp['why_matters_for_ai'], 1):
        print(f"  {i}. {reason}")
    
    print(f"\nBarrot's Approach ({len(pvsnp['barrot_approach'])} steps):")
    for i, step in enumerate(pvsnp['barrot_approach'], 1):
        print(f"  {i}. {step}")


def example_6_pandas_ready():
    """Example 6: Pandas DataFrame creation"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Pandas DataFrame Creation")
    print("=" * 80)
    
    overview = load_json('millennium_problems_overview.json')
    
    print("\n📊 Creating Pandas-Ready Structure:")
    print("```python")
    print("import pandas as pd")
    print("import json")
    print()
    print("with open('millennium_problems_overview.json', 'r') as f:")
    print("    data = json.load(f)")
    print()
    print("df = pd.DataFrame(data)")
    print("print(df[['name', 'status', 'ai_applicability']])")
    print()
    print("# Filter high AI applicability")
    print("high_ai = df[df['ai_applicability'] == 'High']")
    print("print(f'\\nHigh AI Applicability Problems: {len(high_ai)}')")
    print("```")
    
    print("\n📋 Data Preview (first 3 rows):")
    for i, problem in enumerate(overview[:3], 1):
        print(f"\n  Row {i}:")
        print(f"    Name: {problem['name']}")
        print(f"    Status: {problem['status']}")
        print(f"    AI Applicability: {problem['ai_applicability']}")
        print(f"    Progress: {problem['progress']}")


def example_7_batch_query():
    """Example 7: Batch query for ML pipeline"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Batch Query for ML Pipeline")
    print("=" * 80)
    
    # Load all problem detail files
    problem_files = [
        'millennium_problem_1_p_vs_np_problem.json',
        'millennium_problem_2_hodge_conjecture.json',
        'millennium_problem_3_riemann_hypothesis.json',
        'millennium_problem_4_yang-mills_existence_and_mass_gap.json',
        'millennium_problem_5_navier-stokes_existence_and_smoothness.json',
        'millennium_problem_6_birch_and_swinnerton-dyer_conjecture.json',
        'millennium_problem_7_poincaré_conjecture_✅.json'
    ]
    
    all_problems = []
    for f in problem_files:
        try:
            all_problems.append(load_json(f))
        except FileNotFoundError:
            pass
    
    print(f"\n🔄 Loaded {len(all_problems)} problem details")
    
    # Extract all "why it matters" reasons
    all_reasons = []
    for p in all_problems:
        all_reasons.extend(p['why_matters_for_ai'])
    
    print(f"\n💡 Total 'Why It Matters for AI' insights: {len(all_reasons)}")
    print("\nSample insights:")
    for reason in all_reasons[:5]:
        print(f"  • {reason}")
    
    # Count total action items
    total_actions = sum(len(p['next_steps']) for p in all_problems)
    print(f"\n📝 Total next action items across all problems: {total_actions}")


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("🧮 MILLENNIUM PROBLEMS MICRO-INGESTION")
    print("   Example Usage Demonstrations")
    print("=" * 80)
    
    try:
        example_1_overview_analysis()
        example_2_search_by_tag()
        example_3_priority_based_filtering()
        example_4_domain_navigation()
        example_5_detailed_problem_access()
        example_6_pandas_ready()
        example_7_batch_query()
        
        print("\n" + "=" * 80)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nThe micro-ingested data is ready for:")
        print("  • Database import (MongoDB, PostgreSQL, etc.)")
        print("  • Search engine indexing (Elasticsearch)")
        print("  • ML pipeline integration")
        print("  • Pandas DataFrame analysis")
        print("  • API generation")
        print("  • Knowledge graph construction")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you've run millennium_problems_micro_ingestion.py first!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
