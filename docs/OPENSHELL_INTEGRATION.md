# OpenShell Integration Guide

## Overview

OpenShell is a secure runtime environment integrated into B-Agent that provides:

- **Deny-by-default policy enforcement** — every agent action must be explicitly permitted
- **Privacy-first inference routing** — prefers local NVIDIA GPU execution over remote APIs
- **Structured audit logging** — every action is recorded with full context
- **Sandbox execution** — OS-level resource limits on subprocesses
- **Hot-reloadable policies** — update security rules without restarting

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize the runtime

```python
from barrot_agent.runtime.openshell_runtime import OpenShellRuntime

runtime = OpenShellRuntime(policy_path="openshell/policies")
runtime.initialize()
```

### 3. Wrap an agent

```python
@runtime.wrap_agent
def my_inference_agent(prompt: str) -> str:
    return "response"

result = my_inference_agent("What is 2+2?")
```

### 4. Check runtime stats

```python
stats = runtime.get_runtime_stats()
print(stats)
# {'actions_allowed': 1, 'actions_blocked': 0, 'agents_wrapped': 1, 'policies_loaded': 2}
```

## Configuration Reference

The main configuration file is `config/openshell_config.yaml`.

| Key | Description | Default |
|-----|-------------|---------|
| `runtime.enforcement_mode` | `strict` or `permissive` | `strict` |
| `runtime.hot_reload` | Watch policy files for changes | `true` |
| `sandbox.enabled` | Enable subprocess sandboxing | `true` |
| `inference.local_gpu_priority` | Prefer local GPU over remote APIs | `true` |
| `audit.enabled` | Enable audit logging | `true` |

## Policy Configuration

Policies live in `openshell/policies/`. Three files ship by default:

| File | Purpose |
|------|---------|
| `default_policy.yaml` | Base deny-by-default rules |
| `agent_policies.yaml` | Per-agent permission overrides |
| `inference_routes.yaml` | Endpoint routing and privacy rules |

### Writing a custom policy

```yaml
version: "1.0"
policy_name: my_custom_policy
enforcement_mode: strict

allowed_binaries:
  - git
  - python3

network_rules:
  allow_domains:
    - api.example.com
  deny_all_other: true

api_restrictions:
  - method: execute_code
    allow_from:
      - my_agent
    log_level: info
```

## Security Model

### Layered defence

```
Request → Policy Engine → Sandbox Executor → Action
              ↓
         Audit Logger
```

1. **Policy Engine** evaluates every action against loaded YAML policies.
2. **Sandbox Executor** applies OS resource limits to subprocesses.
3. **Audit Logger** records every decision (allow or deny) with full context.

### Deny-by-default

When `enforcement_mode: strict` (the default), any action with no matching rule is **denied**.
You must explicitly add `api_restrictions` entries to permit actions.

## Usage Examples

### Execute with policy check

```python
decision = runtime.execute_with_policy(
    action="network_request",
    context={"domain": "huggingface.co"},
    agent_id="inference_agent",
)
if not decision.allowed:
    raise PermissionError(decision.reason)
```

### Route an inference request

```python
import yaml
from barrot_agent.inference.privacy_router import PrivacyRouter

with open("openshell/policies/inference_routes.yaml") as f:
    config = yaml.safe_load(f)

router = PrivacyRouter(config)
result = router.route_inference("llama3", {"prompt": "Hello world"})
print(result["endpoint"])  # local_nvidia_gpu
```

### Query the audit trail

```python
from openshell.audit.audit_engine import AuditEngine

engine = AuditEngine("/audit")
trail = engine.get_audit_trail(agent_id="inference_agent")
for event in trail:
    print(event["timestamp"], event["action_type"])
```
