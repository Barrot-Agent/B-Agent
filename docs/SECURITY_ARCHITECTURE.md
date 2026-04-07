# Security Architecture

## Overview

B-Agent's security model is built on four pillars:

1. **Policy enforcement** — YAML-driven, deny-by-default access control
2. **Process sandboxing** — OS-level resource limits on every subprocess
3. **Privacy-first inference** — local GPU preferred over remote APIs
4. **Comprehensive auditing** — every action logged with full context

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        B-Agent Process                       │
│                                                             │
│  ┌──────────────┐   ┌───────────────────┐                  │
│  │  Agent Code  │──▶│ OpenShellRuntime  │                  │
│  └──────────────┘   │  (wrap_agent)     │                  │
│                     └────────┬──────────┘                  │
│                              │ execute_with_policy          │
│                     ┌────────▼──────────┐                  │
│                     │   PolicyEngine    │◀── YAML Policies  │
│                     └────────┬──────────┘                  │
│                    ✅ allow  │ ❌ deny                      │
│                    ┌─────────┘                              │
│                    │                                        │
│           ┌────────▼───────────┐                           │
│           │  SandboxExecutor  │  (resource limits)         │
│           └────────┬───────────┘                           │
│                    │                                        │
│           ┌────────▼───────────┐                           │
│           │ SecurityAuditLogger│──▶ /var/log/barrot/       │
│           └────────────────────┘                           │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Inference Subsystem                    │   │
│  │  PrivacyRouter ──▶ LocalGPUManager (H100/B200/A100) │   │
│  │               └──▶ RemoteEndpointManager (fallback) │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                Audit Subsystem                      │   │
│  │  AuditEngine ──▶ AuditLogger ──▶ /audit/*.ndjson    │   │
│  │             └──▶ ComplianceReporter                 │   │
│  │             └──▶ ForensicsAnalyzer                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Sandboxing Layer

### Implementation

`SandboxExecutor` uses Python's `subprocess` module with:

- `preexec_fn` to call `resource.setrlimit` in the child process
- Configurable limits: CPU time, virtual memory, file descriptors, process count
- Wall-clock timeout via `subprocess.run(timeout=...)`

### Resource limit mapping

| Config key | `resource` constant |
|------------|---------------------|
| `max_cpu_seconds` | `RLIMIT_CPU` |
| `max_memory_bytes` | `RLIMIT_AS` |
| `max_file_descriptors` | `RLIMIT_NOFILE` |
| `max_processes` | `RLIMIT_NPROC` |

### AgentSandbox context manager

```python
with AgentSandbox("my_agent", policy=policy, resource_limits=limits) as sb:
    result = sb.execute(my_function, arg1, arg2)
```

Entering the context applies limits to the **current thread's process**.
Exiting restores the previous limits.

---

## Policy Engine

### Evaluation flow

```
evaluate_action(action, agent_id, context)
        │
        ▼
  api_restrictions[*].method == action?
        │
        ├── yes → agent_id in allow_from? → ✅ allow
        │                                 → ❌ deny
        │
        └── no  → enforcement_mode == strict? → ❌ deny
                                              → ✅ allow
```

### Filesystem permission resolution

The engine uses **longest-prefix matching**:

```
Path: /app/models/llama3
Rules: /app (read_write), /app/models (read_only)
Result: read_only  ← /app/models is a longer match
```

---

## Audit System

### Storage format

Events are written as **newline-delimited JSON (NDJSON)** to
`/audit/audit-YYYY-MM-DD.ndjson`.  Each line is a self-contained JSON object:

```json
{"event_id": "uuid", "event_kind": "action", "action_type": "inference",
 "agent_id": "inference_agent", "outcome": "success",
 "details": {"model": "llama3"}, "timestamp": "2024-01-15T10:30:00+00:00"}
```

### Event kinds

| `event_kind` | Trigger |
|--------------|---------|
| `action` | Normal agent action recorded via `record_action` |
| `violation` | Policy breach recorded via `record_violation` |

### Forensics

`ForensicsAnalyzer.identify_anomalies` detects statistical deviations:

- Computes per-agent, per-action-type event rates in a baseline window
- Flags combinations in the analysis window that exceed mean + 2σ

---

## Deployment Security Guide

### Container hardening

The `Dockerfile.openshell` implements:

- Non-root user (`barrot:barrot`, UID 1000)
- Minimal base image (`python:3.11-slim`)
- No unnecessary packages
- Read-only policy volume mount in Kubernetes

### Kubernetes security context

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  capabilities:
    drop: [ALL]
```

### Secret management

Sensitive values (`HF_TOKEN`, `DATABRICKS_TOKEN`) are injected via Kubernetes
`secretKeyRef` — never baked into images or policy files.

### Network policy recommendation

Deploy a Kubernetes `NetworkPolicy` to restrict egress to only the domains
listed in `network_rules.allow_domains`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: b-agent-egress
spec:
  podSelector:
    matchLabels:
      app: b-agent
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector: {}  # DNS
      ports: [{port: 53, protocol: UDP}]
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0   # tighten per environment
      ports: [{port: 443}]
```
