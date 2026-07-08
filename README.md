# B-Agent

[![CI](https://github.com/Barrot-Agent/B-Agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Barrot-Agent/B-Agent/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

B-Agent is Barrot's intelligent AI agent powered by **IBM Granite 4.0-3B Vision** — a multimodal language model capable of image-text-to-text tasks, feature extraction, and conversational AI.

## Features

- 🖼️ **Multimodal Vision** — Image + text understanding via IBM Granite 4.0-3B Vision
- 💬 **Conversational AI** — Chat template support for dialog
- 🔍 **Feature Extraction** — Vision-language embeddings
- ⚡ **BF16 Precision** — Efficient 4B parameter inference
- 🔒 **Safetensors** — Secure model weight loading
- ☁️ **Streamlit UI** — Interactive web interface

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Barrot-Agent/B-Agent.git
cd B-Agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your HF_TOKEN and settings

# Run the app
streamlit run app.py
```

## Model Details

| Property | Value |
|---|---|
| Model ID | `ibm-granite/granite-4.0-3b-vision` |
| Parameters | 4B |
| Tensor Type | BF16 |
| License | Apache 2.0 |
| Task | Image-Text-to-Text |

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for full development setup.

```bash
pip install -r requirements-dev.txt
pytest
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design documentation.

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for contribution guidelines.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
