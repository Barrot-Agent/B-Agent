#!/usr/bin/env python3
"""
Test Suite for Transformative Insights Framework
Validates core functionality and integration
"""

import sys
from datetime import datetime
from transformative_insights import (
    transformative_engine,
    acquire_transformative_data,
    discover_transformative_insights,
    InsightType,
    TransformationStage
)
from barrot_integration import (
    barrot_system,
    transform_data_to_insights
)


def test_data_acquisition():
    """Test basic data acquisition"""
    print("Testing data acquisition...")
    
    fragment_id = acquire_transformative_data(
        content="Test data for validation",
        source="test_suite",
        category="testing"
    )
    
    assert fragment_id is not None
    assert fragment_id.startswith("frag_")
    assert fragment_id in transformative_engine.data_fragments
    
    fragment = transformative_engine.data_fragments[fragment_id]
    assert fragment.content == "Test data for validation"
    assert fragment.source == "test_suite"
    assert fragment.category == "testing"
    assert fragment.transformation_stage == TransformationStage.COLLECTED
    
    print("✅ Data acquisition test passed")
    return True


def test_bulk_acquisition():
    """Test bulk data acquisition"""
    print("Testing bulk data acquisition...")
    
    data_items = [
        {"content": "Item 1", "source": "bulk_test", "category": "cat1"},
        {"content": "Item 2", "source": "bulk_test", "category": "cat2"},
        {"content": "Item 3", "source": "bulk_test", "category": "cat1"}
    ]
    
    fragment_ids = transformative_engine.acquire_bulk_data(data_items)
    
    assert len(fragment_ids) == 3
    assert all(fid in transformative_engine.data_fragments for fid in fragment_ids)
    
    print("✅ Bulk acquisition test passed")
    return True


def test_pattern_recognition():
    """Test pattern recognition"""
    print("Testing pattern recognition...")
    
    # First acquire some data
    fragment_ids = []
    for i in range(5):
        fid = acquire_transformative_data(
            content=f"Pattern test {i}",
            source=f"source_{i % 2}",
            category=f"category_{i % 3}"
        )
        fragment_ids.append(fid)
    
    patterns = transformative_engine.identify_patterns(fragment_ids)
    
    assert "temporal_patterns" in patterns
    assert "categorical_patterns" in patterns
    assert "source_patterns" in patterns
    assert "content_patterns" in patterns
    
    print("✅ Pattern recognition test passed")
    return True


def test_convergence_detection():
    """Test convergence detection"""
    print("Testing convergence detection...")
    
    # Acquire related data
    fragment_ids = []
    for i in range(3):
        fid = acquire_transformative_data(
            content=f"Related data {i}",
            source="convergence_test",
            category="related"
        )
        fragment_ids.append(fid)
    
    convergences = transformative_engine.detect_convergence(fragment_ids)
    
    assert isinstance(convergences, list)
    # May or may not find convergences depending on similarity
    
    print("✅ Convergence detection test passed")
    return True


def test_evolution_tracking():
    """Test evolution tracking"""
    print("Testing evolution tracking...")
    
    fragment_id = acquire_transformative_data(
        content="Initial state",
        source="evolution_test",
        category="tracking"
    )
    
    evolution1 = transformative_engine.track_evolution(fragment_id, "State 2")
    evolution2 = transformative_engine.track_evolution(fragment_id, "State 3")
    
    assert evolution1["fragment_id"] == fragment_id
    assert evolution1["evolution_steps"] == 1
    assert evolution2["evolution_steps"] == 2
    
    fragment = transformative_engine.data_fragments[fragment_id]
    assert fragment.transformation_stage == TransformationStage.EVOLVED
    
    print("✅ Evolution tracking test passed")
    return True


