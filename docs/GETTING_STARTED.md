# Getting Started with B-Agent

## Prerequisites

- Python 3.10 or later
- A Hugging Face account and API token (for model download)
- 8GB+ RAM recommended (16GB for BF16 inference)
- NVIDIA GPU (optional but recommended)

## Installation

```bash
git clone https://github.com/Barrot-Agent/B-Agent.git
cd B-Agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your HF_TOKEN
streamlit run app.py
```

## Docker

```bash
docker compose up
# App available at http://localhost:8501
```

## Configuration

Copy `.env.example` to `.env` and set:

| Variable | Description | Default |
|---|---|---|
| `HF_TOKEN` | Hugging Face API token | — |
| `ENVIRONMENT` | `development` / `staging` / `production` | `development` |
| `DEBUG` | Enable debug logging | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

## First Run

The first run downloads the IBM Granite model (~8GB). Subsequent runs use the cached version.
