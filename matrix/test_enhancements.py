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

def test_global_crawler_glyphs():
    """Test global crawler glyph definitions"""
    print("\n[TEST] Testing global crawler glyph definitions...")
    
    import glyph_mapper
    
    # Check that global crawler glyphs are defined in mappings
    required_glyphs = [
        "GLOBAL_CRAWL_INITIATED_GLYPH",
        "REGIONAL_ACCESS_GLYPH",
        "ACCESS_BLOCK_GLYPH",
        "CRAWL_SYNCHRONIZATION_GLYPH",
        "GLOBAL_COGNITION_EXPANSION_GLYPH"
    ]
    
    for glyph_name in required_glyphs:
        assert glyph_name in glyph_mapper.GLYPH_ACTION_MAPPINGS, f"{glyph_name} not in glyph mappings"
        mapping = glyph_mapper.GLYPH_ACTION_MAPPINGS[glyph_name]
        assert 'actions' in mapping, f"{glyph_name} missing actions"
        assert 'priority' in mapping, f"{glyph_name} missing priority"
        assert len(mapping['actions']) > 0, f"{glyph_name} has no actions defined"
    
    print("✓ Global crawler glyphs properly defined")
    return True

def test_global_crawler_regional_access():
    """Test global crawler regional accessibility simulation"""
    print("\n[TEST] Testing regional accessibility simulation...")
    
    import node_global_crawler
    
    # Test regional access simulation
    test_region = {
        "name": "TestRegion",
        "domains": ["test1", "test2"],
        "framework": "Test Framework"
    }
    
    access_result = node_global_crawler.simulate_regional_access(test_region)
    
    assert 'region' in access_result, "Missing region in access result"
    assert 'accessible' in access_result, "Missing accessible flag in result"
    assert 'framework' in access_result, "Missing framework in result"
    assert 'timestamp' in access_result, "Missing timestamp in result"
    assert access_result['region'] == "TestRegion", "Region name mismatch"
    
    print("✓ Regional accessibility simulation working correctly")
    return True

def test_global_crawler_manifest_update():
    """Test global crawler manifest updates"""
    print("\n[TEST] Testing manifest update with global crawling data...")
    
    import node_global_crawler
    import json
    
    # Create temporary manifest for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_manifest = Path(tmpdir) / "test_manifest.json"
        
        # Create initial manifest
        initial_manifest = {
            "barrot_identity": {"github_user": "Test", "repo": "Test"},
            "cognition": {}
        }
        
        with open(tmp_manifest, 'w') as f:
            json.dump(initial_manifest, f)
        
        # Override manifest path
        original_manifest_path = node_global_crawler.MANIFEST_PATH
        node_global_crawler.MANIFEST_PATH = tmp_manifest
        
        try:
            # Simulate update
            regional_results = {
                "accessible_count": 5,
                "blocked_count": 2
            }
            sync_results = {
                "total_targets": 30,
                "categories": 6
            }
            expansion_results = {
                "new_concepts": 30,
                "domains": 6
            }
            
            node_global_crawler.update_manifest_with_crawl_data(
                regional_results, 
                sync_results, 
                expansion_results
            )
            
            # Verify manifest was updated
            with open(tmp_manifest, 'r') as f:
                updated_manifest = json.load(f)
            
            assert 'global_crawling' in updated_manifest, "global_crawling section missing"
            gc = updated_manifest['global_crawling']
            
            assert gc['active'] == True, "active flag not set"
            assert gc['regional_access_reporting'] == True, "reporting flag not set"
            assert gc['regions_accessible'] == 5, "accessible regions count mismatch"
            assert gc['regions_blocked'] == 2, "blocked regions count mismatch"
            assert gc['targets_crawled'] == 30, "targets crawled count mismatch"
            assert len(gc['glyphs_emitted']) == 5, "glyphs emitted count mismatch"
            
            print("✓ Manifest update working correctly")
            return True
            
        finally:
            # Restore original path
            node_global_crawler.MANIFEST_PATH = original_manifest_path

def test_global_crawler_integration():
    """Test global crawler end-to-end integration"""
    print("\n[TEST] Testing global crawler integration...")
    
    import node_global_crawler
    
    # Test that all global regions are defined
    assert len(node_global_crawler.GLOBAL_REGIONS) >= 6, "Not enough global regions defined"
    
    # Test that all crawl target categories are defined
    assert len(node_global_crawler.CRAWL_TARGETS) >= 5, "Not enough crawl target categories"
    
    # Verify each region has required fields
    for region in node_global_crawler.GLOBAL_REGIONS:
        assert 'name' in region, "Region missing name"
        assert 'domains' in region, "Region missing domains"
        assert 'framework' in region, "Region missing framework"
        assert len(region['domains']) > 0, f"Region {region['name']} has no domains"
    
    # Verify each crawl target category has targets
    for category, targets in node_global_crawler.CRAWL_TARGETS.items():
        assert len(targets) > 0, f"Category {category} has no targets"
    
    print("✓ Global crawler integration verified")
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
        ("Global Crawler Glyphs", test_global_crawler_glyphs),
        ("Global Crawler Regional Access", test_global_crawler_regional_access),
        ("Global Crawler Manifest Update", test_global_crawler_manifest_update),
        ("Global Crawler Integration", test_global_crawler_integration)
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
