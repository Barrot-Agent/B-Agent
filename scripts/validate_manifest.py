#!/usr/bin/env python3
"""
Build Manifest Validator

This script validates the build_manifest.yaml file to ensure it meets
the required structure and contains valid data.
"""
import sys
import yaml
from datetime import datetime


def load_manifest(manifest_path='build_manifest.yaml'):
    """Load and parse the manifest file"""
    try:
        with open(manifest_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Error: Manifest file '{manifest_path}' not found")
        return None
    except yaml.YAMLError as e:
        print(f"❌ Error: Invalid YAML in manifest: {e}")
        return None


def validate_required_fields(manifest):
    """Validate that all required fields are present"""
    required_fields = ['build_signature', 'timestamp', 'modules', 'rail_status']
    errors = []
    
    for field in required_fields:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")
    
    return errors


def validate_build_signature(manifest):
    """Validate build signature format"""
    errors = []
    signature = manifest.get('build_signature')
    
    if not isinstance(signature, str):
        errors.append("build_signature must be a string")
    elif not signature.startswith('BNDL-'):
        errors.append("build_signature must start with 'BNDL-'")
    
    return errors


def validate_timestamp(manifest):
    """Validate timestamp format"""
    errors = []
    timestamp = manifest.get('timestamp')
    
    # Convert to string for validation
    timestamp_str = str(timestamp)
    
    try:
        datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except ValueError:
        errors.append(f"Invalid timestamp format: {timestamp_str} (expected ISO 8601)")
    
    return errors


def validate_modules(manifest):
    """Validate modules list"""
    errors = []
    modules = manifest.get('modules')
    
    if not isinstance(modules, list):
        errors.append("modules must be a list")
    elif len(modules) == 0:
        errors.append("modules list is empty")
    
    return errors


def validate_rail_status(manifest):
    """Validate rail status dictionary"""
    errors = []
    rail_status = manifest.get('rail_status')
    
    if not isinstance(rail_status, dict):
        errors.append("rail_status must be a dictionary")
    elif len(rail_status) == 0:
        errors.append("rail_status is empty")
    else:
        # Canonical lowercase status values
        valid_statuses = [
            'active',
            'stable',
            'recursive',
            'evolving',
            'publishing',
            'initializing',
            'developing',
            'operational',
        ]
        
        for rail, status in rail_status.items():
            # Normalize to lowercase for comparison
            normalized_status = str(status).lower()
            if normalized_status not in valid_statuses:
                errors.append(f"Invalid status '{status}' for rail '{rail}'")
    
    return errors


def validate_optional_fields(manifest):
    """Validate optional fields if present"""
    errors = []
    
    if 'resources' in manifest:
        if not isinstance(manifest['resources'], list):
            errors.append("resources must be a list")
    
    if 'capabilities' in manifest:
        if not isinstance(manifest['capabilities'], list):
            errors.append("capabilities must be a list")
    
    if 'platforms' in manifest:
        if not isinstance(manifest['platforms'], list):
            errors.append("platforms must be a list")
    
    return errors


def main():
    """Main validation function"""
    print("🔍 Validating build_manifest.yaml...")
    print()
    
    # Load manifest
    manifest = load_manifest()
    if manifest is None:
        return 1
    
    # Run all validations
    all_errors = []
    all_errors.extend(validate_required_fields(manifest))
    all_errors.extend(validate_build_signature(manifest))
    all_errors.extend(validate_timestamp(manifest))
    all_errors.extend(validate_modules(manifest))
    all_errors.extend(validate_rail_status(manifest))
    all_errors.extend(validate_optional_fields(manifest))
    
    # Report results
    if all_errors:
        print("❌ Validation failed with the following errors:")
        for error in all_errors:
            print(f"  • {error}")
        print()
        return 1
    else:
        print("✅ Manifest validation passed!")
        print()
        print("Summary:")
        print(f"  • Build Signature: {manifest['build_signature']}")
        print(f"  • Timestamp: {manifest['timestamp']}")
        print(f"  • Modules: {len(manifest['modules'])} configured")
        print(f"  • Rails: {len(manifest['rail_status'])} active")
        if 'resources' in manifest:
            print(f"  • Resources: {len(manifest['resources'])} available")
        if 'capabilities' in manifest:
            print(f"  • Capabilities: {len(manifest['capabilities'])} enabled")
        print()
        return 0


if __name__ == '__main__':
    sys.exit(main())
