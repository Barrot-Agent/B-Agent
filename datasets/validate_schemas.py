#!/usr/bin/env python3
"""
Schema Validator and Usage Examples

This script validates the JSON schemas and provides examples of their usage.
"""

import json
from pathlib import Path
from typing import Dict, Any


def load_schema(schema_name: str) -> Dict[str, Any]:
    """Load a JSON schema from the schemas directory."""
    schema_path = Path('datasets/schemas') / f'{schema_name}.json'
    with open(schema_path, 'r') as f:
        return json.load(f)


def validate_schemas():
    """Validate all JSON schemas."""
    schemas_dir = Path('datasets/schemas')
    
    if not schemas_dir.exists():
        print("Error: schemas directory not found")
        return False
    
    schemas = ['recursive_annotation', 'combinatorial_algebra', 'dataset_metadata']
    all_valid = True
    
    for schema_name in schemas:
        try:
            schema = load_schema(schema_name)
            # Check required fields in schema definition
            assert '$schema' in schema, "Missing $schema field"
            assert 'title' in schema, "Missing title field"
            assert 'type' in schema, "Missing type field"
            assert 'properties' in schema, "Missing properties field"
            
            print(f"✓ {schema_name}.json is valid")
        except Exception as e:
            print(f"✗ {schema_name}.json is invalid: {e}")
            all_valid = False
    
    return all_valid


def example_recursive_annotation():
    """Example of a recursive annotation."""
    return {
        "id": "fib_001",
        "type": "recursive_function",
        "depth": 5,
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
            {"input": 5, "output": 5},
            {"input": 10, "output": 55}
        ],
        "source": {
            "origin": "classic-algorithms",
            "timestamp": "2025-12-20T00:00:00Z",
            "dataset": "recursive-functions"
        }
    }


def example_combinatorial_algebra():
    """Example of a combinatorial algebra structure."""
    return {
        "id": "perm_s3_001",
        "structure_type": "permutation",
        "elements": [1, 2, 3],
        "size": 3,
        "order": 6,
        "generators": [
            {
                "name": "swap_12",
                "representation": [2, 1, 3]
            },
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
            "cycle_type": [1, 2],
            "sign": 1,
            "fixed_points": [3]
        },
        "representation": {
            "cycle_notation": "(1 2)",
            "one_line": [2, 1, 3]
        },
        "provenance": {
            "source": "symmetric-group-library",
            "timestamp": "2025-12-20T00:00:00Z",
            "algorithm": "cayley-table-generation"
        }
    }


def example_dataset_metadata():
    """Example of dataset metadata."""
    return {
        "dataset_id": "kaggle_combinatorics_001",
        "name": "Combinatorial Structures Dataset",
        "category": "mathematical",
        "source": {
            "platform": "kaggle",
            "url": "https://kaggle.com/datasets/combinatorial-structures",
            "api_endpoint": "https://www.kaggle.com/api/v1/datasets/download"
        },
        "ingestion": {
            "first_ingested": "2025-12-01T00:00:00Z",
            "last_updated": "2025-12-20T00:00:00Z",
            "frequency": "monthly",
            "status": "active"
        },
        "statistics": {
            "record_count": 10000,
            "size_bytes": 5242880,
            "version": "1.0"
        },
        "schema_reference": "combinatorial_algebra",
        "quality_metrics": {
            "completeness": 0.98,
            "consistency": 0.95,
            "validation_passed": True
        },
        "tags": ["combinatorics", "algebra", "permutations"],
        "description": "A comprehensive dataset of combinatorial algebraic structures"
    }


def main():
    """Main function to run validation and examples."""
    print("=" * 60)
    print("Schema Validation and Examples")
    print("=" * 60)
    print()
    
    # Validate schemas
    print("Validating JSON Schemas...")
    print("-" * 60)
    if validate_schemas():
        print("\n✓ All schemas are valid!\n")
    else:
        print("\n✗ Some schemas are invalid\n")
        return 1
    
    # Show examples
    print("=" * 60)
    print("Example Data Structures")
    print("=" * 60)
    
    print("\n1. Recursive Annotation Example:")
    print("-" * 60)
    rec_example = example_recursive_annotation()
    print(json.dumps(rec_example, indent=2))
    
    print("\n2. Combinatorial Algebra Example:")
    print("-" * 60)
    comb_example = example_combinatorial_algebra()
    print(json.dumps(comb_example, indent=2))
    
    print("\n3. Dataset Metadata Example:")
    print("-" * 60)
    meta_example = example_dataset_metadata()
    print(json.dumps(meta_example, indent=2))
    
    print("\n" + "=" * 60)
    print("Validation and examples completed successfully!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
