# Barrot V3 Codespaces

## Default environment

The checked-in devcontainer uses Python 3.11 to match GitHub Actions. The image
installs Git, GitHub CLI, Make, and common native build headers. The prebuild
lifecycle creates or reuses `.venv` and installs
`requirements-dev-codespaces.txt`.

The default workspace deliberately does **not** install PyTorch, Transformers,
Accelerate, BitsAndBytes, Safetensors, or Streamlit. These remain explicit
optional groups:

- `make install-ml` installs `requirements-ml.txt`.
- `make install-ui` installs `requirements-ui.txt`.
- `make install-dev-full` installs the complete development dependency set
  used by the full GitHub Actions suite.

The legacy `requirements.txt` remains unchanged and continues to install the
full runtime dependency set for existing Docker and production workflows.

## Commands

Run these from the repository root:

- `make environment-check` — verify Python, Git, GitHub CLI, Make, core modules,
  and dependency consistency.
- `make test-core` — run the core test manifest used by GitHub Actions.
- `make install-dev-full && make test-full` — install complete development
  dependencies and run every test under `tests/`.
- `make lint` and `make format` — use the existing repository tools.
- `make install-ml` or `make install-ui` — opt into heavier model or UI
  dependencies only when the task requires them.

The setup scripts are idempotent. They do not reset, clean, stash, restore, or
overwrite a worktree. If an existing `.venv` directory is incomplete, setup
stops and reports it rather than deleting or replacing it.

## Secrets: Codespaces and Actions are separate

GitHub Codespaces secrets and GitHub Actions secrets are separate scopes. An
Actions secret is not automatically available inside a Codespace, and a
Codespaces secret is not automatically available to Actions.

The existing Actions secret is named exactly `SERP_API_KEY`. This devcontainer
does not read, request, print, copy, or change that secret. If a Codespace later
needs SerpApi access, an authorized operator must separately create a
Codespaces secret with the exact name `SERP_API_KEY` in the appropriate
Codespaces settings scope. Do not put its value in a Dockerfile, build argument,
`devcontainer.json`, committed environment file, terminal transcript, log, or
artifact.

Codespaces secrets are injected for the workspace at runtime. Actions secrets
remain configured under repository Actions secrets and are consumed only by
authorized workflows. Never copy a secret between these scopes automatically.

## Prebuilds and limitations

This change supplies a prebuild-compatible devcontainer lifecycle but does not
enable repository prebuilds or launch a Codespace. Enabling prebuilds is a
repository-settings action that requires an authorized administrator. A real
Codespaces image build and prebuild execution therefore remain unverified until
an administrator enables and runs them.

SerpApi issue #1657 remains a separate implementation task. This environment
provides a reproducible Python 3.11 workspace for that task; it does not perform
a live SerpApi request or access `SERP_API_KEY`.
