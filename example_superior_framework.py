#!/usr/bin/env python3
"""
Example demonstration of the Superior Framework
Showcases integration of Ping Ponging, UPATSTAR, and MMI
"""

import json
from datetime import datetime, timezone

# Import Superior Framework components
from superior_framework import (
    superior_framework,
    process_superior,
    check_integration,
    get_framework_status
)


def example_1_basic_processing():
    """Example 1: Basic Superior Framework Processing"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Superior Framework Processing")
    print("="*60 + "\n")
    
    result = process_superior(
        task="Optimize data processing pipeline for maximum efficiency",
        data={
            "current_metrics": {
                "latency": 500,
                "throughput": 100,
                "error_rate": 0.05
            },
            "target_metrics": {
                "latency": 100,
                "throughput": 500,
                "error_rate": 0.01
            },
            "constraints": ["budget_limited", "time_critical"]
        },
        enable_pingpong=False
    )
    
    print(f"Task: {result['task']}")
    print(f"Operation ID: {result['framework_operation_id']}")
    print(f"Components Used: {', '.join(result['components_used'])}")
    print(f"\nVantage Points Analyzed: {len(result['vantage_analysis']['vantage_points_analyzed'])}")
    print(f"Selected UPATSTAR Strategy: {result['upatstar_processing']['selected_strategy']}")
    
    if 'mmi_integration' in result:
        print(f"MMI Ingestion ID: {result['mmi_integration']['ingestion_id']}")
        print(f"Modalities Processed: {', '.join(result['mmi_integration']['modalities_processed'])}")
    
    print(f"\nProcessing Time: {result['superior_framework_metadata']['processing_time_seconds']:.4f}s")
    print(f"Integration Quality: {result['superior_framework_metadata']['components_integrated']} components")


def example_2_mmi_self_ingestion():
    """Example 2: MMI Self-Ingestion with Ping Ponging"""
    print("\n" + "="*60)
    print("EXAMPLE 2: MMI Self-Ingestion with Ping Ponging")
    print("="*60 + "\n")
    
    result = superior_framework.trigger_mmi_self_ingestion(recursion_depth=3)
    
    print(f"Operation: {result['operation']}")
    print(f"Ping Pong Emitted: {result['pingpong_emitted']}")
    print(f"Recursion Depth: {result['mmi_result']['recursion_depth']}")
    print(f"Cognitive Layers: {', '.join(result['mmi_result']['cognitive_layers'])}")
    print(f"Status: {result['mmi_result']['status']}")
    print(f"Glyph: {result['mmi_result']['glyph']}")


def example_3_integration_check():
    """Example 3: Integration Status Check"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Integration Status Check")
    print("="*60 + "\n")
    
    status = check_integration()
    
    print("Framework Integration Status:")
    print(f"  Framework Active: {status['framework_active']}")
    print(f"  Backward Compatibility: {status['backward_compatibility']}")
    print(f"  Infrastructure Impact: {status['infrastructure_impact']}")
    print(f"  Integration Quality: {status['integration_quality']}")
    
    print("\nComponent Status:")
    for component, state in status['components_status'].items():
        print(f"  {component}: {state}")


def example_4_framework_status():
    """Example 4: Comprehensive Framework Status"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Comprehensive Framework Status")
    print("="*60 + "\n")
    
    status = get_framework_status()
    
    print(f"Framework: {status['framework']}")
    print(f"Version: {status['version']}")
    print(f"Status: {'ACTIVE' if status['active'] else 'INACTIVE'}")
    print(f"Operations Count: {status['operations_count']}")
    
    print("\nFramework Metrics:")
    for metric, value in status['metrics'].items():
        print(f"  {metric}: {value}")
    
    print("\nComponent Details:")
    print(f"  Vantage Points Available: {len(status['components']['vantage_point_analyzer']['vantage_points'])}")
    print(f"  UPATSTAR Strategies: {status['components']['upatstar']['reasoning_strategies_available']}")
    print(f"  MMI Ingestions: {status['components']['mmi']['ingestion_count']}")
    print(f"  Ping Ponging: {status['components']['pingpong']['status']}")


def example_5_multi_modal_processing():
    """Example 5: Multi-Modal Data Processing"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Multi-Modal Data Processing")
    print("="*60 + "\n")
    
    result = process_superior(
        task="Analyze multi-modal project data",
        data={
            "project_description": "Advanced AI system with quantum computing integration",
            "technical_specs": {
                "language": "Python",
                "framework": "TensorFlow",
                "compute": "GPU-accelerated"
            },
            "timeline": {
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
                "milestones": 4
            },
            "team_size": 10,
            "budget": 500000
        },
        enable_pingpong=False
    )
    
    print(f"Task: {result['task']}")
    
    if 'mmi_integration' in result:
        mmi = result['mmi_integration']
        print(f"\nMMI Processing:")
        print(f"  Ingestion ID: {mmi['ingestion_id']}")
        print(f"  Data Keys: {', '.join(mmi['data_keys'])}")
        print(f"  Modalities: {', '.join(mmi['modalities_processed'])}")
        print(f"  Integration Quality: {mmi['integration_result']['unified_representation']['integration_quality']}")
    
    print(f"\nUPATSTAR Analysis:")
    upatstar = result['upatstar_processing']
    print(f"  Strategy: {upatstar['selected_strategy']}")
    print(f"  Confidence: {upatstar['reasoning_result']['confidence']}")


def example_6_with_pingpong():
    """Example 6: Processing with Ping Ponging Enabled"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Processing with Ping Ponging (22-Agent Entanglement)")
    print("="*60 + "\n")
    
    result = process_superior(
        task="Complex cognitive task requiring distributed processing across multiple agents",
        data={
            "complexity": "very_high",
            "cognitive_layers": ["perception", "reasoning", "planning", "execution", "reflection"],
            "optimization_targets": ["speed", "accuracy", "adaptability"]
        },
        enable_pingpong=True  # Enable 22-agent entanglement
    )
    
    print(f"Task: {result['task']}")
    print(f"Ping Pong Emitted: {result['pingpong_emitted']}")
    
    if result['pingpong_emitted']:
        print("\n✓ Request emitted to 22-Agent Entanglement System")
        print("  The external system will process this task asynchronously")
        print("  Check pingpong_request.json for the emitted payload")
    
    print(f"\nFramework Processing Complete:")
    print(f"  Components Used: {len(result['components_used'])}")
    print(f"  Processing Time: {result['superior_framework_metadata']['processing_time_seconds']:.4f}s")


def example_7_generate_report():
    """Example 7: Generate Framework Report"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Superior Framework Status Report")
    print("="*60 + "\n")
    
    report = superior_framework.generate_framework_report()
    print(report)


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("SUPERIOR FRAMEWORK - EXAMPLES DEMONSTRATION")
    print("Integrating Ping Ponging, UPATSTAR, and MMI")
    print("="*60)
    
    try:
        # Run all examples
        example_1_basic_processing()
        example_2_mmi_self_ingestion()
        example_3_integration_check()
        example_4_framework_status()
        example_5_multi_modal_processing()
        example_6_with_pingpong()
        example_7_generate_report()
        
        print("\n" + "="*60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
