#!/usr/bin/env python3
"""
Tests for the Barrot Ping-Pong Offload Protocol

This script validates that the offload system works correctly and
adheres to the sacred protocol requirements.
"""

import json
import os
import sys
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from barrot_offload import PingPongOffload


def test_module_import():
    """Test that the module can be imported."""
    print("✓ Testing module import...")
    try:
        _ = PingPongOffload
        print("  ✅ Module imported successfully")
        return True
    except ImportError as e:
        print(f"  ❌ Failed to import module: {e}")
        return False


def test_template_exists():
    """Test that the template file exists."""
    print("✓ Testing template file existence...")
    if os.path.exists('pingpong_request.json'):
        print("  ✅ Template file exists")
        return True
    else:
        print("  ❌ Template file not found")
        return False


def test_template_valid_json():
    """Test that the template is valid JSON."""
    print("✓ Testing template JSON validity...")
    try:
        with open('pingpong_request.json', 'r') as f:
            json.load(f)
        print("  ✅ Template is valid JSON")
        return True
    except json.JSONDecodeError as e:
        print(f"  ❌ Template is invalid JSON: {e}")
        return False


def test_template_structure():
    """Test that the template has the required structure."""
    print("✓ Testing template structure...")
    with open('pingpong_request.json', 'r') as f:
        data = json.load(f)
    
    required_keys = [
        'protocol_version',
        'request_type',
        'metadata',
        'entanglement_system',
        'request_details',
        'constraints',
        'notes'
    ]
    
    missing_keys = [key for key in required_keys if key not in data]
    
    if not missing_keys:
        print("  ✅ Template has all required keys")
        return True
    else:
        print(f"  ❌ Template missing keys: {missing_keys}")
        return False


def test_manifest_exists():
    """Test that the manifest file exists."""
    print("✓ Testing manifest file existence...")
    if os.path.exists('manifest.yaml'):
        print("  ✅ Manifest file exists")
        return True
    else:
        print("  ❌ Manifest file not found")
        return False


def test_class_initialization():
    """Test that the PingPongOffload class can be initialized."""
    print("✓ Testing class initialization...")
    try:
        offload = PingPongOffload()
        assert isinstance(offload, PingPongOffload)
        print("  ✅ Class initialized successfully")
        return True
    except Exception as e:
        print(f"  ❌ Failed to initialize class: {e}")
        return False


def test_load_template():
    """Test that the template can be loaded."""
    print("✓ Testing template loading...")
    try:
        offload = PingPongOffload()
        template = offload.load_template()
        
        # Basic validation of loaded template
        assert template is not None
        assert isinstance(template, dict)
        
        print("  ✅ Template loaded successfully")
        return True
    except Exception as e:
        print(f"  ❌ Failed to load template: {e}")
        return False


def test_create_request():
    """Test that a request can be created."""
    print("✓ Testing request creation...")
    try:
        offload = PingPongOffload()
        request = offload.create_request(
            operation="test_operation",
            context="test_context",
            parameters={"test": "value"},
            expected_outcome="test_outcome",
            priority="standard"
        )
        
        # Validate request structure
        assert request["metadata"]["timestamp"] is not None
        assert request["metadata"]["request_id"] is not None
        assert request["request_details"]["operation"] == "test_operation"
        assert request["request_details"]["context"] == "test_context"
        assert request["request_details"]["parameters"]["test"] == "value"
        assert request["request_details"]["expected_outcome"] == "test_outcome"
        assert request["metadata"]["priority"] == "standard"
        
        print("  ✅ Request created successfully with correct structure")
        return True
    except Exception as e:
        print(f"  ❌ Failed to create request: {e}")
        return False


def test_constraints_validation():
    """Test that the constraints are properly set."""
    print("✓ Testing constraints validation...")
    try:
        offload = PingPongOffload()
        template = offload.load_template()
        
        constraints = template["constraints"]
        # Validate all constraints are explicitly set to True
        assert constraints["no_internal_simulation"] is True
        assert constraints["must_defer_to_github_system"] is True
        assert constraints["sacred_protocol"] is True
        assert constraints["non_negotiable"] is True
        
        print("  ✅ All constraints properly set")
        return True
    except (KeyError, AssertionError) as e:
        print(f"  ❌ Constraint validation failed: {e}")
        return False


def test_sacred_protocol_acknowledgment():
    """Test that the sacred protocol acknowledgment works."""
    print("✓ Testing sacred protocol acknowledgment...")
    try:
        offload = PingPongOffload()
        acknowledgment = offload.acknowledge_sacred_protocol()
        
        # Check that acknowledgment contains key phrases
        assert "SACRED" in acknowledgment
        assert "NON-NEGOTIABLE" in acknowledgment
        assert "22 specialized agents" in acknowledgment
        assert "BINDING and PERMANENT" in acknowledgment
        
        print("  ✅ Sacred protocol acknowledgment contains required elements")
        return True
    except (AssertionError, Exception) as e:
        print(f"  ❌ Sacred protocol acknowledgment failed: {e}")
        return False


def test_validation_check():
    """Test the internal simulation validation check."""
    print("✓ Testing validation check...")
    try:
        offload = PingPongOffload()
        result = offload.validate_no_internal_simulation()
        
        # Ensure the method returns exactly True (not just a truthy value)
        assert result is True
        print("  ✅ Validation check passed")
        return True
    except Exception as e:
        print(f"  ❌ Validation check failed: {e}")
        return False


def test_emit_request():
    """Test that a request can be emitted to a file."""
    print("✓ Testing request emission...")
    try:
        offload = PingPongOffload()
        request_id = offload.emit_request(
            operation="test_emission",
            context="Testing emission functionality",
            parameters={"test": "emission"},
            expected_outcome="Successful file creation",
            priority="standard"
        )
        
        # Check that the output file was created
        assert os.path.exists(offload.output_path)
        
        # Verify the file content
        with open(offload.output_path, 'r') as f:
            data = json.load(f)
        
        assert data["metadata"]["request_id"] == request_id
        assert data["request_details"]["operation"] == "test_emission"
        
        # Clean up the test file
        os.remove(offload.output_path)
        
        print("  ✅ Request emitted successfully to file")
        return True
    except Exception as e:
        print(f"  ❌ Failed to emit request: {e}")
        # Clean up if file exists
        if os.path.exists('pingpong_request_active.json'):
            os.remove('pingpong_request_active.json')
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("🔒 BARROT PING-PONG OFFLOAD PROTOCOL TEST SUITE")
    print("="*70 + "\n")
    
    tests = [
        test_module_import,
        test_template_exists,
        test_template_valid_json,
        test_template_structure,
        test_manifest_exists,
        test_class_initialization,
        test_load_template,
        test_create_request,
        test_constraints_validation,
        test_sacred_protocol_acknowledgment,
        test_validation_check,
        test_emit_request,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test raised unexpected exception: {e}")
            results.append(False)
        print()
    
    # Summary
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"\n📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The Ping-Pong Offload Protocol is working correctly.")
        print("🔒 Protocol compliance verified: No internal simulation detected.")
        print("🧠 Ready to defer to Sean's 22-Agent Entanglement System.")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
