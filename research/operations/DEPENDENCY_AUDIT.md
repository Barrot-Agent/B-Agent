# Dependency audit status

Audit basis: main commit `34248159231cc469ac7c95c919b336615ceab10e` (2026-11-03).

## Manifests found

The complete Git tree was inspected (1,350 entries; not truncated). The dependency files found were:

- `requirements.txt`: 11 main runtime declarations.
- `requirements-dev.txt`: includes `requirements.txt` plus 12 development declarations.
- `hf_space/requirements.txt`: 4 deployment declarations.
- `legacy/requirements_legacy.txt`: 12 legacy/deployment declarations, including Databricks SDK, Kaggle, pandas and scikit-learn.

No `uv.lock`, `poetry.lock`, `Pipfile.lock`, npm lockfile, Cargo lockfile, or other conventional dependency lockfile was found in the complete tree.

## Current controls

- Dependabot is configured for weekly pip and GitHub Actions updates, with a five-PR limit for each ecosystem.
- The core CI workflow installs a limited test subset (`pytest`, `pytest-cov`, PyJWT, cryptography, pydantic, pydantic-settings and requests). It does not install and test the full declared runtime dependency set.
- No dedicated pip vulnerability-audit workflow was found on the inspected main commit.

## New read-only audit

The proposed `.github/workflows/dependency-audit.yml` runs `pip-audit` on:
1. Main runtime plus development declarations (the dev manifest includes the runtime manifest).
2. Hugging Face Space declarations.
3. Legacy declarations.

It runs on dependency-related pull requests, weekly, and manually. It requests only `contents: read`; it does not use secrets, write files, open PRs or deploy.

## Interpretation limits

There are no lockfiles. `pip-audit -r` resolves current compatible package versions from declared ranges; it does not prove which exact package builds are installed in every deployed environment. The legacy manifest's current deployment use is not established. Results must be treated as a resolver snapshot, not a reproducible deployed SBOM.

The workflow uses the repository's current major-tag action convention (`actions/checkout@v4`, `actions/setup-python@v5`). Immutable SHA pinning of third-party actions remains a separate supply-chain hardening task.
