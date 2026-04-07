.PHONY: install install-dev lint format test build docker-build clean

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

lint:
	flake8 barrot_agent tests
	mypy barrot_agent

format:
	black barrot_agent tests
	isort barrot_agent tests

test:
	pytest

test-fast:
	pytest tests/test_config.py tests/test_models.py -v

docker-build:
	docker build -t b-agent:latest .

docker-dev:
	docker compose up --build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache htmlcov coverage.xml dist build *.egg-info
