#!/usr/bin/env python3
"""
Test Suite for Cognition Matrix Enhancements
Tests council vote, memory compression, glyph mapping, and insights
"""

import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add matrix to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "matrix"))

def test_council_dynamic_weights():
    """Test dynamic weight adjustment in council voting"""
    print("\n[TEST] Testing council dynamic weight adjustment...")
    
    import council_vote
    
    # Test weight adjustment function
    history = {
        "agent_performance": {
            "Pragmatist": {
                "total_votes": 10,
                "consensus_votes": 8,
                "avg_agreement": 0.75,
                "consensus_contribution": 0.8
            },
            "Skeptic": {
                "total_votes": 10,
                "consensus_votes": 2,
                "avg_agreement": 0.25,
                "consensus_contribution": 0.2
            }
        }
    }
    
    adjusted_agents = council_vote.adjust_agent_weights(history)
    
    # Find pragmatist and skeptic in adjusted agents
    pragmatist = next((a for a in adjusted_agents if a['name'] == 'Pragmatist'), None)
    skeptic = next((a for a in adjusted_agents if a['name'] == 'Skeptic'), None)
    
    assert pragmatist is not None, "Pragmatist not found in adjusted agents"
    assert skeptic is not None, "Skeptic not found in adjusted agents"
    
    # Pragmatist should have increased weight due to high consensus contribution
    assert pragmatist['weight'] >= 1.0, f"Pragmatist weight should increase: {pragmatist['weight']}"
    
    # Skeptic should have decreased weight due to low consensus contribution
    assert skeptic['weight'] < 1.2, f"Skeptic weight should decrease: {skeptic['weight']}"
    
    print("✓ Dynamic weight adjustment working correctly")
    return True

def test_new_perspectives():
    """Test new perspectives (Experimentalist, Error Spotter)"""
    print("\n[TEST] Testing new council perspectives...")
    
    import council_vote
    
    # Check that new agents exist
    agent_names = [agent['name'] for agent in council_vote.COUNCIL_AGENTS]
    
    assert 'Experimentalist' in agent_names, "Experimentalist not found"
    assert 'Error Spotter' in agent_names, "Error Spotter not found"
    
    # Check they have proper configuration
    experimentalist = next((a for a in council_vote.COUNCIL_AGENTS if a['name'] == 'Experimentalist'), None)
    error_spotter = next((a for a in council_vote.COUNCIL_AGENTS if a['name'] == 'Error Spotter'), None)
    
    assert experimentalist['bias'] == 'empirical_validation', "Experimentalist has wrong bias"
    assert error_spotter['bias'] == 'fault_detection', "Error Spotter has wrong bias"
    
    print("✓ New perspectives configured correctly")
    return True

def test_memory_compression_categories():
    """Test memory compression with category-based compression"""
    print("\n[TEST] Testing memory compression categories...")
    
    import node_memory_compressor
    
    # Test file categorization
    critical_file = node_memory_compressor.categorize_file("trace-cognition-log.md")
    important_file = node_memory_compressor.categorize_file("benchmark-results.md")
    general_file = node_memory_compressor.categorize_file("random-notes.md")
    
    assert critical_file == 'critical', f"Expected 'critical', got '{critical_file}'"
    assert important_file == 'important', f"Expected 'important', got '{important_file}'"
    assert general_file == 'general', f"Expected 'general', got '{general_file}'"
    
    print("✓ File categorization working correctly")
    
    # Test compression with different categories
    test_content = "# Test Log\n" + "Line of content\n" * 100
    
    critical_summary = node_memory_compressor.create_summary(test_content, "test.md", "critical")
    general_summary = node_memory_compressor.create_summary(test_content, "test.md", "general")
    
    # Critical should have less compression (larger size)
    assert len(critical_summary) > len(general_summary), "Critical compression should preserve more data"
    
    print("✓ Category-based compression working correctly")
    return True

