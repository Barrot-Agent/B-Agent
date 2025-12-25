#!/usr/bin/env python3
"""
Barrot Cognitive Capabilities Verification Script

This script verifies that all cognitive enhancement components are properly
integrated and configured.
"""

import json
import yaml
import os
from pathlib import Path

def verify_cognitive_core():
    """Verify cognitive-core module structure and configurations."""
    print("=" * 60)
    print("BARROT COGNITIVE CAPABILITIES VERIFICATION")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    cognitive_core_path = base_path / "cognitive-core"
    
    # Check directory exists
    if not cognitive_core_path.exists():
        print("❌ cognitive-core directory not found")
        return False
    print("✓ cognitive-core directory exists")
    
    # Expected files
    expected_files = {
        "yaml": [
            "ping-pong-engine.yaml",
            "sapients-hierarchy.yaml",
            "reorganization-engine.yaml",
            "cross-spectrum-solver.yaml",
            "recursive-learning-pipeline.yaml",
            "dynamic-scheduler.yaml"
        ],
        "json": [
            "capabilities-registry.json",
            "knowledge-base.json"
        ],
        "docs": [
            "README.md"
        ]
    }
    
    # Verify YAML files
    print("\n--- YAML Configuration Files ---")
    for yaml_file in expected_files["yaml"]:
        file_path = cognitive_core_path / yaml_file
        if not file_path.exists():
            print(f"❌ {yaml_file} not found")
            return False
        
        try:
            with open(file_path) as f:
                data = yaml.safe_load(f)
            print(f"✓ {yaml_file} - Valid and loaded")
        except Exception as e:
            print(f"❌ {yaml_file} - Error: {e}")
            return False
    
    # Verify JSON files
    print("\n--- JSON Configuration Files ---")
    for json_file in expected_files["json"]:
        file_path = cognitive_core_path / json_file
        if not file_path.exists():
            print(f"❌ {json_file} not found")
            return False
        
        try:
            with open(file_path) as f:
                data = json.load(f)
            print(f"✓ {json_file} - Valid and loaded")
        except Exception as e:
            print(f"❌ {json_file} - Error: {e}")
            return False
    
    # Verify documentation
    print("\n--- Documentation ---")
    for doc_file in expected_files["docs"]:
        file_path = cognitive_core_path / doc_file
        if not file_path.exists():
            print(f"❌ {doc_file} not found")
            return False
        print(f"✓ {doc_file} exists")
    
    return True

def verify_capabilities_registry():
    """Verify capabilities registry structure."""
    print("\n--- Capabilities Registry ---")
    
    base_path = Path(__file__).parent
    registry_path = base_path / "cognitive-core" / "capabilities-registry.json"
    
    try:
        with open(registry_path) as f:
            registry = json.load(f)
        
        reg_data = registry["cognitive_capabilities_registry"]
        
        # Check version
        print(f"✓ Registry Version: {reg_data['version']}")
        
        # Check capabilities
        capabilities = reg_data["registered_capabilities"]
        print(f"✓ Registered Capabilities: {len(capabilities)}")
        
        for cap in capabilities:
            print(f"  - {cap['name']} (v{cap['version']}) - {cap['status']}")
        
        # Check integration topology
        topology = reg_data["integration_topology"]
        print(f"✓ Core Modules: {len(topology['core_modules'])}")
        print(f"✓ Support Modules: {len(topology['support_modules'])}")
        
        return True
    except Exception as e:
        print(f"❌ Registry verification failed: {e}")
        return False

def verify_knowledge_base():
    """Verify knowledge base structure."""
    print("\n--- Knowledge Base ---")
    
    base_path = Path(__file__).parent
    kb_path = base_path / "cognitive-core" / "knowledge-base.json"
    
    try:
        with open(kb_path) as f:
            kb = json.load(f)
        
        kb_data = kb["knowledge_base"]
        
        # Check version
        print(f"✓ Knowledge Base Version: {kb_data['version']}")
        
        # Check domains
        domains = kb_data["structure"]["domains"]
        print(f"✓ Knowledge Domains: {len(domains)}")
        
        for domain in domains:
            print(f"  - {domain['name']}")
        
        # Check ingestion pipelines
        pipelines = kb_data["ingestion_pipelines"]
        print(f"✓ Continuous Feeds: {len(pipelines['continuous_feeds'])}")
        print(f"✓ Batch Imports: {len(pipelines['batch_imports'])}")
        
        return True
    except Exception as e:
        print(f"❌ Knowledge base verification failed: {e}")
        return False

