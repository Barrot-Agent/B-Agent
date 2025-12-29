# SHRM - System Health & Resource Monitor

## Overview
SHRM (System Health & Resource Monitor) is a companion system that maintains continuous communication with Barrot-Agent through a ping-pong protocol.

## Purpose
SHRM monitors and responds to Barrot's operational status, creating a feedback loop that ensures:
- System health is continuously tracked
- Resource allocation is monitored
- Workflow integrity is maintained
- Bundle synchronization is verified
- Rail status is confirmed

## Ping-Pong Protocol
The Barrot-SHRM ping-pong cycle operates as follows:

1. **PING**: Barrot sends a health check signal to SHRM
2. **PONG**: SHRM responds with system status confirmation
3. **Logging**: Both interactions are logged to respective files
4. **Frequency**: Executes every 15 minutes via GitHub Actions

## Files
- `shrm-config.yaml` - SHRM configuration and settings
- `shrm-response-log.md` - Complete history of all ping-pong interactions
- `README.md` - This documentation

## Benefits
- **Reliability**: Ensures both systems are operational
- **Traceability**: Complete audit trail of all interactions
- **Automation**: Self-maintaining through GitHub Actions
- **Monitoring**: Real-time health status tracking
- **Integration**: Seamless coordination with Barrot's existing workflow

## Integration Points
- Writes to `memory-bundles/outcome-relay.md`
- Updates `memory-bundles/build-ledger.json`
- Maintains own log in `SHRM-System/shrm-response-log.md`
- Syncs status in `SHRM-System/shrm-config.yaml`

## Workflow
The ping-pong cycle is automated via the `barrot-ping-pong` job in `.github/workflows/barrot-unified.yml` and runs on a schedule (every 15 minutes) or can be triggered manually with the 'ping-pong' option.