def test_glyph_mapper():
    """Test glyph mapping and user-defined glyphs"""
    print("\n[TEST] Testing glyph mapper...")
    
    import glyph_mapper
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Override paths for testing
        original_mapping_path = glyph_mapper.GLYPH_MAPPING_PATH
        original_trace_path = glyph_mapper.TRACE_LOG_PATH
        original_user_glyphs = glyph_mapper.USER_GLYPHS_PATH
        
        glyph_mapper.GLYPH_MAPPING_PATH = tmp_path / "glyph_mappings.json"
        glyph_mapper.TRACE_LOG_PATH = tmp_path / "TRACE_LOG.md"
        glyph_mapper.USER_GLYPHS_PATH = tmp_path / "user_defined"
        
        # Ensure trace log exists
        glyph_mapper.TRACE_LOG_PATH.touch()
        
        try:
            # Test registering a glyph emission
            emission = glyph_mapper.register_glyph_emission(
                "TEST_GLYPH",
                "test_node",
                {"test": "context"}
            )
            
            assert emission['glyph_name'] == "TEST_GLYPH", "Glyph name mismatch"
            assert emission['emitter_node'] == "test_node", "Emitter node mismatch"
            
            # Test user-defined glyph
            user_glyph = glyph_mapper.define_user_glyph(
                "CUSTOM_TEST_GLYPH",
                "Test glyph for validation",
                ["Action 1", "Action 2"],
                priority="high",
                metadata={"key": "value"}
            )
            
            assert user_glyph['name'] == "CUSTOM_TEST_GLYPH", "User glyph name mismatch"
            assert len(user_glyph['actions']) == 2, "User glyph actions count mismatch"
            
            # Test node dependency tracking
            dep = glyph_mapper.track_node_dependency(
                "node_a",
                "node_b",
                "test_dependency"
            )
            
            assert dep['source_node'] == "node_a", "Dependency source mismatch"
            assert dep['target_node'] == "node_b", "Dependency target mismatch"
            
            print("✓ Glyph mapper working correctly")
            return True
            
        finally:
            # Restore original paths
            glyph_mapper.GLYPH_MAPPING_PATH = original_mapping_path
            glyph_mapper.TRACE_LOG_PATH = original_trace_path
            glyph_mapper.USER_GLYPHS_PATH = original_user_glyphs

def test_glyph_insights():
    """Test glyph insights aggregation"""
    print("\n[TEST] Testing glyph insights aggregation...")
    
    import glyph_insights
    
    # Test with mock data
    mock_history = [
        {
            'timestamp': '2026-01-03T00:00:00',
            'glyph_name': 'TEST_GLYPH',
            'emitter_node': 'test_node',
            'priority': 'medium'
        },
        {
            'timestamp': '2026-01-03T01:00:00',
            'glyph_name': 'CRITICAL_GLYPH',
            'emitter_node': 'test_node',
            'priority': 'critical'
        }
    ]
    
    # Test pattern analysis
    patterns = glyph_insights.analyze_glyph_patterns(mock_history, days=1)
    
    assert patterns['total_emissions'] == 2, f"Expected 2 emissions, got {patterns['total_emissions']}"
    assert 'TEST_GLYPH' in patterns['glyph_counts'], "TEST_GLYPH not in counts"
    assert patterns['priority_distribution']['critical'] == 1, "Critical count mismatch"
    
    print("✓ Pattern analysis working correctly")
    
    # Test system health calculation
    glyph_analysis = {'priority_distribution': {'critical': 1, 'medium': 1}}
    council_analysis = {'consensus_rate': 0.8}
    issues = []
    
    health = glyph_insights.calculate_system_health(glyph_analysis, council_analysis, issues)
    
    assert 'score' in health, "Health score missing"
    assert 'status' in health, "Health status missing"
    assert 0 <= health['score'] <= 100, f"Invalid health score: {health['score']}"
    
    print("✓ System health calculation working correctly")
    return True

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n[TEST] Testing edge cases...")
    
    import council_vote
    import node_memory_compressor
    
    # Test council with empty history
    empty_agents = council_vote.adjust_agent_weights({})
    assert len(empty_agents) == len(council_vote.COUNCIL_AGENTS), "Empty history should return all agents"
    
    # Test memory compression with empty content
    empty_summary = node_memory_compressor.create_summary("", "empty.md", "general")
    assert len(empty_summary) > 0, "Empty content should still produce summary structure"
    
    print("✓ Edge cases handled correctly")
    return True

