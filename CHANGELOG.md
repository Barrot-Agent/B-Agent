# Changelog

All notable changes to B-Agent are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-04-07

### Added
- Initial project structure with `barrot_agent/` package
- IBM Granite 4.0-3B Vision model integration (`models.py`, `inference.py`)
- Pydantic-based configuration management (`config.py`)
- Structured JSON logging with rotating file support (`logger.py`)
- Core application class (`core.py`)
- Comprehensive test suite with pytest (`tests/`)
- GitHub Actions CI/CD pipeline (`ci.yml`, `release.yml`)
- Dockerfile and docker-compose for containerized deployment
- Pre-commit hooks for code quality enforcement
- Dependabot for automated dependency updates
- Documentation: README, ARCHITECTURE, DEVELOPMENT, CONTRIBUTING, API
- `.env.example` for environment variable templates
- Makefile for common development tasks
- `requirements.txt` with pinned versions
- `requirements-dev.txt` with development tooling
