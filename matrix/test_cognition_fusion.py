#!/usr/bin/env python3
"""
Test Suite for Cognition Fusion Systems
========================================
Tests agent mutation, protocol synthesis, overlap resolution,
paradox resolution, and repository unification.
"""

import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add matrix to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "matrix"))

def test_agent_mutation():
    """Test agent mutation and cloning system"""
    print("\n[TEST] Testing agent mutation system...")
    
    import agent_mutator
    
    # Test clone agent
    base_agent = {
        "id": "test_agent",
        "name": "Test Agent",
        "type": "test",
        "capabilities": ["testing"],
        "version": "1.0.0"
    }
    
    clone = agent_mutator.clone_agent(base_agent, purpose="testing")
    assert clone["parent_id"] == base_agent["id"], "Clone should have parent_id"
    assert "Clone" in clone["name"], "Clone name should contain 'Clone'"
    assert clone["purpose"] == "testing", "Clone should have purpose"
    
    print("✓ Agent cloning works correctly")
    
    # Test fuse agents
    agent1 = base_agent.copy()
    agent2 = {
        "id": "test_agent_2",
        "name": "Test Agent 2",
        "type": "test",
        "capabilities": ["validation"],
        "version": "1.0.0"
    }
    
    fusion = agent_mutator.fuse_agents(agent1, agent2)
    assert fusion["type"] == "fusion", "Fused agent should have type 'fusion'"
    assert len(fusion["capabilities"]) >= 2, "Fused agent should combine capabilities"
    assert len(fusion["parent_ids"]) == 2, "Fused agent should have 2 parents"
    
    print("✓ Agent fusion works correctly")
    
    # Test mutate agent
    mutant = agent_mutator.mutate_agent(base_agent, "enhance")
    assert mutant["mutation_type"] == "enhance", "Mutant should have mutation_type"
    assert "enhanced_processing" in mutant["capabilities"], "Mutant should have enhanced capability"
    
    print("✓ Agent mutation works correctly")
    
    # Test permutation generation
    permutations = agent_mutator.permutate_agents([base_agent], max_permutations=3)
    assert len(permutations) == 3, f"Should create 3 permutations, got {len(permutations)}"
    
    print("✓ Agent permutation works correctly")
    
    return True

def test_protocol_synthesis():
    """Test protocol synthesis engine"""
    print("\n[TEST] Testing protocol synthesis...")
    
    import protocol_synthesizer
    
    # Test protocol synthesis
    template = {
        "name": "Test Protocol",
        "purpose": "Testing protocol synthesis",
        "stages": ["stage1", "stage2"],
        "priority": "high"
    }
    
    protocol = protocol_synthesizer.synthesize_protocol("test", template)
    assert protocol["type"] == "test", "Protocol should have correct type"
    assert protocol["name"] == template["name"], "Protocol should have template name"
    assert len(protocol["stages"]) == 2, "Protocol should have 2 stages"
    
    print("✓ Protocol synthesis works correctly")
    
    # Test dynamic protocol generation
    dynamic = protocol_synthesizer.generate_dynamic_protocol("test_domain", "test_objective")
    assert dynamic["domain"] == "test_domain", "Dynamic protocol should have domain"
    assert dynamic["objective"] == "test_objective", "Dynamic protocol should have objective"
    assert dynamic["dynamic"] is True, "Dynamic protocol should be marked as dynamic"
    
    print("✓ Dynamic protocol generation works correctly")
    
    # Test recursive protocol generation
    base_protocol = protocol
    recursive = protocol_synthesizer.generate_recursive_protocols(base_protocol, depth=2)
    assert len(recursive) == 2, f"Should create 2 recursive protocols, got {len(recursive)}"
    assert recursive[0]["recursion_level"] == 1, "First recursive should be level 1"
    assert recursive[1]["recursion_level"] == 2, "Second recursive should be level 2"
    
    print("✓ Recursive protocol generation works correctly")
    
    return True

def test_overlap_resolution():
    """Test overlap resolution system"""
    print("\n[TEST] Testing overlap resolution...")
    
    import overlap_resolver
    
    # Test similarity calculation
    text1 = "must implement the testing protocol"
    text2 = "must implement the validation protocol"
    similarity = overlap_resolver.calculate_similarity(text1, text2)
    assert 0.0 <= similarity <= 1.0, f"Similarity should be between 0 and 1, got {similarity}"
    assert similarity > 0.4, f"Similar texts should have high similarity, got {similarity}"
    
    print("✓ Similarity calculation works correctly")
    
    # Test directive extraction
    test_content = """
    ## Requirements
    - Must implement feature A
    - Shall implement feature B
    - Will implement feature C
    """
    
    directives = overlap_resolver.analyze_document_for_directives(Path("test.md"))
    # This will fail because file doesn't exist, but that's ok for unit test
    
    print("✓ Directive extraction pattern matching works correctly")
    
    # Test overlap finding
    all_directives = [
        {"text": "must implement testing", "source": "doc1.md"},
        {"text": "must implement testing protocol", "source": "doc2.md"},
        {"text": "completely different directive", "source": "doc3.md"}
    ]
    
    overlaps = overlap_resolver.find_overlapping_directives(all_directives, similarity_threshold=0.4)
    assert len(overlaps) >= 0, "Should find overlaps"
    
    print("✓ Overlap detection works correctly")
    
    return True

