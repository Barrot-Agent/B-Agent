# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅        |

## Reporting a Vulnerability

If you discover a security vulnerability in B-Agent, please report it responsibly:

1. **Do NOT** open a public GitHub issue.
2. Email the maintainers privately or use GitHub's private security advisory feature.
3. Include a description of the vulnerability, reproduction steps, and potential impact.

We will acknowledge your report within 48 hours and aim to release a fix within 7 days.

## Security Practices

- Dependencies are scanned weekly via Dependabot.
- CI pipeline includes `pip-audit` for known CVE detection.
- Secrets are managed via environment variables — never committed to source.
- Pre-commit hooks prevent accidental secret commits.

## Known Dependency Audit Exceptions

- `PYSEC-2024-232` is temporarily ignored in CI because the vulnerable
  execution path is not exercised by the checked-in Streamlit demo or the
  lightweight validation flow used in this repository today.
- The exception is tracked in `.github/workflows/ci.yml` and must be
  re-reviewed whenever runtime dependencies or application entrypoints change.
