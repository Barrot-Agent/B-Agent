# Quick Start Guide: Dataset Ingestion Workflows

## Overview
This guide provides quick instructions for using the automated dataset ingestion workflows.

## Prerequisites

### Required Secrets
Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

1. **KAGGLE_USERNAME** - Your Kaggle username
2. **KAGGLE_KEY** - Your Kaggle API key (from Kaggle → Account → API → Create New API Token)

Note: `GITHUB_TOKEN` is automatically provided by GitHub Actions.

## Manual Workflow Triggers

### Using GitHub UI
1. Go to **Actions** tab in your repository
2. Select the workflow you want to run
3. Click **Run workflow** button
4. Select branch (usually `main`)
5. Click **Run workflow**

### Using GitHub CLI
```bash
# Master pipeline (coordinates all workflows)
gh workflow run master-ingestion-pipeline.yml -f force_all=true

# Individual workflows
gh workflow run ingest-kaggle-datasets.yml
gh workflow run ingest-github-libraries.yml
gh workflow run ingest-ml-training-data.yml
gh workflow run ingest-quantum-libraries.yml
```

## Automatic Schedules

Workflows run automatically on these schedules:

| Workflow | Schedule | Description |
|----------|----------|-------------|
| Master Pipeline | Daily at 01:00 UTC | Coordinates all workflows |
| Kaggle Datasets | Monthly (1st) at 00:00 UTC | Ingests Kaggle datasets |
| GitHub Libraries | Weekly (Sundays) at 02:00 UTC | Tracks GitHub libraries |
| ML Training Data | Weekly (Mondays) at 03:00 UTC | Generates training data |
| Quantum Libraries | Monthly (15th) at 04:00 UTC | Tracks quantum libraries |

## Local Testing

### Validate Schemas
```bash
cd /home/runner/work/Barrot-Agent/Barrot-Agent
python datasets/validate_schemas.py
```

### Run Demonstration
```bash
python datasets/demo_ingestion.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Checking Ingestion Status

### View Status Reports
Status reports are generated daily in: `datasets/reports/ingestion_status.md`

### View Metadata Files
Metadata for ingested datasets is stored in: `datasets/metadata/`

Files:
- `kaggle_ingestion.json` - Kaggle datasets metadata
- `github_libraries.json` - GitHub library metadata
- `algorithm_search.json` - Algorithm repository search results
- `ml_training.json` - ML training dataset metadata
- `quantum_libraries.json` - Quantum library metadata
- `demo_dataset.json` - Demonstration dataset metadata (if generated)

### Check Workflow Logs
1. Go to **Actions** tab in GitHub
2. Click on the workflow run you want to inspect
3. Click on the job name to see detailed logs
4. Expand steps to see specific output

## Data Access

### Python Example
```python
import json
from pathlib import Path

# Load Kaggle dataset metadata
with open('datasets/metadata/kaggle_ingestion.json') as f:
    kaggle_data = json.load(f)
    print(f"Datasets: {len(kaggle_data['datasets'])}")

# Load GitHub library metadata
with open('datasets/metadata/github_libraries.json') as f:
    github_data = json.load(f)
    for lib in github_data['libraries']:
        print(f"Library: {lib['name']} - Stars: {lib['stars']}")

# Load ML training data
with open('datasets/ml-training/optimization/tsp_instances.json') as f:
    tsp_data = json.load(f)
    print(f"TSP instances: {len(tsp_data)}")
```

### Command Line
```bash
# View metadata files
cat datasets/metadata/github_libraries.json | jq '.libraries[] | {name, stars, url}'

# Count records in datasets
find datasets/ -name "*.json" -type f | wc -l

# View ingestion reports
cat datasets/reports/ingestion_status.md
```

## Customization

### Adding New Data Sources
1. Edit `datasets/sources_config.yaml`
2. Add your data source under the appropriate category
3. Create or modify workflow to handle the new source
4. Test the ingestion process

### Modifying Schedules
Edit the cron schedule in the workflow file:
```yaml
on:
  schedule:
    - cron: '0 2 * * 1'  # Every Monday at 02:00 UTC
```

Cron format: `minute hour day-of-month month day-of-week`

Examples:
- `0 0 * * *` - Daily at midnight
- `0 0 * * 0` - Weekly on Sunday
- `0 0 1 * *` - Monthly on the 1st
- `0 */6 * * *` - Every 6 hours

### Creating Custom Schemas
1. Create new JSON schema in `datasets/schemas/`
2. Follow JSON Schema Draft 07 specification
3. Add validation in `datasets/validate_schemas.py`
4. Reference in `datasets/sources_config.yaml`

## Troubleshooting

### Workflow Fails to Run
- Check if secrets are properly configured
- Verify API rate limits not exceeded
- Check workflow syntax with YAML validator
- Review GitHub Actions logs for errors

### Data Not Ingested
- Verify data source is accessible
- Check API credentials are valid
- Ensure network connectivity
- Review error messages in workflow logs

### Schema Validation Errors
- Run `python datasets/validate_schemas.py` locally
- Check JSON syntax
- Verify all required fields are present
- Ensure data types match schema

### Permission Errors
- Verify workflow has `contents: write` permission
- Check repository settings allow workflow to write
- Ensure branch protection rules don't block commits

## Best Practices

1. **Test Locally First**: Always test changes locally before pushing
2. **Monitor Workflows**: Check workflow logs regularly for issues
3. **Version Control**: Keep schemas and configs in version control
4. **Document Changes**: Update documentation when adding sources
5. **Quality Checks**: Enable all quality assurance features
6. **Backup Data**: Ensure ingested data is backed up
7. **Review Metadata**: Regularly review metadata for accuracy
8. **Update Dependencies**: Keep Python packages up to date
9. **Security**: Never commit API keys or secrets
10. **Validation**: Always validate data against schemas

## Getting Help

### Resources
- Main documentation: `IMPLEMENTATION.md`
- Dataset documentation: `datasets/README.md`
- Workflow files: `.github/workflows/`
- Schema definitions: `datasets/schemas/`

### Common Commands
```bash
# Validate everything
python datasets/validate_schemas.py
python datasets/demo_ingestion.py

# Check workflow syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/master-ingestion-pipeline.yml'))"

# List all workflows
gh workflow list

# View workflow runs
gh run list --workflow=master-ingestion-pipeline.yml

# View specific run
gh run view <run-id>
```

## Quick Reference

### Directory Structure
```
datasets/
├── mathematical/         # Math datasets
├── programming-libraries/# Library metadata
├── ml-training/         # ML datasets
├── quantum/             # Quantum libraries
├── schemas/             # Data schemas
├── metadata/            # Ingestion metadata
├── reports/             # Status reports
└── sources_config.yaml  # Source configuration
```

### Key Files
- `requirements.txt` - Python dependencies
- `build_manifest.yaml` - Build configuration
- `datasets/sources_config.yaml` - Data source config
- `datasets/validate_schemas.py` - Schema validator
- `datasets/demo_ingestion.py` - Demonstration script
- `.github/workflows/*.yml` - Ingestion workflows

### Workflow Dependencies
```
master-ingestion-pipeline.yml
├── Triggers based on schedule
├── ingest-kaggle-datasets.yml (monthly)
├── ingest-github-libraries.yml (weekly)
├── ingest-ml-training-data.yml (weekly)
└── ingest-quantum-libraries.yml (monthly)
```