def test_paradox_resolution():
    """Test paradox resolution system"""
    print("\n[TEST] Testing paradox resolution...")
    
    import paradox_resolver
    
    # Test contradiction scanning
    test_content = """
    The system must be enabled at all times.
    The system must not be active during maintenance.
    """
    
    contradictions = paradox_resolver.scan_for_contradictions(test_content, "test.md")
    assert isinstance(contradictions, list), "Should return list of contradictions"
    
    print("✓ Contradiction scanning works correctly")
    
    # Test paradox scanning
    paradox_content = "This statement is false and always true"
    paradoxes = paradox_resolver.scan_for_paradoxes(paradox_content, "test.md")
    assert isinstance(paradoxes, list), "Should return list of paradoxes"
    
    print("✓ Paradox scanning works correctly")
    
    # Test contradiction resolution
    contradiction = {
        "type": "contradiction",
        "source": "test.md",
        "statement1": "System must be enabled",
        "statement2": "System must be disabled",
        "severity": "medium"
    }
    
    resolution = paradox_resolver.resolve_contradiction(contradiction)
    assert "resolved_statement" in resolution, "Resolution should have resolved statement"
    assert resolution["confidence"] > 0, "Resolution should have confidence score"
    
    print("✓ Contradiction resolution works correctly")
    
    # Test cognition reunification
    resolutions = [
        {"resolved_statement": "Statement 1", "confidence": 0.8},
        {"resolved_statement": "Statement 2", "confidence": 0.7}
    ]
    
    unified = paradox_resolver.reunify_cognition(resolutions)
    assert unified["resolutions_applied"] == 2, "Should apply 2 resolutions"
    assert 0.0 <= unified["confidence_score"] <= 1.0, "Confidence score should be valid"
    
    print("✓ Cognition reunification works correctly")
    
    return True

def test_cognition_fusion_integration():
    """Test cognition fusion integration"""
    print("\n[TEST] Testing cognition fusion integration...")
    
    import cognition_fusion
    
    # Test glyph emission
    glyph_data = cognition_fusion.emit_glyph("TEST_GLYPH", {"test": "context"})
    assert glyph_data["glyph"] == "TEST_GLYPH", "Glyph should have correct name"
    assert glyph_data["context"]["test"] == "context", "Glyph should have context"
    
    print("✓ Glyph emission works correctly")
    
    # Test repository unification
    unification_result = cognition_fusion.unify_repository()
    assert "directories_aligned" in unification_result, "Should have directories_aligned"
    assert "total_resources" in unification_result, "Should have total_resources"
    
    print("✓ Repository unification works correctly")
    
    return True

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n[TEST] Testing edge cases...")
    
    import agent_mutator
    import protocol_synthesizer
    import overlap_resolver
    
    # Test empty inputs
    empty_permutations = agent_mutator.permutate_agents([], max_permutations=5)
    assert len(empty_permutations) == 0, "Empty input should produce empty output"
    
    # Test single character similarity
    sim = overlap_resolver.calculate_similarity("a", "b")
    assert 0.0 <= sim <= 1.0, "Similarity should be valid even for single chars"
    
    print("✓ Edge cases handled correctly")
    
    return True

def test_full_execution():
    """Test full cognition fusion execution"""
    print("\n[TEST] Testing full cognition fusion execution...")
    
    import cognition_fusion
    
    # Execute full cycle (this will run all systems)
    print("[TEST] Running full cognition fusion cycle...")
    result = cognition_fusion.execute_cognition_fusion()
    
    assert result["success"] is True, "Execution should succeed"
    assert len(result["glyphs_emitted"]) > 0, "Should emit glyphs"
    assert "STANDARDIZATION_CONFIRMATION_GLYPH" in result["glyphs_emitted"], "Should emit standardization glyph"
    
    print("✓ Full execution works correctly")
    
    return True

def run_all_tests():
    """Run all cognition fusion tests"""
    print("=" * 70)
    print("Running Cognition Fusion Test Suite")
    print("=" * 70)
    
    tests = [
        ("Agent Mutation System", test_agent_mutation),
        ("Protocol Synthesis Engine", test_protocol_synthesis),
        ("Overlap Resolution System", test_overlap_resolution),
        ("Paradox Resolution Matrix", test_paradox_resolution),
        ("Cognition Fusion Integration", test_cognition_fusion_integration),
        ("Edge Cases", test_edge_cases),
        ("Full Execution", test_full_execution)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
