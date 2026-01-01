# Barrot Snapshot System - Technical Overview

## Introduction

The Barrot Snapshot System is a comprehensive monitoring and transparency solution that captures every action and system state in real-time. This document provides a technical overview of the implementation.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      Barrot Snapshot System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │ Action Snapshots│    │Periodic Snapshots│                    │
│  │   (immediate)   │    │  (every 30 min)  │                    │
│  └────────┬────────┘    └────────┬─────────┘                    │
│           │                       │                              │
│           └───────────┬───────────┘                              │
│                       │                                          │
│           ┌───────────▼──────────┐                              │
│           │  Snapshot Generator   │                              │
│           │  (snapshot_generator) │                              │
│           └───────────┬──────────┘                              │
│                       │                                          │
│           ┌───────────▼──────────┐                              │
│           │   Storage Layer      │                              │
│           │  (snapshots/*.json)  │                              │
│           └───────────┬──────────┘                              │
│                       │                                          │
│        ┌──────────────┼──────────────┐                          │
│        │              │               │                          │
│  ┌─────▼─────┐  ┌────▼────┐  ┌──────▼──────┐                  │
│  │  Viewer   │  │Dashboard│  │Action Tracker│                  │
│  │   (CLI)   │  │  (HTML) │  │   (API)      │                  │
│  └───────────┘  └─────────┘  └──────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Action Execution** → Action Tracker captures details
2. **Snapshot Generator** → Creates JSON snapshot
3. **Storage** → Saves to `snapshots/` directory
4. **Viewers** → CLI, Dashboard, or API access

## File Structure

```
snapshots/
├── action_YYYYMMDD_HHMMSS_ffffff.json  # Individual action snapshots
├── periodic_YYYYMMDD_HHMMSS.json       # Periodic state snapshots
├── latest_periodic.json                # Latest periodic snapshot (symlink-like)
└── action_log.jsonl                    # Continuous action log (JSONL format)
```

## Snapshot Schema

### Action Snapshot

```json
{
  "snapshot_id": "action_20251222_023211_483890",
  "snapshot_type": "action",
  "timestamp": "2025-12-22T02:32:11.483890Z",
  "action": {
    "type": "deployment",
    "status": "executing|completed|failed",
    "details": {
      "environment": "production",
      "version": "1.0.0"
    },
    "started_at": "2025-12-22T02:32:11.483890Z"
  },
  "metadata": {
    "generated_by": "BarrotSnapshotGenerator",
    "version": "1.0.0"
  }
}
```

### Periodic Snapshot

```json
{
  "snapshot_id": "periodic_20251222_023211",
  "snapshot_type": "periodic",
  "timestamp": "2025-12-22T02:32:11.661541Z",
  "interval": "30_minutes",
  "system_state": {
    "timestamp": "2025-12-22T02:32:11.661570Z",
    "uptime": "active",
    "health": "operational"
  },
  "build_state": {
    "build_signature": "BNDL-V2",
    "timestamp": "2025-12-06T03:15:00Z",
    "modules": [...],
    "provenance_hash": "123e4567-e89b-12d3-a456-426614174000"
  },
  "rail_status": {
    "ingestion": "active",
    "deployment": "stable",
    "microagent": "recursive",
    "prediction": "evolving",
    "dashboard": "publishing",
    "cognition": "recursive"
  },
  "active_processes": {...},
  "workflows": {...},
  "cognitive_state": {
    "protocols": ["Cross Reliance", "Cross Annex", "Cross Index"],
    "status": "active"
  },
  "task_progress": {...},
  "metadata": {...}
}
```

## API Reference

### BarrotSnapshotGenerator

The main class for generating snapshots.

#### Methods

- `generate_action_snapshot(action_type, action_details, status="executing")`
  - Generates an immediate snapshot for an action
  - Returns: `(snapshot_id, snapshot_dict)`

- `generate_periodic_snapshot()`
  - Generates a comprehensive system state snapshot
  - Returns: `(snapshot_id, snapshot_dict)`

- `get_latest_snapshots(count=10)`
  - Retrieves the N most recent snapshots
  - Returns: `List[dict]`

- `generate_snapshot_summary()`
  - Generates summary statistics
  - Returns: `dict` with counts and timestamps

### ActionTracker

Wrapper class for easy action tracking.

#### Methods

- `track_action(action_type, details, status="executing")`
  - Track a single action
  - Returns: `snapshot_id`

- `track_start(action_type, details=None)`
  - Track the start of an action
  - Returns: `snapshot_id`

- `track_complete(action_type, details=None)`
  - Track the completion of an action
  - Returns: `snapshot_id`

- `track_failure(action_type, error, details=None)`
  - Track a failed action
  - Returns: `snapshot_id`

#### Context Manager

```python
with TrackedAction(tracker, "deployment", {"env": "prod"}):
    # Your code here
    # Automatically tracked on success or failure
```

### SnapshotViewer

View and analyze snapshots.

#### Methods

- `view_latest_periodic()`
  - Display the latest periodic snapshot

- `view_latest_actions(count=10)`
  - Display the N most recent actions

- `view_all_snapshots()`
  - List all available snapshots

- `view_snapshot_by_id(snapshot_id)`
  - Display a specific snapshot

- `generate_dashboard_html(output_file="snapshot_dashboard.html")`
  - Generate an HTML dashboard

## GitHub Actions Integration

### Workflow Configuration

Location: `.github/workflows/barrot-snapshot.yml`

#### Triggers

1. **Schedule**: Every 30 minutes via cron
2. **Push**: On push to main branch
3. **Manual**: Via workflow_dispatch

#### Jobs

##### generate-periodic-snapshot
- Runs on schedule or manual trigger
- Generates a periodic system state snapshot
- Commits and pushes to repository

##### generate-action-snapshot
- Runs on push events
- Captures push event details
- Updates build ledger and outcome relay
- Commits and pushes snapshot

### Workflow Security

- Uses `checkout@v4` for secure repository checkout
- Uses `setup-python@v5` for Python environment
- Properly escapes commit messages to prevent injection
- Uses `contents: write` permission (minimal required)

## Security Features

### Input Validation

1. **JSON Parsing**: Validates JSON inputs with error handling
2. **Path Validation**: Ensures file paths exist and are valid
3. **Type Checking**: Validates data types before processing

### Output Security

1. **HTML Escaping**: All user data in HTML is escaped to prevent XSS
2. **JSON Encoding**: Proper JSON encoding for commit messages
3. **File Permissions**: Appropriate file permissions on snapshots

### Error Handling

1. **Try-Catch Blocks**: Comprehensive error handling
2. **Graceful Degradation**: System continues if non-critical errors occur
3. **Error Logging**: All errors are logged with context

## Performance Considerations

### Storage

- JSON files are compact and efficient
- JSONL format for action log enables append-only writes
- Periodic cleanup can be automated via cron or workflow

### Scalability

- O(1) write operations for snapshots
- O(n) read operations where n is number of snapshots
- Latest periodic snapshot cached for quick access

### Optimization Tips

1. Archive old snapshots periodically
2. Use `latest_periodic.json` for most recent state
3. Index action_log.jsonl for faster searches
4. Consider compression for archived snapshots

## Monitoring and Alerting

### Health Checks

Monitor these indicators:

1. **Snapshot Generation Rate**: Should match expected frequency
2. **File System Usage**: Monitor disk space
3. **Error Rate**: Track errors in snapshot generation
4. **Action Diversity**: Variety of action types being tracked

### Alerts

Set up alerts for:

1. Failed snapshot generation
2. Missing periodic snapshots (> 35 minutes gap)
3. Disk space low
4. Abnormal action patterns

## Best Practices

### Action Naming

- Use descriptive, consistent action types
- Follow naming convention: `module_action` (e.g., `deployment_start`)
- Use lowercase with underscores

### Details Content

- Include all relevant context
- Add timestamps when appropriate
- Include error messages for failures
- Add performance metrics (duration, resource usage)

### Integration

- Use context managers for automatic tracking
- Wrap critical operations with action tracking
- Track both start and end of long-running operations
- Always track failures

### Maintenance

- Review snapshots weekly for insights
- Archive old snapshots monthly
- Update dashboards regularly
- Monitor storage usage

## Troubleshooting

### Common Issues

#### Issue: Snapshots not being generated

**Check:**
1. Permissions on `snapshots/` directory
2. Disk space available
3. Python dependencies installed
4. GitHub Actions workflow status

#### Issue: Invalid JSON in snapshots

**Check:**
1. Input validation in action_tracker
2. YAML file format in build_manifest
3. Recent code changes

#### Issue: Dashboard not updating

**Solution:**
1. Regenerate dashboard: `python snapshot_viewer.py dashboard`
2. Check if `latest_periodic.json` exists
3. Verify browser cache is cleared

## Future Enhancements

Potential improvements:

1. **Real-time Streaming**: WebSocket-based live updates
2. **Advanced Analytics**: Trend analysis and predictions
3. **Alerting System**: Automated alerts for anomalies
4. **Compression**: Automatic compression of old snapshots
5. **Database Backend**: Optional database storage for large scale
6. **API Server**: REST API for programmatic access
7. **Retention Policies**: Configurable snapshot retention
8. **Search and Filter**: Advanced search capabilities

## Conclusion

The Barrot Snapshot System provides comprehensive transparency into all operations with minimal performance overhead. It's designed to be extensible, secure, and easy to integrate into existing workflows.

For usage examples and integration patterns, see:
- [README.md](README.md) - Overview and quick start
- [USAGE.md](USAGE.md) - Detailed usage guide
- [examples/](examples/) - Integration examples
