# Contributing to B-Agent

Thank you for contributing!

## Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes
4. Run tests: `pytest`
5. Run linting: `make lint`
6. Commit using conventional commits: `feat: add vision batch inference`
7. Push and open a Pull Request using the PR template

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `test:` adding/updating tests
- `refactor:` code refactor
- `chore:` maintenance

## Code Style

- Formatter: `black` (line length 100)
- Import sort: `isort`
- Linter: `flake8`
- Type hints required for all public functions (`mypy`)

## Tests

All new features must include tests. Coverage must remain ≥ 70%.

## License

By contributing, you agree your contributions are licensed under Apache 2.0.
