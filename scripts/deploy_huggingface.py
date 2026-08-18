"""
deploy_huggingface.py
=====================
Pushes the B-Agent repository to a Hugging Face Hub model/space repository
and auto-generates a model card (README.md) with badges and metadata.

Required environment variable:
    HF_TOKEN  – Hugging Face write-access token (store as a GitHub secret)

Optional environment variables:
    HF_REPO_ID  – Destination repo, defaults to "Barrot-Agent/B-Agent"
    HF_REPO_TYPE – "model" | "space" | "dataset", defaults to "model"
"""

import logging
import os
import sys
from pathlib import Path

from huggingface_hub import HfApi, create_repo, upload_folder
from huggingface_hub.utils import RepositoryNotFoundError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
HF_TOKEN = os.environ.get("HF_TOKEN", "")
REPO_ID = os.environ.get("HF_REPO_ID", "Scribedpengenius/barrot-omega")
REPO_TYPE = os.environ.get("HF_REPO_TYPE", "space")
LOCAL_DIR = Path(__file__).parent

# Files / patterns to exclude from the upload
IGNORE_PATTERNS = [
    ".git*",
    ".config",
    ".npm",
    ".termux",
    "__pycache__",
    "*.pyc",
    "venv",
    ".venv",
    "node_modules",
    "output",
    "kaggle.json",
    ".databrickscfg",
    ".env",
    "*.log",
    "*.tmp",
]

MODEL_CARD_TEMPLATE = """---
language:
- en
tags:
- barrot
- agent
- llm
license: apache-2.0
---

# Barrot Agent – B-Agent

![Sync to HF](https://github.com/Barrot-Agent/B-Agent/actions/workflows/sync-huggingface.yml/badge.svg)
![Databricks Deploy](https://github.com/Barrot-Agent/B-Agent/actions/workflows/deploy-databricks.yml/badge.svg)

## Overview

B-Agent is an autonomous AI agent system built on top of open-source large
language models.  This repository is automatically synchronised from
[GitHub](https://github.com/Barrot-Agent/B-Agent) every six hours.

## Quickstart

```python
from transformers import pipeline
pipe = pipeline("text-generation", model="Barrot-Agent/B-Agent")
print(pipe("Hello, I am Barrot")[0]["generated_text"])
```

## Repository structure

| Path | Description |
|------|-------------|
| `app.py` | Streamlit demo application |
| `deploy_huggingface.py` | HF Hub deployment script |
| `deploy_databricks.py` | Databricks deployment script |
| `kaggle_competitions_automation.py` | Kaggle pipeline |
| `sync_manager.py` | Multi-platform orchestrator |

## License

Apache 2.0
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate_token() -> None:
    if not HF_TOKEN:
        log.error("HF_TOKEN environment variable is not set.")
        sys.exit(1)


def _ensure_repo(api: HfApi) -> None:
    """Create the remote repository if it does not exist yet."""
    try:
        api.repo_info(repo_id=REPO_ID, repo_type=REPO_TYPE)
        log.info("Repository %s already exists.", REPO_ID)
    except RepositoryNotFoundError:
        log.info("Creating repository %s (type=%s)…", REPO_ID, REPO_TYPE)
        create_repo(
            repo_id=REPO_ID,
            repo_type=REPO_TYPE,
            token=HF_TOKEN,
            private=False,
            exist_ok=True,
        )
        log.info("Repository created.")


def _write_model_card() -> None:
    card_path = LOCAL_DIR / "README.md"
    if not card_path.exists():
        card_path.write_text(MODEL_CARD_TEMPLATE, encoding="utf-8")
        log.info("Model card written to README.md")
    else:
        log.info("README.md already exists – skipping auto-generation.")


def _upload(api: HfApi) -> str:
    log.info("Uploading %s to %s …", LOCAL_DIR, REPO_ID)
    commit_url = upload_folder(
        repo_id=REPO_ID,
        repo_type=REPO_TYPE,
        folder_path=str(LOCAL_DIR),
        token=HF_TOKEN,
        ignore_patterns=IGNORE_PATTERNS,
        commit_message="Auto-sync from GitHub Actions",
    )
    return commit_url


def _tag_release(api: HfApi) -> None:
    """
    Create a lightweight tag on the Hub matching the GitHub SHA when available.
    Silently skips if the tag already exists.
    """
    sha = os.environ.get("GITHUB_SHA", "")
    if not sha:
        return
    tag = f"sha-{sha[:7]}"
    try:
        api.create_tag(
            repo_id=REPO_ID,
            repo_type=REPO_TYPE,
            tag=tag,
            token=HF_TOKEN,
        )
        log.info("Tagged release: %s", tag)
    except Exception as exc:  # tag may already exist
        log.debug("Tag creation skipped: %s", exc)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    _validate_token()
    api = HfApi(token=HF_TOKEN)

    _ensure_repo(api)
    _write_model_card()
    commit_url = _upload(api)
    log.info("Upload committed: %s", commit_url)
    _tag_release(api)
    log.info("✅ Hugging Face deployment complete.")


if __name__ == "__main__":
    main()
