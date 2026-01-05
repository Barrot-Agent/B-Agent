#!/usr/bin/env python3
"""
Example Usage of Dependency Micro-Ingestion System

Demonstrates how to use the dependency micro-ingestion system
to enhance Barrot's knowledge and generate optimizations.
"""

import json
import os
from datetime import datetime
from dependency_micro_ingestion import (
    DependencyMicroIngestion,
    PackageCategory,
    OptimizationLevel,
)


def example_full_ingestion():
    """Example: Full ingestion of all configured dependencies"""
    print("=" * 70)
    print("Example 1: Full Ingestion of All Dependencies")
    print("=" * 70)
    
    # Initialize the ingestion system
    ingestion_system = DependencyMicroIngestion(
        config_file="dependency-ingestion-config.yaml",
        output_dir="ingested_dependencies"
    )
    
    # Run full ingestion
    summary = ingestion_system.ingest_all()
    
    # Display summary
    print("\n📊 Ingestion Summary:")
    print(f"   Total packages: {summary['total_packages']}")
    print(f"   Successful: {summary['successful_ingestions']}")
    print(f"   Failed: {summary['failed_ingestions']}")
    print(f"   Duration: {summary['duration_seconds']:.2f}s")
    print(f"   Optimizations generated: {summary['optimizations_generated']}")
    
    return summary


def example_analyze_single_package():
    """Example: Analyze a single package in detail"""
    print("\n" + "=" * 70)
    print("Example 2: Analyze Single Package (PyTorch)")
    print("=" * 70)
    
    # Check if PyTorch knowledge file exists
    pytorch_file = "ingested_dependencies/dependency_pytorch.json"
    
    if not os.path.exists(pytorch_file):
        print("⚠️  PyTorch knowledge file not found. Run full ingestion first.")
        return None
    
    # Load PyTorch knowledge
    with open(pytorch_file, 'r', encoding='utf-8') as f:
        pytorch_knowledge = json.load(f)
    
    # Display metadata
    print("\n📦 PyTorch Metadata:")
    print(f"   Name: {pytorch_knowledge['metadata']['name']}")
    print(f"   Category: {pytorch_knowledge['metadata']['category']}")
    print(f"   Description: {pytorch_knowledge['metadata']['description']}")
    
    # Display key features
    print(f"\n✨ Key Features ({len(pytorch_knowledge['metadata']['key_features'])}):")
    for feature in pytorch_knowledge['metadata']['key_features'][:3]:
        print(f"   • {feature}")
    
    # Display architecture components
    print(f"\n🏗️  Architecture Components ({len(pytorch_knowledge['architecture'])}):")
    for component in pytorch_knowledge['architecture'][:2]:
        print(f"   • {component['name']}: {component['purpose']}")
        print(f"     Key classes: {', '.join(component['key_classes'][:3])}")
    
    # Display API endpoints
    print(f"\n🔌 API Endpoints ({len(pytorch_knowledge['api_endpoints'])}):")
    for api in pytorch_knowledge['api_endpoints'][:2]:
        print(f"   • {api['name']}")
        print(f"     Signature: {api['signature']}")
    
    # Display best practices
    print(f"\n✅ Best Practices ({len(pytorch_knowledge['best_practices'])}):")
    for practice in pytorch_knowledge['best_practices'][:3]:
        print(f"   • {practice}")
    
    return pytorch_knowledge


