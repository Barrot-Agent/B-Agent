# Barrot Snapshot Examples

This directory contains practical examples demonstrating how to integrate the Barrot snapshot system into your workflows.

## Examples

### 1. Python Integration (`integration_example.py`)

Demonstrates various Python integration patterns:

- Basic snapshot generation
- Action tracking
- Context manager for automatic tracking
- Failure tracking
- Batch operations

**Run it:**
```bash
python examples/integration_example.py
```

### 2. Shell Script Integration (`shell_integration.sh`)

Shows how to use snapshots in shell scripts:

- Track deployment actions
- Track build processes
- Track test execution
- Generate periodic snapshots
- View recent actions

**Run it:**
```bash
bash examples/shell_integration.sh
```

## Integration Patterns

### Pattern 1: Simple Action Tracking

```python
from action_tracker import ActionTracker

tracker = ActionTracker()
snapshot_id = tracker.track_action(
    "deployment",
    {"target": "production", "version": "1.0.0"}
)
```

### Pattern 2: Context Manager

```python
from action_tracker import ActionTracker, TrackedAction

tracker = ActionTracker()

with TrackedAction(tracker, "build", {"module": "core"}):
    # Your build logic here
    build_application()
    # Automatically tracked on success or failure
```

### Pattern 3: Shell Script

```bash
# Track action in shell script
python snapshot_generator.py action "deployment" \
  '{"environment": "prod", "version": "2.0.0"}'
```

### Pattern 4: Periodic Snapshots

```bash
# Generate periodic system state snapshot
python snapshot_generator.py periodic
```

## Use Cases

### Continuous Integration

Track CI/CD pipeline stages:
```python
tracker.track_action("ci_start", {"branch": "main", "commit": "abc123"})
tracker.track_action("tests", {"passed": 100, "failed": 0})
tracker.track_action("build", {"status": "success", "duration": "45s"})
tracker.track_action("deploy", {"environment": "production"})
```

### Data Pipelines

Track data processing stages:
```python
tracker.track_action("data_ingestion", {"source": "api", "records": 10000})
tracker.track_action("data_validation", {"checks_passed": 15})
tracker.track_action("data_transformation", {"operations": 5})
tracker.track_action("data_storage", {"destination": "warehouse"})
```

### System Monitoring

Regular health checks:
```python
# In a cron job or scheduler
generator = BarrotSnapshotGenerator()
generator.generate_periodic_snapshot()
```

## Tips

1. **Use descriptive action types**: Make them searchable and meaningful
2. **Include relevant details**: Add context that helps debugging
3. **Track failures**: Always track errors and exceptions
4. **Use context managers**: They handle success/failure automatically
5. **Regular periodic snapshots**: Set up automated periodic snapshots for baseline monitoring

## Advanced Usage

### Custom Action Tracker

Extend the `ActionTracker` class for domain-specific tracking:

```python
from action_tracker import ActionTracker

class MLActionTracker(ActionTracker):
    def track_training(self, model_name, metrics):
        return self.track_action("model_training", {
            "model": model_name,
            "accuracy": metrics.get("accuracy"),
            "loss": metrics.get("loss"),
            "epochs": metrics.get("epochs")
        })
    
    def track_inference(self, model_name, input_count):
        return self.track_action("inference", {
            "model": model_name,
            "inputs": input_count
        })
```

### Integration with Logging

Combine snapshots with logging:

```python
import logging
from action_tracker import ActionTracker

logger = logging.getLogger(__name__)
tracker = ActionTracker()

def deploy(environment, version):
    logger.info(f"Starting deployment to {environment}")
    snapshot_id = tracker.track_start("deployment", {
        "environment": environment,
        "version": version
    })
    
    try:
        # Deployment logic
        perform_deployment(environment, version)
        
        logger.info(f"Deployment successful")
        tracker.track_complete("deployment", {
            "environment": environment,
            "version": version
        })
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        tracker.track_failure("deployment", e, {
            "environment": environment,
            "version": version
        })
        raise
```

## More Information

- See [main README](../README.md) for overview
- See [USAGE.md](../USAGE.md) for detailed usage guide
- Check the source code for more advanced features
