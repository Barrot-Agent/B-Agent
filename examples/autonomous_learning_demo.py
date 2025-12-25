"""
Example Usage: Autonomous Learning Demo

Run from repository root with:
    PYTHONPATH=. python examples/autonomous_learning_demo.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.autonomous_learning import initialize_autonomous_learning

def main():
    print("=" * 60)
    print("Autonomous Learning Demo")
    print("=" * 60)
    
    # Initialize
    components = initialize_autonomous_learning()
    pipeline = components['pipeline']
    meta_engine = components['meta_engine']
    
    # 1. Evaluate performance
    print("\n1. Evaluating performance on tasks...")
    
    eval1 = pipeline.evaluate_performance('image_classification', {
        'accuracy': 0.92,
        'precision': 0.90,
        'recall': 0.88
    })
    print(f"   Task: {eval1['task']}")
    print(f"   Improvement needed: {eval1['improvement_needed']}")
    
    eval2 = pipeline.evaluate_performance('image_classification', {
        'accuracy': 0.85,  # Lower than baseline
        'precision': 0.83,
        'recall': 0.82
    })
    print(f"\n   Task: {eval2['task']}")
    print(f"   Improvement needed: {eval2['improvement_needed']}")
    
    # 2. Generate improvement plan
    if eval2['improvement_needed']:
        print("\n2. Generating improvement plan...")
        plan = pipeline.generate_improvement_plan(eval2)
        print(f"   Actions: {len(plan['actions'])}")
        for action in plan['actions']:
            print(f"   - {action['action']}: {action['current']:.3f} -> {action['target']:.3f}")
    
    # 3. Meta-learning across domains
    print("\n3. Meta-learning across domains...")
    
    meta_engine.learn_from_task('computer_vision', {
        'features': ['edge_detection', 'feature_extraction'],
        'success': True,
        'approach': 'CNN-based'
    })
    
    meta_engine.learn_from_task('nlp', {
        'features': ['tokenization', 'embedding'],
        'success': True,
        'approach': 'transformer-based'
    })
    
    # Transfer knowledge
    transfer = meta_engine.transfer_knowledge('computer_vision', 'nlp')
    print(f"   Transferred {len(transfer['patterns'])} patterns")
    print(f"   From: {transfer['source']} -> To: {transfer['target']}")
    
    # 4. Cross-domain insights
    print("\n4. Analyzing cross-domain insights...")
    insights = meta_engine.get_cross_domain_insights()
    for insight in insights:
        print(f"   Domain: {insight['domain']}")
        print(f"   - Patterns: {insight['pattern_count']}")
        print(f"   - Success rate: {insight['success_rate']:.2%}")
        print(f"   - Generalization score: {insight['generalization_score']:.2f}")
    
    print("\n" + "=" * 60)
    print("Demo Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