def test_insight_synthesis():
    """Test insight synthesis"""
    print("Testing insight synthesis...")
    
    # Acquire data for synthesis
    fragment_ids = []
    for i in range(3):
        fid = acquire_transformative_data(
            content=f"Synthesis data {i}",
            source="synthesis_test",
            category="synthesis"
        )
        fragment_ids.append(fid)
    
    insight = transformative_engine.synthesize_insights(fragment_ids)
    
    assert insight.id is not None
    assert isinstance(insight.insight_type, InsightType)
    assert insight.confidence > 0.0
    assert insight.impact_score >= 0.0
    assert len(insight.involved_data) == len(fragment_ids)
    
    print(f"✅ Insight synthesis test passed (confidence: {insight.confidence:.2f})")
    return True


def test_transcendence_detection():
    """Test transcendence detection"""
    print("Testing transcendence detection...")
    
    # Create high-impact insight
    fragment_ids = []
    for i in range(2):
        fid = acquire_transformative_data(
            content=f"High impact data {i}",
            source="transcendence_test",
            category="breakthrough"
        )
        fragment_ids.append(fid)
    
    insight = transformative_engine.synthesize_insights(fragment_ids)
    transcendence_events = transformative_engine.detect_transcendence([insight.id])
    
    assert isinstance(transcendence_events, list)
    # May or may not detect transcendence depending on scores
    
    print("✅ Transcendence detection test passed")
    return True


def test_epiphany_generation():
    """Test epiphany generation"""
    print("Testing epiphany generation...")
    
    # Generate some insights first
    for i in range(2):
        fragment_ids = [
            acquire_transformative_data(
                content=f"Epiphany data {i}-{j}",
                source="epiphany_test",
                category="insight"
            )
            for j in range(2)
        ]
        transformative_engine.synthesize_insights(fragment_ids)
    
    epiphany = transformative_engine.generate_epiphany()
    
    assert epiphany["id"] is not None
    assert "confidence" in epiphany
    assert "impact_potential" in epiphany
    assert "actionable_steps" in epiphany
    
    print(f"✅ Epiphany generation test passed (confidence: {epiphany['confidence']:.2f})")
    return True


def test_realization():
    """Test insight realization"""
    print("Testing insight realization...")
    
    # Create insights
    fragment_ids = [
        acquire_transformative_data(
            content=f"Realization data {i}",
            source="realization_test",
            category="application"
        )
        for i in range(2)
    ]
    
    insight = transformative_engine.synthesize_insights(fragment_ids)
    realizations = transformative_engine.realize_insights([insight.id])
    
    assert "realized_insights" in realizations
    assert "realizations" in realizations
    assert "framework_integration" in realizations
    
    print("✅ Realization test passed")
    return True


def test_integrated_pipeline():
    """Test complete integrated pipeline"""
    print("Testing complete integrated pipeline...")
    
    data_items = [
        {"content": "Pipeline test 1", "source": "pipeline", "category": "test1"},
        {"content": "Pipeline test 2", "source": "pipeline", "category": "test2"},
        {"content": "Pipeline test 3", "source": "pipeline", "category": "test1"}
    ]
    
    result = transform_data_to_insights(data_items)
    
    assert "acquisition" in result
    assert "patterns" in result
    assert "convergences" in result
    assert "insights" in result
    assert "transcendence" in result
    assert "epiphany" in result
    assert "realizations" in result
    
    print("✅ Integrated pipeline test passed")
    return True


def test_system_integration():
    """Test integration with Barrot system"""
    print("Testing Barrot system integration...")
    
    status = barrot_system.get_system_status()
    
    assert "transformative_insights_status" in status
    ti_status = status["transformative_insights_status"]
    
    assert "total_fragments" in ti_status
    assert "total_insights" in ti_status
    assert "convergence_events" in ti_status
    
    print("✅ System integration test passed")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("TRANSFORMATIVE INSIGHTS FRAMEWORK - TEST SUITE")
    print("=" * 80 + "\n")
    
    tests = [
        test_data_acquisition,
        test_bulk_acquisition,
        test_pattern_recognition,
        test_convergence_detection,
        test_evolution_tracking,
        test_insight_synthesis,
        test_transcendence_detection,
        test_epiphany_generation,
        test_realization,
        test_integrated_pipeline,
        test_system_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 80 + "\n")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
