#!/usr/bin/env python3
"""
SHRM v2 Integration Validator

This script validates that the SHRM v2 framework and dataset identification
are properly integrated with existing Barrot capabilities.
"""

import os
import json
import yaml
import sys

# Use script directory as base, or allow override via environment variable
BASE_DIR = os.environ.get('BARROT_BASE_DIR', os.path.dirname(os.path.abspath(__file__)))

def color_print(text, color_code):
    """Print colored text for better visibility"""
    print(f"\033[{color_code}m{text}\033[0m")

def success(text):
    color_print(f"✓ {text}", "92")  # Green

def error(text):
    color_print(f"✗ {text}", "91")  # Red

def warning(text):
    color_print(f"⚠ {text}", "93")  # Yellow

def info(text):
    color_print(f"ℹ {text}", "94")  # Blue

def check_file_exists(filepath, description):
    """Check if a file exists"""
    full_path = os.path.join(BASE_DIR, filepath)
    if os.path.exists(full_path):
        success(f"{description} exists: {filepath}")
        return True
    else:
        error(f"{description} missing: {filepath}")
        return False

def validate_yaml_structure(filepath, required_keys):
    """Validate YAML file structure"""
    full_path = os.path.join(BASE_DIR, filepath)
    try:
        with open(full_path, 'r') as f:
            data = yaml.safe_load(f)
        
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            error(f"Missing keys in {filepath}: {missing_keys}")
            return False
        else:
            success(f"YAML structure valid: {filepath}")
            return True
    except Exception as e:
        error(f"Error parsing YAML {filepath}: {e}")
        return False

def validate_json_structure(filepath, required_keys):
    """Validate JSON file structure"""
    full_path = os.path.join(BASE_DIR, filepath)
    try:
        with open(full_path, 'r') as f:
            data = json.load(f)
        
        # Navigate nested structure for registry
        if isinstance(required_keys, dict):
            for key, nested_keys in required_keys.items():
                if key not in data:
                    error(f"Missing key in {filepath}: {key}")
                    return False
                if nested_keys and not all(nk in data[key] for nk in nested_keys):
                    missing = [nk for nk in nested_keys if nk not in data[key]]
                    error(f"Missing nested keys in {filepath}[{key}]: {missing}")
                    return False
        else:
            missing_keys = [key for key in required_keys if key not in data]
            if missing_keys:
                error(f"Missing keys in {filepath}: {missing_keys}")
                return False
        
        success(f"JSON structure valid: {filepath}")
        return True
    except Exception as e:
        error(f"Error parsing JSON {filepath}: {e}")
        return False