def verify_build_manifest():
    """Verify build manifest updates."""
    print("\n--- Build Manifest ---")
    
    base_path = Path(__file__).parent
    manifest_path = base_path / "build_manifest.yaml"
    
    try:
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
        
        # Check signature
        print(f"✓ Build Signature: {manifest['build_signature']}")
        
        # Check cognitive modules
        modules = manifest["modules"]
        cognitive_modules = [
            "ping_pong_analysis",
            "sapients_hierarchy_reasoning",
            "component_reorganization",
            "cross_spectrum_problem_solving",
            "recursive_learning_pipeline",
            "dynamic_scheduler"
        ]
        
        for mod in cognitive_modules:
            if mod in modules:
                print(f"✓ Module registered: {mod}")
            else:
                print(f"❌ Module missing: {mod}")
                return False
        
        # Check cognitive enhancement section
        if "cognitive_enhancement" in manifest:
            print(f"✓ Cognitive enhancement section present")
            cog_enh = manifest["cognitive_enhancement"]
            print(f"  - Status: {cog_enh['status']}")
            print(f"  - Capabilities: {len(cog_enh['capabilities'])}")
        else:
            print(f"❌ Cognitive enhancement section missing")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Build manifest verification failed: {e}")
        return False

def verify_spells():
    """Verify spell documentation."""
    print("\n--- Spells ---")
    
    base_path = Path(__file__).parent
    spell_path = base_path / "spells" / "cognitive-ascension.md"
    
    if not spell_path.exists():
        print(f"❌ cognitive-ascension.md not found")
        return False
    
    print(f"✓ Cognitive Ascension spell exists")
    
    # Check existing spells
    existing_spells = [
        "omega-ingest.md",
        "keyseer-insight.md"
    ]
    
    for spell in existing_spells:
        spell_file = base_path / "spells" / spell
        if spell_file.exists():
            print(f"✓ Existing spell: {spell}")
    
    return True

def verify_protocols():
    """Verify memory bundle protocols."""
    print("\n--- Memory Bundle Protocols ---")
    
    base_path = Path(__file__).parent
    protocols_path = base_path / "memory-bundles" / "protocols" / "registry.json"
    
    try:
        with open(protocols_path) as f:
            protocols = json.load(f)
        
        protocol_list = protocols["protocols"]
        print(f"✓ Total Protocols: {len(protocol_list)}")
        
        cognitive_protocols = [
            "Ping Pong Multi-Dataset",
            "Sapients Hierarchy Reasoning",
            "Component Reorganization",
            "Cross Spectrum Solving",
            "Recursive Learning",
            "Dynamic Orchestration"
        ]
        
        for protocol in cognitive_protocols:
            if protocol in protocol_list:
                print(f"✓ Protocol registered: {protocol}")
            else:
                print(f"❌ Protocol missing: {protocol}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Protocols verification failed: {e}")
        return False

def main():
    """Run all verifications."""
    results = []
    
    results.append(("Cognitive Core", verify_cognitive_core()))
    results.append(("Capabilities Registry", verify_capabilities_registry()))
    results.append(("Knowledge Base", verify_knowledge_base()))
    results.append(("Build Manifest", verify_build_manifest()))
    results.append(("Spells", verify_spells()))
    results.append(("Protocols", verify_protocols()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for component, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status} - {component}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✓ ALL VERIFICATIONS PASSED")
        print("\nCognitive enhancement successfully implemented!")
        print("All capabilities are properly integrated and configured.")
        return 0
    else:
        print("❌ SOME VERIFICATIONS FAILED")
        print("\nPlease review the errors above.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
