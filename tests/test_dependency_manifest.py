"""Regression tests for the primary runtime dependency manifests."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_RUNTIME_DISTRIBUTIONS = {"numpy", "pyjwt", "cryptography", "websockets"}


def _distribution_name(specification: str) -> str:
    value = specification.strip().strip('"').rstrip(",")
    return re.split(r"[<=>!~\[]", value, maxsplit=1)[0].strip().lower().replace("_", "-")


def _requirements_names(text: str) -> set[str]:
    names = set()
    for line in text.splitlines():
        value = line.strip()
        if not value or value.startswith("#") or value.startswith("-"):
            continue
        names.add(_distribution_name(value))
    return names


def _project_dependency_names(text: str) -> set[str]:
    # Read quoted TOML dependency entries without requiring Python 3.11 tomllib,
    # because the project declares Python >=3.10.
    block = text.split("[project]", 1)[-1].split("[tool.", 1)[0]
    dependencies = block.split("dependencies = [", 1)[-1].split("]", 1)[0]
    entries = re.findall(r'^\s*"([^"]+)"\s*,?\s*$', dependencies, re.MULTILINE)
    return {_distribution_name(entry) for entry in entries}


def test_imported_runtime_dependencies_are_in_primary_manifests() -> None:
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    missing_requirements = REQUIRED_RUNTIME_DISTRIBUTIONS - _requirements_names(requirements)
    missing_project = REQUIRED_RUNTIME_DISTRIBUTIONS - _project_dependency_names(pyproject)

    assert not missing_requirements, f"requirements.txt missing: {sorted(missing_requirements)}"
    assert not missing_project, f"pyproject.toml missing: {sorted(missing_project)}"


def test_development_manifest_inherits_runtime_dependencies() -> None:
    requirements_dev = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
    assert "-r requirements.txt" in requirements_dev
