# Policy Configuration Guide

## YAML Syntax Reference

Every policy file must be a YAML mapping with at minimum:

```yaml
version: "1.0"       # required — semantic version string
policy_name: my_pol  # required — unique identifier
```

Optional top-level keys are described in the sections below.

---

## `enforcement_mode`

Controls the default decision when no rule matches.

| Value | Behaviour |
|-------|-----------|
| `strict` | Deny everything not explicitly permitted (recommended) |
| `permissive` | Allow everything not explicitly denied |

```yaml
enforcement_mode: strict
```

---

## `allowed_binaries`

Whitelist of executable names that agents may run via the sandbox.

```yaml
allowed_binaries:
  - git
  - python3
  - pip
  - bash
```

---

## Network Rules

Control which domains agents may reach.

```yaml
network_rules:
  allow_domains:
    - huggingface.co       # exact match
    - "*.internal.corp"    # glob — all subdomains
  deny_all_other: true     # block all unlisted domains
```

### Glob patterns

Use `*.domain.com` to allow all subdomains.  The leading `*.` is treated as a
prefix match, so `*.huggingface.co` also matches `models.huggingface.co`.

---

## Filesystem Permissions

Define access levels for file-system paths.  The **longest matching prefix** wins.

```yaml
filesystem_permissions:
  - path: /app
    access: read_write   # agents can read and write
  - path: /app/secrets
    access: none         # override — block even though /app is read_write
  - path: /data
    access: read_only
  - path: /var/log
    access: append       # can write but not overwrite
```

### Access modes

| Mode | Read | Write | Append |
|------|------|-------|--------|
| `read_only` | ✅ | ❌ | ❌ |
| `read_write` | ✅ | ✅ | ✅ |
| `append` | ✅ | ❌ | ✅ |
| `none` | ❌ | ❌ | ❌ |

---

## API Restrictions

Control which agents may call named methods or actions.

```yaml
api_restrictions:
  - method: execute_code        # action name (string)
    allow_from:                 # list of permitted agent IDs
      - inference_agent
      - research_agent
    log_level: info             # audit log severity

  - method: access_credentials
    allow_from:
      - deployment_agent
    log_level: critical
```

### Log levels

Valid values: `debug`, `info`, `warning`, `error`, `critical`.

---

## Resource Limits

Cap resource consumption of agent processes.

```yaml
resource_limits:
  max_cpu_percent: 80          # 0–100
  max_memory_mb: 4096          # megabytes
  max_file_descriptors: 1024
  max_processes: 50
  execution_timeout_seconds: 300
```

> **Note:** `max_cpu_percent` is advisory (enforced at the scheduler level).
> Hard limits on memory and file descriptors are applied via `resource.setrlimit`.

---

## Common Use Cases

### Research agent — read-only web access

```yaml
version: "1.0"
policy_name: research_readonly
enforcement_mode: strict

network_rules:
  allow_domains:
    - arxiv.org
    - scholar.google.com
  deny_all_other: true

api_restrictions:
  - method: web_search
    allow_from: [research_agent]
  - method: read_files
    allow_from: [research_agent]

resource_limits:
  max_memory_mb: 2048
  execution_timeout_seconds: 600
```

### Deployment agent — credentials + containers

```yaml
version: "1.0"
policy_name: deployment_ops
enforcement_mode: strict

allowed_binaries:
  - git
  - docker
  - kubectl

api_restrictions:
  - method: access_credentials
    allow_from: [deployment_agent]
    log_level: critical
  - method: docker_operations
    allow_from: [deployment_agent]
  - method: kubernetes_operations
    allow_from: [deployment_agent]

resource_limits:
  max_memory_mb: 1024
  execution_timeout_seconds: 900
```

### Audit agent — read-only log access

```yaml
version: "1.0"
policy_name: audit_readonly
enforcement_mode: strict

filesystem_permissions:
  - path: /var/log
    access: read_only
  - path: /audit
    access: read_write   # can write reports

api_restrictions:
  - method: read_logs
    allow_from: [audit_agent]
  - method: generate_reports
    allow_from: [audit_agent]
```
