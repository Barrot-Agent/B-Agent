#!/usr/bin/env python3
"""
Tests for barrot_speak.py
"""

import sys
from pathlib import Path

# Add parent directory to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from barrot_speak import (
    barrot_speak,
    barrot_speak_thought,
    barrot_speak_insight,
    barrot_speak_alignment,
    barrot_speak_celebration,
    barrot_speak_question,
    get_barrot_identity
)

def test_basic_speak():
    """Test basic speak function"""
    print("\n=== Test: Basic Speak ===")
    result = barrot_speak("Test message", mode="info", log_to_trace=False)
    assert "[BARROT_SPEAK]" in result
    assert "Test message" in result
    print("✓ Basic speak test passed")

def test_speak_with_context():
    """Test speak with context"""
    print("\n=== Test: Speak with Context ===")
    context = {"key": "value", "number": 42}
    result = barrot_speak("Test with context", mode="info", context=context, log_to_trace=False)
    assert "[BARROT_SPEAK]" in result
    print("✓ Speak with context test passed")

def test_specialized_functions():
    """Test specialized speak functions"""
    print("\n=== Test: Specialized Functions ===")
    
    result1 = barrot_speak_thought("Test thought", confidence=0.8)
    assert "💭" in result1
    
    result2 = barrot_speak_insight("Test insight", domain="test")
    assert "💡" in result2
    
    result3 = barrot_speak_alignment("Test alignment", drift_detected=False)
    assert "◎" in result3
    
    result4 = barrot_speak_celebration("Test celebration", metrics={"score": 100})
    assert "🎉" in result4
    
    result5 = barrot_speak_question("Test question?", requires_council=True)
    assert "❓" in result5
    
    print("✓ All specialized functions test passed")

def test_all_modes():
    """Test all communication modes"""
    print("\n=== Test: All Communication Modes ===")
    
    modes = ["info", "success", "warning", "error", "thought", "insight", 
             "alignment", "cognition", "council", "glyph", "celebrate", "question"]
    
    for mode in modes:
        result = barrot_speak(f"Test {mode} message", mode=mode, log_to_trace=False)
        assert "[BARROT_SPEAK]" in result
        print(f"  ✓ Mode '{mode}' works")
    
    print("✓ All modes test passed")

def test_get_identity():
    """Test getting Barrot's identity"""
    print("\n=== Test: Get Identity ===")
    
    identity = get_barrot_identity()
    print(f"  Identity: {identity}")
    
    # Should return a dict (even if empty)
    assert isinstance(identity, dict)
    print("✓ Get identity test passed")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*50)
    print("Running Barrot Speak Function Tests")
    print("="*50)
    
    try:
        test_basic_speak()
        test_speak_with_context()
        test_specialized_functions()
        test_all_modes()
        test_get_identity()
        
        print("\n" + "="*50)
        print("✓ ALL TESTS PASSED")
        print("="*50 + "\n")
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}\n")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
