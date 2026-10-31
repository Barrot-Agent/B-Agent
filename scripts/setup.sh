#!/usr/bin/env bash
set -euo pipefail

echo "Setting up B-Agent development environment..."

python -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements-dev.txt

pre-commit install

if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env created from template. Edit it with your credentials."
fi

echo "Setup complete. Activate with: source .venv/bin/activate"
