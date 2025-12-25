# Barrot Snapshot System - Usage Guide

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Advanced Usage](#advanced-usage)
5. [Integration](#integration)
6. [Troubleshooting](#troubleshooting)

## Overview

The Barrot Snapshot System is designed to provide complete transparency into Barrot's operations by capturing:

- **Real-time action snapshots** as each action is executed
- **Periodic state snapshots** every 30 minutes
- **Comprehensive system state** including builds, rails, processes, and cognitive state

## Installation

### Requirements

```bash
pip install pyyaml
```

### Verify Installation

```bash
python snapshot_generator.py --help
python snapshot_viewer.py --help
```

## Basic Usage

### Generate Your First Snapshot

#### Periodic Snapshot

```bash
python snapshot_generator.py periodic
```

Output:
```
Generated periodic snapshot: periodic_20251222_022049
{
  "snapshot_id": "periodic_20251222_022049",
  "snapshot_type": "periodic",
  "timestamp": "2025-12-22T02:20:49.563714Z",
  ...
}
```

#### Action Snapshot

```bash
python snapshot_generator.py action "deployment" '{"target": "production", "version": "1.2.0"}'
```

### View Snapshots

#### View Latest Periodic Snapshot

```bash
python snapshot_viewer.py latest
```

#### View Recent Actions

```bash
# View last 10 actions
python snapshot_viewer.py actions 10

# View last 50 actions
python snapshot_viewer.py actions 50
```

#### List All Snapshots

```bash
python snapshot_viewer.py all
```

#### View Specific Snapshot

```bash
python snapshot_viewer.py view periodic_20251222_022049
```

## Advanced Usage

### Programmatic Access

#### Generate Snapshots from Python Code

```python
from snapshot_generator import BarrotSnapshotGenerator

# Initialize generator
generator = BarrotSnapshotGenerator()

# Generate action snapshot
snapshot_id, snapshot = generator.generate_action_snapshot(
    action_type="test_execution",
    action_details={
        "test_suite": "integration",
        "tests_passed": 45,
        "tests_failed": 2,
        "duration": "120s"
    },
    status="completed"
)

print(f"Generated snapshot: {snapshot_id}")

# Generate periodic snapshot
snapshot_id, snapshot = generator.generate_periodic_snapshot()

# Get summary of all snapshots
summary = generator.generate_snapshot_summary()
print(f"Total snapshots: {summary['total_snapshots']}")
```

#### View Snapshots from Python Code

```python
from snapshot_viewer import SnapshotViewer

# Initialize viewer
viewer = SnapshotViewer()

# View latest periodic snapshot
viewer.view_latest_periodic()

# View recent actions
viewer.view_latest_actions(count=20)

# Generate HTML dashboard
dashboard_path = viewer.generate_dashboard_html()
print(f"Dashboard generated at: {dashboard_path}")
```

### Custom Action Types

You can create snapshots for any action type:

```bash
# Build action
python snapshot_generator.py action "build" '{"module": "core", "result": "success", "duration": "45s"}'

# Deployment action
python snapshot_generator.py action "deployment" '{"environment": "staging", "status": "deployed"}'

# Test action
python snapshot_generator.py action "test" '{"suite": "unit", "passed": 100, "failed": 0}'

# Custom action
python snapshot_generator.py action "data_ingestion" '{"source": "kaggle", "records": 10000, "status": "completed"}'
```

### Filtering and Analysis

#### Count Snapshots by Type

```bash
python snapshot_generator.py summary
```

Output:
```json
{
  "total_snapshots": 42,
  "action_snapshots": 35,
  "periodic_snapshots": 7,
  "latest_action": 1734831657.454420,
  "latest_periodic": 1734831649.563714
}
```

## Integration

### GitHub Actions Integration

The snapshot system is automatically integrated with GitHub Actions:

#### Automatic Triggers

1. **Every 30 minutes**: Periodic snapshot via cron schedule
2. **On push**: Action snapshot capturing commit details
3. **Manual trigger**: Via GitHub Actions UI

#### Workflow Configuration

See `.github/workflows/barrot-snapshot.yml`:

```yaml
on:
  schedule:
    - cron: '*/30 * * * *'  # Every 30 minutes
  push:
    branches: [ main ]
  workflow_dispatch:  # Manual trigger
```

### Custom Integration

#### In Shell Scripts

```bash
#!/bin/bash

# Generate snapshot at start of deployment
python snapshot_generator.py action "deployment_start" \
  '{"environment": "'$ENV'", "version": "'$VERSION'"}'

# Run deployment
./deploy.sh

# Generate snapshot at end
python snapshot_generator.py action "deployment_complete" \
  '{"environment": "'$ENV'", "version": "'$VERSION'", "status": "success"}'
```

#### In Python Scripts

```python
import subprocess
import json

def capture_action(action_type, details):
    """Helper function to capture action snapshots"""
    cmd = [
        'python', 'snapshot_generator.py', 'action',
        action_type,
        json.dumps(details)
    ]
    subprocess.run(cmd)

# Use in your code
capture_action("model_training", {
    "model": "neural_net_v2",
    "accuracy": 0.95,
    "epochs": 100
})
```

## Troubleshooting

### Common Issues

#### Issue: "No periodic snapshot found yet"

**Solution**: Generate your first periodic snapshot:
```bash
python snapshot_generator.py periodic
```

#### Issue: "Failed to read build manifest"

**Solution**: Ensure `build_manifest.yaml` exists in the repository root.

#### Issue: PyYAML not found

**Solution**: Install dependencies:
```bash
pip install pyyaml
```

#### Issue: Permission denied when creating snapshots

**Solution**: Ensure the `snapshots/` directory has write permissions:
```bash
chmod -R u+w snapshots/
```

### Debug Mode

To debug snapshot generation, you can examine the raw JSON:

```bash
# Generate and view in one step
python snapshot_generator.py periodic | python -m json.tool

# View existing snapshot
cat snapshots/latest_periodic.json | python -m json.tool
```

### Logs and Monitoring

#### Check Action Log

```bash
# View raw action log
cat snapshots/action_log.jsonl

# View with pretty printing
cat snapshots/action_log.jsonl | while read line; do echo "$line" | python -m json.tool; echo "---"; done
```

#### Monitor Snapshot Generation

```bash
# Watch for new snapshots
watch -n 5 'ls -lt snapshots/ | head -10'

# Count snapshots by type
echo "Action snapshots: $(ls snapshots/action_*.json 2>/dev/null | wc -l)"
echo "Periodic snapshots: $(ls snapshots/periodic_*.json 2>/dev/null | wc -l)"
```

## Best Practices

1. **Regular Monitoring**: Check the dashboard regularly to monitor system health
2. **Action Naming**: Use descriptive action types for better tracking
3. **Detail Rich**: Include comprehensive details in action snapshots
4. **Clean Up**: Periodically archive old snapshots to manage disk space
5. **Automation**: Leverage GitHub Actions for automatic snapshot generation

## Examples

### Example 1: Complete Deployment Flow

```bash
# Start deployment
python snapshot_generator.py action "deployment_start" \
  '{"target": "production", "version": "2.0.0", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}'

# Execute deployment steps
./build.sh
./test.sh
./deploy.sh

# Complete deployment
python snapshot_generator.py action "deployment_complete" \
  '{"target": "production", "version": "2.0.0", "status": "success", "duration": "300s"}'

# Generate summary
python snapshot_viewer.py latest
```

### Example 2: Monitoring Loop

```bash
#!/bin/bash
# monitor.sh - Continuous monitoring script

while true; do
  echo "=== Barrot Status ==="
  python snapshot_viewer.py latest
  
  echo -e "\n=== Recent Actions ==="
  python snapshot_viewer.py actions 5
  
  sleep 300  # Check every 5 minutes
done
```

### Example 3: Dashboard Generation

```bash
# Generate and open dashboard
python snapshot_viewer.py dashboard
xdg-open snapshot_dashboard.html  # Linux
# or
open snapshot_dashboard.html      # macOS
# or
start snapshot_dashboard.html     # Windows
```

## Next Steps

- Explore the [API Documentation](API.md)
- Check out the [Architecture Guide](ARCHITECTURE.md)
- Review [GitHub Actions Workflows](.github/workflows/)
- Contribute to the [project](CONTRIBUTING.md)