def example_view_optimizations():
    """Example: View optimization recommendations for Barrot"""
    print("\n" + "=" * 70)
    print("Example 3: View Optimization Recommendations")
    print("=" * 70)
    
    # Check if optimizations file exists
    opt_file = "ingested_dependencies/barrot_optimization_recommendations.json"
    
    if not os.path.exists(opt_file):
        print("⚠️  Optimizations file not found. Run full ingestion first.")
        return None
    
    # Load optimizations
    with open(opt_file, 'r', encoding='utf-8') as f:
        optimizations = json.load(f)
    
    # Display summary
    print("\n📊 Optimization Summary:")
    print(f"   Generated at: {optimizations['generated_at']}")
    print(f"   Total recommendations: {optimizations['total_recommendations']}")
    
    # Display by level
    print("\n🎯 By Priority Level:")
    for level, count in optimizations['by_level'].items():
        print(f"   {level}: {count}")
    
    # Display by category
    print("\n🏷️  By Category:")
    for category, count in optimizations['by_category'].items():
        print(f"   {category}: {count}")
    
    # Display top recommendations
    print("\n⭐ Top Recommendations:")
    for i, rec in enumerate(optimizations['recommendations'][:3], 1):
        print(f"\n{i}. {rec['title']} ({rec['level'].upper()})")
        print(f"   Package: {rec['package']}")
        print(f"   Category: {rec['category']}")
        print(f"   Impact: {rec['impact']}")
        print(f"   Description: {rec['description'][:100]}...")
        
        if rec['implementation_notes']:
            print(f"   Implementation notes:")
            for note in rec['implementation_notes'][:2]:
                print(f"     • {note}")
    
    return optimizations


def example_view_taxonomy():
    """Example: View dependency taxonomy"""
    print("\n" + "=" * 70)
    print("Example 4: View Dependency Taxonomy")
    print("=" * 70)
    
    # Check if taxonomy file exists
    taxonomy_file = "ingested_dependencies/dependency_taxonomy.json"
    
    if not os.path.exists(taxonomy_file):
        print("⚠️  Taxonomy file not found. Run full ingestion first.")
        return None
    
    # Load taxonomy
    with open(taxonomy_file, 'r', encoding='utf-8') as f:
        taxonomy = json.load(f)
    
    # Display by category
    print("\n📚 By Category:")
    for category, packages in taxonomy['by_category'].items():
        print(f"\n   {category.upper()}:")
        for pkg in packages:
            print(f"     • {pkg}")
    
    # Display by priority
    print("\n⚡ By Priority:")
    for priority, packages in taxonomy['by_priority'].items():
        print(f"\n   {priority.upper()}: {len(packages)} packages")
        print(f"     {', '.join(packages[:5])}")
        if len(packages) > 5:
            print(f"     ... and {len(packages) - 5} more")
    
    # Display by use case
    print("\n🎯 By Use Case:")
    for use_case, packages in taxonomy['by_use_case'].items():
        print(f"\n   {use_case.replace('_', ' ').title()}:")
        for pkg in packages:
            print(f"     • {pkg}")
    
    return taxonomy


def example_compare_frameworks():
    """Example: Compare ML frameworks (PyTorch vs TensorFlow)"""
    print("\n" + "=" * 70)
    print("Example 5: Compare ML Frameworks")
    print("=" * 70)
    
    frameworks = ['pytorch', 'tensorflow']
    comparison = {}
    
    for framework in frameworks:
        framework_file = f"ingested_dependencies/dependency_{framework}.json"
        
        if not os.path.exists(framework_file):
            print(f"⚠️  {framework} knowledge file not found.")
            continue
        
        with open(framework_file, 'r', encoding='utf-8') as f:
            comparison[framework] = json.load(f)
    
    if len(comparison) < 2:
        print("⚠️  Not enough frameworks for comparison. Run full ingestion first.")
        return None
    
    # Compare key features
    print("\n🔍 Feature Comparison:")
    print(f"\n{'Framework':<15} {'Features':<10} {'APIs':<10} {'Best Practices':<15}")
    print("-" * 50)
    
    for name, data in comparison.items():
        features = len(data['metadata']['key_features'])
        apis = len(data['api_endpoints'])
        practices = len(data['best_practices'])
        print(f"{name:<15} {features:<10} {apis:<10} {practices:<15}")
    
    # Compare categories
    print("\n📊 Unique Features:")
    for name, data in comparison.items():
        print(f"\n{name.upper()}:")
        for feature in data['metadata']['key_features'][:3]:
            print(f"   • {feature}")
    
    # Compare use cases
    print("\n🎯 Use Cases:")
    for name, data in comparison.items():
        print(f"\n{name.upper()}:")
        for use_case in data['metadata']['use_cases'][:3]:
            print(f"   • {use_case}")
    
    return comparison


