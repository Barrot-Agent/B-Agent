from pathlib import Path


WORKFLOW = Path(".github/workflows/dependency-audit.yml").read_text(encoding="utf-8")
REQUIREMENTS = Path("requirements.txt").read_text(encoding="utf-8")
DEV_REQUIREMENTS = Path("requirements-dev.txt").read_text(encoding="utf-8")
PYPROJECT = Path("pyproject.toml").read_text(encoding="utf-8")


def test_dependency_audit_is_scheduled_and_runs_on_dependency_changes():
    assert "schedule:" in WORKFLOW
    assert "pull_request:" in WORKFLOW
    assert "'requirements*.txt'" in WORKFLOW
    assert "'pyproject.toml'" in WORKFLOW
    assert "workflow_dispatch:" in WORKFLOW


def test_dependency_audit_is_read_only_and_does_not_persist_checkout_credentials():
    assert "permissions:\n  contents: read" in WORKFLOW
    assert "persist-credentials: false" in WORKFLOW
    assert "contents: write" not in WORKFLOW
    assert "pull-requests: write" not in WORKFLOW
    assert "actions: write" not in WORKFLOW
    assert "GH_TOKEN" not in WORKFLOW
    assert "git push" not in WORKFLOW
    assert "gh secret set" not in WORKFLOW
    assert "workflow_dispatch" in WORKFLOW


def test_dependency_audit_covers_the_dev_manifest_that_includes_production():
    assert "-r requirements.txt" in DEV_REQUIREMENTS
    assert "--requirement requirements-dev.txt" in WORKFLOW
    assert "pip-audit" in WORKFLOW
    assert "upload-artifact@v4" in WORKFLOW
    assert "if: always()" in WORKFLOW


def test_repository_dependency_reproducibility_gaps_are_explicit():
    assert "torch>=2.0.0" in REQUIREMENTS
    assert "torch>=2.0.0" in PYPROJECT
    assert "requires-python = \">=3.10\"" in PYPROJECT
    assert "python-version: \"3.11\"" in WORKFLOW