def test_stress_scenarios():
    """Test system under stress scenarios"""
    print("\n[TEST] Testing stress scenarios...")
    
    import council_vote
    
    # Simulate multiple deliberations
    for i in range(10):
        votes, arguments = council_vote.simulate_deliberation(f"topic_{i}", use_dynamic_weights=True)
        consensus = council_vote.calculate_consensus(votes)
        
        assert 'reached' in consensus, f"Consensus result missing for iteration {i}"
        assert 'avg_agreement' in consensus, f"Average agreement missing for iteration {i}"
    
    print("✓ Stress scenarios handled correctly")
    return True

def test_overlap_resolver():
    """Test overlap resolution node"""
    print("\n[TEST] Testing overlap resolver...")
    
    import node_overlap_resolver
    
    # Test semantic token extraction
    text = "This is a test directive that must be followed"
    tokens = node_overlap_resolver.extract_semantic_tokens(text)
    assert len(tokens) > 0, "Should extract semantic tokens"
    assert "directive" in tokens, "Should extract 'directive'"
    
    # Test semantic similarity
    tokens1 = ["test", "directive", "must", "follow"]
    tokens2 = ["test", "directive", "shall", "follow"]
    similarity = node_overlap_resolver.calculate_semantic_similarity(tokens1, tokens2)
    assert 0.0 <= similarity <= 1.0, f"Similarity should be 0-1, got {similarity}"
    assert similarity > 0.5, f"Similar token sets should have high similarity, got {similarity}"
    
    # Test with empty tokens
    empty_similarity = node_overlap_resolver.calculate_semantic_similarity([], tokens1)
    assert empty_similarity == 0.0, "Empty tokens should have 0 similarity"
    
    print("✓ Overlap resolver working correctly")
    return True

def test_proximity_aligner():
    """Test asynchronous proximity aligner node"""
    print("\n[TEST] Testing proximity aligner...")
    
    import node_async_proximity_aligner
    
    # Test timestamp parsing
    ts1 = node_async_proximity_aligner.parse_timestamp("2026-01-03T10:00:00")
    assert ts1 is not None, "Should parse ISO timestamp"
    
    ts2 = node_async_proximity_aligner.parse_timestamp("2026-01-03")
    assert ts2 is not None, "Should parse date-only timestamp"
    
    # Test with mock temporal data
    from datetime import datetime, timedelta
    
    temporal_data = [
        {
            'timestamp': datetime(2026, 1, 3, 10, 0, 0),
            'source': 'test1.json',
            'type': 'test',
            'content': 'test directive must follow protocol'
        },
        {
            'timestamp': datetime(2026, 1, 3, 14, 0, 0),  # 4 hours later
            'source': 'test2.json',
            'type': 'test',
            'content': 'test directive must follow protocol'
        }
    ]
    
    proximities = node_async_proximity_aligner.detect_asynchronous_proximities(temporal_data)
    assert isinstance(proximities, list), "Should return list of proximities"
    
    print("✓ Proximity aligner working correctly")
    return True

