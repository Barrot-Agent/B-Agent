from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dependency_audit_covers_every_pyproject_optional_extra() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    extras = project.get("project", {}).get("optional-dependencies", {})
    assert {"integrations", "music"}.issubset(extras)

    workflow = (ROOT / ".github" / "workflows" / "dependency-audit.yml").read_text(
        encoding="utf-8"
    )
    assert 'project.get("project", {}).get("optional-dependencies", {})' in workflow
    assert "for name, dependencies in sorted(extras.items())" in workflow
    assert "pyproject-extras" in workflow
    assert 'pip-audit -r "$requirements_file" --strict' in workflow
    assert "PYPROJECT_OPTIONAL_EXTRAS" in workflow
    assert "steps.pyproject_optional_extras.outcome" in workflow
