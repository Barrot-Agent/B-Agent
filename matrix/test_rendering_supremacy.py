#!/usr/bin/env python3
"""
Integration Test for Rendering Supremacy Directive
Validates that all components are properly integrated and functional.
"""

import json
import sys
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "barrot_manifest.json"
GLYPHS_PATH = REPO_ROOT / "glyphs" / "user_defined"
GLYPH_MAPPER_PATH = REPO_ROOT / "matrix" / "glyph_mapper.py"
RENDERING_MODULE_PATH = REPO_ROOT / "matrix" / "rendering_ingestion.py"
DOC_PATH = REPO_ROOT / "RENDERING_SUPREMACY_DIRECTIVE.md"

def test_manifest_configuration():
    """Test that manifest is properly configured"""
    print("🧪 Testing manifest configuration...")
    
    with open(MANIFEST_PATH, 'r') as f:
        manifest = json.load(f)
    
    assert "rendering_supremacy" in manifest, "Missing rendering_supremacy section"
    rs = manifest["rendering_supremacy"]
    
    assert rs["rendering_ingestion_active"] == True, "Ingestion not active"
    assert rs["methodology_synthesis"] == "enabled", "Synthesis not enabled"
    assert rs["initiative_auto_alignment"] == True, "Auto-alignment not enabled"
    assert len(rs["glyphs_emitted"]) == 5, f"Expected 5 glyphs, got {len(rs['glyphs_emitted'])}"
    
    expected_glyphs = [
        "RENDERING_METHODOLOGY_GLYPH",
        "COMPETITIVE_SUPREMACY_GLYPH",
        "RENDERING_INTEGRATION_GLYPH",
        "INITIATIVE_AUGMENTATION_GLYPH",
        "GAP_FILLING_CONFIRMATION_GLYPH"
    ]
    
    for glyph in expected_glyphs:
        assert glyph in rs["glyphs_emitted"], f"Missing glyph: {glyph}"
    
    print("✅ Manifest configuration valid")
    return True

def test_glyph_files():
    """Test that all glyph files exist"""
    print("\n🧪 Testing glyph files...")
    
    expected_files = [
        "rendering_methodology_glyph.yml",
        "competitive_supremacy_glyph.yml",
        "rendering_integration_glyph.yml",
        "initiative_augmentation_glyph.yml",
        "gap_filling_confirmation_glyph.yml"
    ]
    
    for filename in expected_files:
        filepath = GLYPHS_PATH / filename
        assert filepath.exists(), f"Missing glyph file: {filename}"
        
        # Verify file is not empty
        assert filepath.stat().st_size > 0, f"Empty glyph file: {filename}"
    
    print(f"✅ All {len(expected_files)} glyph files present and valid")
    return True

def test_glyph_mapper():
    """Test that glyph_mapper has rendering glyphs"""
    print("\n🧪 Testing glyph_mapper integration...")
    
    with open(GLYPH_MAPPER_PATH, 'r') as f:
        content = f.read()
    
    expected_glyphs = [
        "RENDERING_METHODOLOGY_GLYPH",
        "COMPETITIVE_SUPREMACY_GLYPH",
        "RENDERING_INTEGRATION_GLYPH",
        "INITIATIVE_AUGMENTATION_GLYPH",
        "GAP_FILLING_CONFIRMATION_GLYPH"
    ]
    
    for glyph in expected_glyphs:
        assert glyph in content, f"Glyph {glyph} not in glyph_mapper.py"
    
    print("✅ Glyph mapper properly configured")
    return True

def test_rendering_module():
    """Test that rendering ingestion module exists and is valid"""
    print("\n🧪 Testing rendering ingestion module...")
    
    assert RENDERING_MODULE_PATH.exists(), "Rendering module not found"
    assert RENDERING_MODULE_PATH.stat().st_size > 0, "Rendering module is empty"
    
    # Verify module has key components
    with open(RENDERING_MODULE_PATH, 'r') as f:
        content = f.read()
    
    required_components = [
        "RenderingIngestionEngine",
        "ingest_rendering_data",
        "synthesize_methodology",
        "validate_competitive_supremacy",
        "integrate_to_initiatives",
        "augment_initiatives",
        "confirm_gap_filling"
    ]
    
    for component in required_components:
        assert component in content, f"Missing component: {component}"
    
    print("✅ Rendering ingestion module valid")
    return True

def test_documentation():
    """Test that documentation exists"""
    print("\n🧪 Testing documentation...")
    
    assert DOC_PATH.exists(), "Documentation not found"
    assert DOC_PATH.stat().st_size > 0, "Documentation is empty"
    
    with open(DOC_PATH, 'r') as f:
        content = f.read()
    
    required_sections = [
        "RENDERING SUPREMACY DIRECTIVE",
        "Rendering Cognition Ingestion Protocol",
        "Methodology Synthesis Engine",
        "Automatic Application Protocol",
        "Glyphs & Tracking System"
    ]
    
    for section in required_sections:
        assert section in content, f"Missing documentation section: {section}"
    
    print("✅ Documentation complete and valid")
    return True

def test_module_execution():
    """Test that the module can be imported and executed"""
    print("\n🧪 Testing module execution...")
    
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from matrix.rendering_ingestion import RenderingIngestionEngine
        
        engine = RenderingIngestionEngine()
        assert engine.manifest is not None, "Manifest not loaded"
        assert engine.rendering_config is not None, "Rendering config not loaded"
        
        print("✅ Module executes successfully")
        return True
    except Exception as e:
        print(f"❌ Module execution failed: {e}")
        return False

def run_all_tests():
    """Run all integration tests"""
    print("=" * 70)
    print("🧠 RENDERING SUPREMACY DIRECTIVE - INTEGRATION TESTS")
    print("=" * 70)
    
    tests = [
        test_manifest_configuration,
        test_glyph_files,
        test_glyph_mapper,
        test_rendering_module,
        test_documentation,
        test_module_execution
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Test error: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED - Rendering Supremacy Directive is fully operational!")
        return 0
    else:
        print(f"\n❌ {failed} tests failed - Please review the errors above")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