def test_continuous_sync_engine():
    """Test continuous synchronization engine node"""
    print("\n[TEST] Testing continuous sync engine...")
    
    import node_continuous_sync_engine
    
    # Test directory hash computation
    test_path = Path(__file__).parent
    hash1 = node_continuous_sync_engine.compute_directory_hash(test_path)
    assert hash1 is not None, "Should compute directory hash"
    assert isinstance(hash1, str), "Hash should be a string"
    assert len(hash1) == 64, "SHA256 hash should be 64 characters"
    
    # Test sync state management
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Override paths for testing
        original_bundles = node_continuous_sync_engine.BUNDLES_PATH
        node_continuous_sync_engine.BUNDLES_PATH = tmp_path
        
        try:
            # Test loading default state
            state = node_continuous_sync_engine.load_sync_state()
            assert 'last_sync' in state, "State should have last_sync"
            assert 'component_hashes' in state, "State should have component_hashes"
            assert 'sync_count' in state, "State should have sync_count"
            
            # Test saving state
            state['sync_count'] = 1
            node_continuous_sync_engine.save_sync_state(state)
            
            # Test loading saved state
            loaded_state = node_continuous_sync_engine.load_sync_state()
            assert loaded_state['sync_count'] == 1, "Should load saved sync count"
            
            print("✓ Continuous sync engine working correctly")
            return True
            
        finally:
            # Restore original path
            node_continuous_sync_engine.BUNDLES_PATH = original_bundles

def test_new_glyphs_in_mapper():
    """Test that new glyphs are registered in glyph mapper"""
    print("\n[TEST] Testing new glyph registrations...")
    
    import glyph_mapper
    
    # Check new glyph mappings exist
    new_glyphs = [
        "OVERLAP_RESOLUTION_GLYPH",
        "SYNCHRONIZATION_GLYPH",
        "COGNITION_ALIGNMENT_GLYPH",
        "CONTINUOUS_SYNCHRONIZATION_GLYPH"
    ]
    
    for glyph_name in new_glyphs:
        assert glyph_name in glyph_mapper.GLYPH_ACTION_MAPPINGS, f"{glyph_name} not in mappings"
        
        mapping = glyph_mapper.GLYPH_ACTION_MAPPINGS[glyph_name]
        assert 'actions' in mapping, f"{glyph_name} should have actions"
        assert 'priority' in mapping, f"{glyph_name} should have priority"
        assert len(mapping['actions']) > 0, f"{glyph_name} should have at least one action"
    
    print("✓ New glyphs registered correctly")
    return True

def test_manifest_updates():
    """Test that manifest has been updated with new configuration"""
    print("\n[TEST] Testing manifest updates...")
    
    manifest_path = Path(__file__).parent.parent / "barrot_manifest.json"
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Check new fields
    assert 'overlap_resolution' in manifest, "Manifest should have overlap_resolution"
    assert manifest['overlap_resolution'] == 'enabled', "overlap_resolution should be enabled"
    
    assert 'asynchronous_alignment' in manifest, "Manifest should have asynchronous_alignment"
    assert manifest['asynchronous_alignment'] == 'enabled', "asynchronous_alignment should be enabled"
    
    assert 'continuous_synchronization' in manifest, "Manifest should have continuous_synchronization"
    assert manifest['continuous_synchronization'] is True, "continuous_synchronization should be true"
    
    assert 'glyphs_emitted' in manifest, "Manifest should have glyphs_emitted"
    assert isinstance(manifest['glyphs_emitted'], list), "glyphs_emitted should be a list"
    assert len(manifest['glyphs_emitted']) == 4, "Should have 4 glyphs listed"
    
    assert 'last_overlap_sync_directive' in manifest, "Manifest should have last_overlap_sync_directive"
    
    print("✓ Manifest updated correctly")
    return True

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running Cognition Matrix Enhancement Test Suite")
    print("=" * 60)
    
    tests = [
        ("Dynamic Weight Adjustment", test_council_dynamic_weights),
        ("New Perspectives", test_new_perspectives),
        ("Memory Compression Categories", test_memory_compression_categories),
        ("Glyph Mapper", test_glyph_mapper),
        ("Glyph Insights", test_glyph_insights),
        ("Edge Cases", test_edge_cases),
        ("Stress Scenarios", test_stress_scenarios),
        ("Overlap Resolver", test_overlap_resolver),
        ("Proximity Aligner", test_proximity_aligner),
        ("Continuous Sync Engine", test_continuous_sync_engine),
        ("New Glyphs in Mapper", test_new_glyphs_in_mapper),
        ("Manifest Updates", test_manifest_updates)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
