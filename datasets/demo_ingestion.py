#!/usr/bin/env python3
"""
Demonstration of Dataset Ingestion Infrastructure

This script demonstrates how to use the dataset ingestion infrastructure,
including schema validation, data generation, and metadata management.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path


def create_sample_recursive_data():
    """Create sample recursive function data."""
    
    samples = [
        {
            "id": "factorial_001",
            "type": "recursive_function",
            "depth": 10,
            "base_case": {
                "condition": "n == 0",
                "value": "1"
            },
            "recursive_case": {
                "transformation": "n * factorial(n-1)",
                "parameters": ["n"]
            },
            "complexity": {
                "time": "O(n)",
                "space": "O(n)"
            },
            "properties": {
                "associative": False,
                "commutative": False,
                "idempotent": False
            },
            "examples": [
                {"input": 0, "output": 1},
                {"input": 5, "output": 120},
                {"input": 10, "output": 3628800}
            ],
            "source": {
                "origin": "demonstration",
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "dataset": "recursive-functions-demo"
            }
        },
        {
            "id": "fibonacci_001",
            "type": "recursive_function",
            "depth": 15,
            "base_case": {
                "condition": "n <= 1",
                "value": "n"
            },
            "recursive_case": {
                "transformation": "fib(n-1) + fib(n-2)",
                "parameters": ["n"]
            },
            "complexity": {
                "time": "O(2^n)",
                "space": "O(n)"
            },
            "properties": {
                "associative": False,
                "commutative": False,
                "idempotent": False
            },
            "examples": [
                {"input": 0, "output": 0},
                {"input": 1, "output": 1},
                {"input": 10, "output": 55},
                {"input": 15, "output": 610}
            ],
            "source": {
                "origin": "demonstration",
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "dataset": "recursive-functions-demo"
            }
        }
    ]
    
    return samples


def create_sample_permutation_data():
    """Create sample permutation group data."""
    
    samples = [
        {
            "id": "s3_identity",
            "structure_type": "permutation",
            "elements": [1, 2, 3],
            "size": 3,
            "order": 1,
            "generators": [
                {
                    "name": "identity",
                    "representation": [1, 2, 3]
                }
            ],
            "operations": [
                {
                    "name": "composition",
                    "arity": 2,
                    "definition": "function composition"
                }
            ],
            "invariants": {
                "cycle_type": [1, 1, 1],
                "sign": 1,
                "fixed_points": [1, 2, 3]
            },
            "representation": {
                "cycle_notation": "()",
                "one_line": [1, 2, 3]
            },
            "provenance": {
                "source": "demonstration",
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "algorithm": "manual-construction"
            }
        },
        {
            "id": "s3_swap_12",
            "structure_type": "permutation",
            "elements": [1, 2, 3],
            "size": 3,
            "order": 2,
            "generators": [
                {
                    "name": "swap_12",
                    "representation": [2, 1, 3]
                }
            ],
            "operations": [
                {
                    "name": "composition",
                    "arity": 2,
                    "definition": "function composition"
                }
            ],
            "invariants": {
                "cycle_type": [2, 1],
                "sign": -1,
                "fixed_points": [3]
            },
            "representation": {
                "cycle_notation": "(1 2)",
                "one_line": [2, 1, 3]
            },
            "provenance": {
                "source": "demonstration",
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "algorithm": "manual-construction"
            }
        },
        {
            "id": "s3_cycle_123",
            "structure_type": "permutation",
            "elements": [1, 2, 3],
            "size": 3,
            "order": 3,
            "generators": [
                {
                    "name": "cycle_123",
                    "representation": [2, 3, 1]
                }
            ],
            "operations": [
                {
                    "name": "composition",
                    "arity": 2,
                    "definition": "function composition"
                }
            ],
            "invariants": {
                "cycle_type": [3],
                "sign": 1,
                "fixed_points": []
            },
            "representation": {
                "cycle_notation": "(1 2 3)",
                "one_line": [2, 3, 1]
            },
            "provenance": {
                "source": "demonstration",
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "algorithm": "manual-construction"
            }
        }
    ]
    
    return samples


def save_demonstration_data():
    """Save demonstration data to the datasets directory."""
    
    # Create demonstration directories
    demo_dir = Path("datasets/demonstration")
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate and save recursive function samples
    recursive_samples = create_sample_recursive_data()
    recursive_file = demo_dir / "recursive_functions.json"
    with open(recursive_file, 'w') as f:
        json.dump(recursive_samples, f, indent=2)
    print(f"✓ Created {len(recursive_samples)} recursive function samples")
    print(f"  Saved to: {recursive_file}")
    
    # Generate and save permutation samples
    permutation_samples = create_sample_permutation_data()
    permutation_file = demo_dir / "permutations_s3.json"
    with open(permutation_file, 'w') as f:
        json.dump(permutation_samples, f, indent=2)
    print(f"✓ Created {len(permutation_samples)} permutation samples")
    print(f"  Saved to: {permutation_file}")
    
    # Create metadata for demonstration datasets
    metadata = {
        "dataset_id": "demo_permutation_001",
        "name": "Demonstration Dataset - Permutations and Recursion",
        "category": "mathematical",
        "source": {
            "platform": "synthetic-generation",
            "url": "internal-demonstration"
        },
        "ingestion": {
            "first_ingested": datetime.now(timezone.utc).isoformat() + "Z",
            "last_updated": datetime.now(timezone.utc).isoformat() + "Z",
            "frequency": "on-demand",
            "status": "completed"
        },
        "statistics": {
            "record_count": len(recursive_samples) + len(permutation_samples),
            "size_bytes": os.path.getsize(recursive_file) + os.path.getsize(permutation_file),
            "version": "demo-1.0"
        },
        "schema_reference": "recursive_annotation,combinatorial_algebra",
        "quality_metrics": {
            "completeness": 1.0,
            "consistency": 1.0,
            "validation_passed": True
        },
        "tags": ["demonstration", "permutations", "recursion", "symmetric-group"],
        "description": "Demonstration dataset showing recursive functions and permutation group structures"
    }
    
    metadata_file = Path("datasets/metadata") / "demo_dataset.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Created metadata file")
    print(f"  Saved to: {metadata_file}")


def demonstrate_data_access():
    """Demonstrate how to access and use the ingested data."""
    
    print("\n" + "="*60)
    print("Data Access Demonstration")
    print("="*60 + "\n")
    
    # Load and display recursive function data
    recursive_file = Path("datasets/demonstration/recursive_functions.json")
    if recursive_file.exists():
        with open(recursive_file) as f:
            recursive_data = json.load(f)
        
        print("Recursive Function Example:")
        print("-" * 60)
        for func in recursive_data:
            print(f"Function: {func['id']}")
            print(f"  Type: {func['type']}")
            print(f"  Base Case: {func['base_case']['condition']} -> {func['base_case']['value']}")
            print(f"  Recursive: {func['recursive_case']['transformation']}")
            print(f"  Complexity: {func['complexity']['time']} time, {func['complexity']['space']} space")
            print()
    
    # Load and display permutation data
    permutation_file = Path("datasets/demonstration/permutations_s3.json")
    if permutation_file.exists():
        with open(permutation_file) as f:
            permutation_data = json.load(f)
        
        print("Permutation Group Example (S₃):")
        print("-" * 60)
        for perm in permutation_data:
            print(f"Element: {perm['id']}")
            print(f"  Representation: {perm['representation']['one_line']}")
            print(f"  Cycle Notation: {perm['representation']['cycle_notation']}")
            print(f"  Order: {perm['order']}")
            print(f"  Sign: {perm['invariants']['sign']}")
            print(f"  Fixed Points: {perm['invariants']['fixed_points']}")
            print()
    
    # Load and display metadata
    metadata_file = Path("datasets/metadata/demo_dataset.json")
    if metadata_file.exists():
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        print("Dataset Metadata:")
        print("-" * 60)
        print(f"Name: {metadata['name']}")
        print(f"Category: {metadata['category']}")
        print(f"Records: {metadata['statistics']['record_count']}")
        print(f"Status: {metadata['ingestion']['status']}")
        print(f"Tags: {', '.join(metadata['tags'])}")


def main():
    """Main demonstration function."""
    
    print("="*60)
    print("Dataset Ingestion Infrastructure Demonstration")
    print("="*60)
    print()
    
    print("1. Generating Demonstration Data")
    print("-"*60)
    save_demonstration_data()
    
    print("\n2. Accessing and Using Data")
    demonstrate_data_access()
    
    print("\n" + "="*60)
    print("Demonstration Complete!")
    print("="*60)
    print("\nThe following files were created:")
    print("  - datasets/demonstration/recursive_functions.json")
    print("  - datasets/demonstration/permutations_s3.json")
    print("  - datasets/metadata/demo_dataset.json")
    print("\nYou can now:")
    print("  1. View these files to see the data structure")
    print("  2. Use them as templates for your own data")
    print("  3. Validate them against the schemas in datasets/schemas/")
    print("  4. Run the ingestion workflows to get real data")


if __name__ == "__main__":
    main()
