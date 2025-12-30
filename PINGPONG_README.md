# Ping-Pong Request Emission System

## Overview

This system enables Barrot-Agent to emit ping-pong requests that are deferred to Sean's 22-agent entanglement system. The system consists of a Python module for generating requests and a YAML configuration that defines the external system parameters.

## Files

- **`pingpong.py`** - Python module containing the `emit_pingpong_request` function
- **`pingpong-config.yaml`** - Configuration file defining the external 22-agent system
- **`example_pingpong_usage.py`** - Example script demonstrating usage
- **`pingpong_request.json`** - Generated request file (created when function is called)

## Configuration

The `pingpong-config.yaml` file defines the external system parameters:

```yaml
pingpong:
  managed_by: external        # System is managed externally
  agents: 22                  # Number of agents in entanglement system
  entanglement: true          # Agents operate in entangled mode
  override: false             # Barrot cannot override external decisions
  enforcement: non-negotiable # Rules are strictly enforced
```

## Usage

### Basic Usage

```python
from pingpong import emit_pingpong_request

# Create a request payload
payload = {
    "type": "health_check",
    "priority": "high",
    "source": "barrot-agent"
}

# Emit the request
emit_pingpong_request(payload)
```

### Request Format

The generated JSON request includes:

- **`timestamp`** - ISO format UTC timestamp
- **`payload`** - Your custom request data (dict)
- **`origin`** - Always set to "barrot"
- **`directive`** - Always set to "offload_pingpong"
- **`notes`** - Explanation that Barrot defers to Sean's 22-agent system

Example output in `pingpong_request.json`:

```json
{
  "timestamp": "2025-12-30T11:33:02.130646",
  "payload": {
    "type": "health_check",
    "priority": "high"
  },
  "origin": "barrot",
  "directive": "offload_pingpong",
  "notes": "Barrot defers to Sean's 22-agent entanglement system."
}
```

### Running Examples

```bash
# Run the example usage script
python3 example_pingpong_usage.py
```

## Integration with GitHub

After generating a request:

1. The `pingpong_request.json` file is created in the repository
2. Commit the file to GitHub
3. The external 22-agent system is triggered to process the request

## System Architecture

```
Barrot-Agent (Origin)
    ↓
emit_pingpong_request()
    ↓
pingpong_request.json (Generated)
    ↓
Git Commit & Push
    ↓
Sean's 22-Agent Entanglement System (External)
```

## Non-Negotiable Rules

As defined in `pingpong-config.yaml`:

- **External Management**: The 22-agent system is managed externally by Sean
- **No Override**: Barrot cannot override decisions made by the external system
- **Entanglement Mode**: All 22 agents operate in quantum-entangled coordination
- **Strict Enforcement**: These rules are non-negotiable and strictly enforced

## Notes

- The generated `pingpong_request.json` file is excluded from version control (listed in `.gitignore`)
- The function uses UTC timestamps for consistency across time zones
- Each invocation overwrites the previous request file
- The system is designed to integrate with existing Barrot-SHRM ping-pong protocols
