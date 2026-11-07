# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes |

## Reporting a Vulnerability

If you discover a security vulnerability in B-Agent, please report it responsibly:

1. Do NOT open a public GitHub issue.
2. Email the maintainers privately or use GitHub's private security advisory feature.
3. Include a description of the vulnerability, reproduction steps, and potential impact.

We will acknowledge your report within 48 hours and aim to release a fix within 7 days.

## Security Practices

- Dependencies are scanned weekly via Dependabot.
- Pull-request dependency validation uses strict `pip-audit` checks for the runtime/development requirements, supplemental requirements, Hugging Face Space requirements, legacy requirements, and PEP 621 dependencies in `pyproject.toml`.
- Active workflows use read-only repository permissions for dependency auditing.
- Secrets are managed via environment variables and must never be committed to source.
- Pre-commit hooks prevent accidental secret commits.

## Archived Dependency-Audit Exception

The identifier `PYSEC-2024-232` appears in the archived backup `.barrot-backup/workflows/ci.yml`. It does not appear as an ignore flag in the active `.github/workflows/ci.yml` or `.github/workflows/dependency-audit.yml`. The archived backup is not an active workflow. Re-review its contents before restoring or reactivating any backup workflow.
