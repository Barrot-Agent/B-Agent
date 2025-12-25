# Datasets Directory

This directory contains ingested datasets and tools for enhancing Barrot's permutation capabilities and processes.

## Directory Structure

```
datasets/
├── mathematical/          # Mathematical and logical datasets
│   ├── kaggle/           # Datasets from Kaggle
│   └── public-apis/      # Data from public APIs
├── programming-libraries/ # Programming libraries for permutations
│   └── github/           # Libraries from GitHub
├── ml-training/          # Machine learning training datasets
│   ├── optimization/     # Optimization problem datasets
│   └── benchmarks/       # Benchmark datasets
├── quantum/              # Quantum computing libraries and algorithms
├── schemas/              # Data annotation schemas
│   ├── recursive_annotation.json
│   ├── combinatorial_algebra.json
│   └── dataset_metadata.json
├── metadata/             # Metadata for ingested datasets
├── reports/              # Ingestion status reports
└── sources_config.yaml   # Configuration for data sources
```

## Data Categories

### 1. Mathematical & Logical Data
- **Combinatorial Algebra**: Group theory structures, permutation groups
- **Recursive Functions**: Patterns and algorithms for recursive computation
- **Advanced Group Theories**: Algebraic structures and transformations

### 2. Programming Libraries
- **Python Libraries**: itertools, more-itertools, sympy combinatorics
- **Permutation Algorithms**: Open-source implementations from GitHub
- **Combinatorial Tools**: Libraries for working with permutations and combinations

### 3. Machine Learning Training Data
- **Optimization Problems**: TSP, VRP, Job Shop Scheduling
- **Permutation Learning**: Benchmarks for permutation-based ML
- **Synthetic Datasets**: Generated training data for optimization

### 4. Quantum Computing Libraries
- **Qiskit**: IBM's quantum computing framework
- **Cirq**: Google's quantum computing library
- **PennyLane**: Quantum machine learning library
- **Algorithm Catalogs**: Quantum algorithms for combinatorial problems

## Data Schemas

### Recursive Annotation Schema
Defines the structure for annotating recursive patterns and functions:
- Recursion depth tracking
- Base and recursive case definitions
- Complexity analysis
- Mathematical properties (associative, commutative, idempotent)

### Combinatorial Algebra Schema
Structures for combinatorial and algebraic data:
- Permutation groups and structures
- Generators and operations
- Cycle notation and matrix representations
- Algebraic invariants

### Dataset Metadata Schema
Tracks metadata for all ingested datasets:
- Source information (platform, URL, API endpoints)
- Ingestion schedule and status
- Quality metrics
- Version tracking

## Automated Ingestion

Data ingestion is automated through GitHub Actions workflows:

### Workflows
1. **ingest-kaggle-datasets.yml**: Monthly ingestion from Kaggle (1st of month)
2. **ingest-github-libraries.yml**: Weekly ingestion of GitHub libraries (Sundays)
3. **ingest-ml-training-data.yml**: Weekly ML dataset generation (Mondays)
4. **ingest-quantum-libraries.yml**: Monthly quantum library updates (15th of month)
5. **master-ingestion-pipeline.yml**: Coordinates all ingestion workflows daily

### Configuration
All data sources are configured in `sources_config.yaml`, which defines:
- Dataset identifiers and locations
- Ingestion frequency and priority
- Tags and categorization
- Quality assurance settings

## Data Quality

All ingested data undergoes quality checks:
- **Schema Validation**: Ensures data conforms to defined schemas
- **Completeness Check**: Verifies all required fields are present
- **Duplicate Detection**: Identifies and removes duplicate entries
- **Format Verification**: Validates data format consistency

## Usage

### Accessing Datasets
Datasets are organized by category and can be accessed programmatically:

```python
import json
from pathlib import Path

# Load metadata
metadata_dir = Path('datasets/metadata')
with open(metadata_dir / 'kaggle_ingestion.json') as f:
    kaggle_data = json.load(f)

# Load ML training data
with open('datasets/ml-training/optimization/tsp_instances.json') as f:
    tsp_instances = json.load(f)
```

### Using Schemas
Validate data against schemas:

```python
import json
import jsonschema

# Load schema
with open('datasets/schemas/recursive_annotation.json') as f:
    schema = json.load(f)

# Validate data
jsonschema.validate(instance=your_data, schema=schema)
```

## Continuous Updates

The ingestion pipeline runs continuously to keep datasets up-to-date:
- **Daily**: Master pipeline checks what needs to run
- **Weekly**: GitHub libraries and ML training data
- **Monthly**: Kaggle datasets and quantum libraries

## Integration with Barrot

These datasets enhance Barrot's capabilities in:
- **Cognitive Recursion**: Understanding and applying recursive patterns
- **Advanced Combinations**: Working with complex combinatorial structures
- **Permutation Processing**: Efficiently handling permutation operations
- **Optimization**: Solving combinatorial optimization problems
- **Quantum Computing**: Leveraging quantum algorithms for permutations

## Contributing

To add new data sources:
1. Update `sources_config.yaml` with the new source
2. Create or modify the appropriate workflow in `.github/workflows/`
3. Ensure the data conforms to existing schemas or create a new schema
4. Test the ingestion process
5. Update this README

## License

Datasets are ingested from public sources and subject to their respective licenses. Always check source licenses before use.