def example_integration_analysis():
    """Example: Analyze integration opportunities with Barrot"""
    print("\n" + "=" * 70)
    print("Example 6: Integration Analysis with Barrot Systems")
    print("=" * 70)
    
    # Find packages with integration notes
    ingestion_dir = "ingested_dependencies"
    
    if not os.path.exists(ingestion_dir):
        print("⚠️  Ingested dependencies directory not found. Run full ingestion first.")
        return None
    
    integrations = {}
    
    for filename in os.listdir(ingestion_dir):
        if filename.startswith('dependency_') and filename.endswith('.json'):
            filepath = os.path.join(ingestion_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if data.get('integration_notes'):
                package_name = data['metadata']['name']
                integrations[package_name] = data['integration_notes']
    
    # Display integration opportunities
    print(f"\n🔗 Integration Opportunities ({len(integrations)} packages):")
    
    for package, notes in integrations.items():
        print(f"\n{package.upper()}:")
        for note in notes:
            print(f"   • {note}")
    
    return integrations


def example_performance_analysis():
    """Example: Analyze performance optimization opportunities"""
    print("\n" + "=" * 70)
    print("Example 7: Performance Optimization Analysis")
    print("=" * 70)
    
    ingestion_dir = "ingested_dependencies"
    
    if not os.path.exists(ingestion_dir):
        print("⚠️  Ingested dependencies directory not found. Run full ingestion first.")
        return None
    
    performance_tips = {}
    
    for filename in os.listdir(ingestion_dir):
        if filename.startswith('dependency_') and filename.endswith('.json'):
            filepath = os.path.join(ingestion_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if data.get('performance_tips'):
                package_name = data['metadata']['name']
                performance_tips[package_name] = data['performance_tips']
    
    # Display performance tips
    print(f"\n⚡ Performance Tips ({len(performance_tips)} packages):")
    
    for package, tips in performance_tips.items():
        print(f"\n{package.upper()}:")
        for tip in tips[:3]:
            print(f"   • {tip}")
    
    return performance_tips


def main():
    """Run all examples"""
    print("\n")
    print("🦜" * 35)
    print("     Barrot Dependency Micro-Ingestion System Examples")
    print("🦜" * 35)
    print("\n")
    
    # Run examples in sequence
    examples = [
        ("Full Ingestion", example_full_ingestion),
        ("Single Package Analysis", example_analyze_single_package),
        ("Optimization Recommendations", example_view_optimizations),
        ("Dependency Taxonomy", example_view_taxonomy),
        ("Framework Comparison", example_compare_frameworks),
        ("Integration Analysis", example_integration_analysis),
        ("Performance Analysis", example_performance_analysis),
    ]
    
    results = {}
    
    for name, example_func in examples:
        try:
            result = example_func()
            results[name] = result
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            results[name] = None
    
    # Final summary
    print("\n" + "=" * 70)
    print("🎉 Examples Completed!")
    print("=" * 70)
    
    successful = sum(1 for r in results.values() if r is not None)
    print(f"\n✅ Successful examples: {successful}/{len(examples)}")
    
    print("\n📂 Output files in 'ingested_dependencies/' directory:")
    if os.path.exists("ingested_dependencies"):
        for filename in sorted(os.listdir("ingested_dependencies"))[:10]:
            print(f"   • {filename}")
    
    print("\n💡 Next steps:")
    print("   1. Review individual dependency JSON files")
    print("   2. Implement optimization recommendations")
    print("   3. Integrate patterns with Barrot systems")
    print("   4. Schedule weekly re-ingestion for updates")


if __name__ == '__main__':
    main()
