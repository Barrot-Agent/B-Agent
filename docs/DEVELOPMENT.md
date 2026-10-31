# Development Guide

## Setup

```bash
git clone https://github.com/Barrot-Agent/B-Agent.git
cd B-Agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
pre-commit install
```

## Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_config.py -v

# With coverage
pytest --cov=barrot_agent --cov-report=html
```

## Code Quality

```bash
# Format
black barrot_agent tests
isort barrot_agent tests

# Lint
flake8 barrot_agent tests

# Type check
mypy barrot_agent
```

Or use Make:

```bash
make lint
make test
make format
```

## Docker Development

```bash
docker compose up --build
```

## Environment Variables

See `.env.example` for all available options.

## Repository Hygiene

- Keep root-level files limited to repository entrypoints, packaging metadata, and top-level documentation.
- Place new experiments, one-off scripts, and legacy material under subsystem directories or `legacy/`.