def check_shrm_v2_module():
    """Check if SHRM v2 module is registered"""
    manifest_path = os.path.join(BASE_DIR, "build_manifest.yaml")
    try:
        with open(manifest_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if 'shrm_v2_reasoning' in data.get('modules', []):
            success("SHRM v2 module registered in build_manifest.yaml")
            return True
        else:
            error("SHRM v2 module not found in build_manifest.yaml modules")
            return False
    except Exception as e:
        error(f"Error checking SHRM v2 module: {e}")
        return False

def check_rail_status():
    """Check if SHRM v2 rails are active"""
    manifest_path = os.path.join(BASE_DIR, "build_manifest.yaml")
    try:
        with open(manifest_path, 'r') as f:
            data = yaml.safe_load(f)
        
        rail_status = data.get('rail_status', {})
        shrm_rails = {
            'shrm_v2_contradiction': 'active',
            'shrm_v2_symbolic': 'active',
            'shrm_v2_augmented': 'recursive'
        }
        
        all_valid = True
        for rail, expected_status in shrm_rails.items():
            if rail in rail_status:
                if rail_status[rail] == expected_status:
                    success(f"Rail {rail} is {expected_status}")
                else:
                    warning(f"Rail {rail} status is {rail_status[rail]}, expected {expected_status}")
                    all_valid = False
            else:
                error(f"Rail {rail} not found in rail_status")
                all_valid = False
        
        return all_valid
    except Exception as e:
        error(f"Error checking rail status: {e}")
        return False

def check_protocols_registered():
    """Check if SHRM v2 protocols are registered"""
    registry_path = os.path.join(BASE_DIR, "memory-bundles/protocols/registry.json")
    try:
        with open(registry_path, 'r') as f:
            data = json.load(f)
        
        protocols = data.get('protocols', [])
        shrm_protocols = [
            'SHRM v2 Framework',
            'SHRM v2 Dataset Registry',
            'High-Impact Datasets Identification'
        ]
        
        all_registered = True
        for protocol in shrm_protocols:
            if protocol in protocols:
                success(f"Protocol registered: {protocol}")
            else:
                error(f"Protocol not registered: {protocol}")
                all_registered = False
        
        return all_registered
    except Exception as e:
        error(f"Error checking protocol registration: {e}")
        return False

def check_dataset_count():
    """Check dataset registry has expected number of datasets"""
    registry_path = os.path.join(BASE_DIR, "memory-bundles/protocols/shrm-v2-dataset-registry.json")
    try:
        with open(registry_path, 'r') as f:
            data = json.load(f)
        
        registry = data.get('shrm_v2_dataset_registry', {})
        total = registry.get('total_datasets', 0)
        
        if total >= 60:
            success(f"Dataset registry contains {total} datasets (expected ~63)")
            return True
        else:
            warning(f"Dataset registry contains only {total} datasets (expected ~63)")
            return False
    except Exception as e:
        error(f"Error checking dataset count: {e}")
        return False

def check_category_coverage():
    """Check all three SHRM v2 categories are covered"""
    registry_path = os.path.join(BASE_DIR, "memory-bundles/protocols/shrm-v2-dataset-registry.json")
    try:
        with open(registry_path, 'r') as f:
            data = json.load(f)
        
        categories = data.get('shrm_v2_dataset_registry', {}).get('categories', {})
        required_categories = [
            'contradiction_harvesting',
            'symbolic_reasoning',
            'augmented_cognition'
        ]
        
        all_present = True
        for cat in required_categories:
            if cat in categories:
                count = categories[cat].get('count', 0)
                success(f"Category '{cat}' present with {count} datasets")
            else:
                error(f"Category '{cat}' missing")
                all_present = False
        
        return all_present
    except Exception as e:
        error(f"Error checking category coverage: {e}")
        return False

def check_phase_definitions():
    """Check implementation phases are defined"""
    registry_path = os.path.join(BASE_DIR, "memory-bundles/protocols/shrm-v2-dataset-registry.json")
    try:
        with open(registry_path, 'r') as f:
            data = json.load(f)
        
        phases = data.get('shrm_v2_dataset_registry', {}).get('implementation_phases', [])
        
        if len(phases) == 4:
            success(f"All 4 implementation phases defined")
            for phase in phases:
                phase_num = phase.get('phase')
                focus = phase.get('focus')
                info(f"  Phase {phase_num}: {focus}")
            return True
        else:
            error(f"Expected 4 implementation phases, found {len(phases)}")
            return False
    except Exception as e:
        error(f"Error checking phase definitions: {e}")
        return False

def check_integration_compatibility():
    """Check integration with existing Barrot spells"""
    registry_path = os.path.join(BASE_DIR, "memory-bundles/protocols/shrm-v2-dataset-registry.json")
    try:
        with open(registry_path, 'r') as f:
            data = json.load(f)
        
        integration = data.get('shrm_v2_dataset_registry', {}).get('integration_protocols', {})
        
        expected_compatible = {
            'omega_ingest_compatible': True,
            'keyseer_insight_compatible': True,
            'prediction_methodologies_compatible': True,
            'microagent_logic_compatible': True
        }
        
        all_compatible = True
        for key, expected in expected_compatible.items():
            if integration.get(key) == expected:
                success(f"Integration compatible: {key}")
            else:
                error(f"Integration not compatible: {key}")
                all_compatible = False
        
        return all_compatible
    except Exception as e:
        error(f"Error checking integration compatibility: {e}")
        return False

def check_directives_updated():
    """Check if SHRM v2 directives are added to build manifest"""
    manifest_path = os.path.join(BASE_DIR, "build_manifest.yaml")
    try:
        with open(manifest_path, 'r') as f:
            data = yaml.safe_load(f)
        
        directives = data.get('roadmap_ingestion', {}).get('directives', [])
        shrm_keywords = ['SHRM', 'contradiction', 'symbolic', 'augmented cognition']
        
        shrm_directive_found = False
        for directive in directives:
            if any(keyword.lower() in directive.lower() for keyword in shrm_keywords):
                shrm_directive_found = True
                info(f"  Found directive: {directive}")
        
        if shrm_directive_found:
            success("SHRM v2 directives found in build manifest")
            return True
        else:
            warning("No SHRM v2-specific directives found in build manifest")
            return False
    except Exception as e:
        error(f"Error checking directives: {e}")
        return False

def main():
    """Run all validation checks"""
    print("="*70)
    info("SHRM v2 INTEGRATION VALIDATION")
    print("="*70)
    
    checks = []
    
    # File existence checks
    info("\n1. Checking file existence...")
    checks.append(check_file_exists(
        "memory-bundles/protocols/shrm-v2-framework.md",
        "SHRM v2 Framework documentation"
    ))
    checks.append(check_file_exists(
        "memory-bundles/protocols/high-impact-datasets.md",
        "High-Impact Datasets documentation"
    ))
    checks.append(check_file_exists(
        "memory-bundles/protocols/shrm-v2-dataset-registry.json",
        "SHRM v2 Dataset Registry"
    ))
    checks.append(check_file_exists(
        "memory-bundles/protocols/dataset-acquisition-guide.md",
        "Dataset Acquisition Guide"
    ))
    
    # Structure validation
    info("\n2. Checking file structures...")
    checks.append(validate_yaml_structure(
        "build_manifest.yaml",
        ['build_signature', 'modules', 'resources', 'rail_status']
    ))
    checks.append(validate_json_structure(
        "memory-bundles/protocols/shrm-v2-dataset-registry.json",
        {'shrm_v2_dataset_registry': ['version', 'categories', 'implementation_phases']}
    ))
    
    # Integration checks
    info("\n3. Checking SHRM v2 module integration...")
    checks.append(check_shrm_v2_module())
    checks.append(check_rail_status())
    checks.append(check_protocols_registered())
    
    # Content validation
    info("\n4. Validating dataset registry content...")
    checks.append(check_dataset_count())
    checks.append(check_category_coverage())
    checks.append(check_phase_definitions())
    
    # Compatibility checks
    info("\n5. Checking compatibility with existing systems...")
    checks.append(check_integration_compatibility())
    checks.append(check_directives_updated())
    
    # Summary
    print("\n" + "="*70)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        success(f"\nALL CHECKS PASSED: {passed}/{total}")
        print("="*70)
        info("\nSHRM v2 framework is properly integrated with Barrot-Agent!")
        info("Next steps:")
        info("  1. Begin Phase 1 dataset acquisition")
        info("  2. Implement SHRM v2 reasoning modules")
        info("  3. Set up evaluation metrics tracking")
        return 0
    else:
        error(f"\nSOME CHECKS FAILED: {passed}/{total} passed")
        print("="*70)
        warning("\nPlease address the failed checks before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
