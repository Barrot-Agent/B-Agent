# Dependency audit status

Audit basis: current main `58425d038a0a16082267d9de28757fd5c4eb499d` (2026-11-04); this integration branch adds the corrections below.

## Manifests found

The complete Git tree was inspected (1,389 entries; not truncated). The dependency files found were:

- `requirements.txt`: 15 canonical runtime declarations. PyJWT, cryptography, numpy and websockets are now included because the full-suite collection exposed a missing PyJWT dependency and the supplemental manifest already declared these runtime libraries.
- `requirements-dev.txt`: includes `requirements.txt` plus 12 development declarations.
- `requirements.tx`: 6 supplemental compatibility declarations. It is not referenced by the README quickstart; its separate intended consumer remains unresolved. It is retained and audited rather than silently deleted.
- `hf_space/requirements.txt`: 4 deployment declarations.
- `legacy/requirements_legacy.txt`: 12 legacy/deployment declarations, including Databricks SDK, Kaggle, pandas and scikit-learn.

No `uv.lock`, `poetry.lock`, `Pipfile.lock`, npm lockfile, Cargo lockfile, or other conventional dependency lockfile was found in the complete tree.

## Current controls

- Dependabot is configured for weekly pip and GitHub Actions updates, with a five-PR limit for each ecosystem.
- Core CI runs the selected core test modules; the integrated CI adds a separate full-suite job that installs `requirements-dev.txt` and runs every file under `tests/`.
- The first full-suite collection identified `ModuleNotFoundError: jwt` in `tests/test_pillars_check_readonly.py`. PyJWT was installed manually by core CI but missing from the declared development/runtime requirements. This branch adds PyJWT to both `requirements.txt` and `pyproject.toml`, together with the supplemental cryptography, numpy and websockets declarations.
- The read-only `pip-audit` workflow audits runtime/development, supplemental `requirements.tx`, Hugging Face Space and legacy manifests.

## Interpretation limits

There are no lockfiles. `pip-audit -r` resolves current compatible package versions from declared ranges; it does not prove which exact package builds are installed in every deployed environment. The legacy and supplemental manifest deployment use remains partly unresolved. Results are resolver snapshots, not a reproducible deployed SBOM.

The workflow uses the repository's current major-tag action convention (`actions/checkout@v4`, `actions/setup-python@v5`). Immutable SHA pinning of third-party actions remains a separate supply-chain hardening task.
