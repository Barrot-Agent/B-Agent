from pathlib import Path

WORKFLOW = Path(".github/workflows/dependency-audit.yml").read_text(encoding="utf-8")
CI = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
DEV_REQUIREMENTS = Path("requirements-dev.txt").read_text(encoding="utf-8")
ROOT_REQUIREMENTS = Path("requirements.txt").read_text(encoding="utf-8")
HF_REQUIREMENTS = Path("hf_space/requirements.txt").read_text(encoding="utf-8")
LEGACY_REQUIREMENTS = Path("legacy/requirements_legacy.txt").read_text(encoding="utf-8")


def test_dependency_audit_is_scheduled_and_runs_on_dependency_changes():
    assert "schedule:" in WORKFLOW
    assert "pull_request:" in WORKFLOW
    assert "'requirements*.txt'" in WORKFLOW
    assert "'pyproject.toml'" in WORKFLOW
    assert "'hf_space/requirements.txt'" in WORKFLOW
    assert "'legacy/requirements_legacy.txt'" in WORKFLOW
    assert "workflow_dispatch:" in WORKFLOW


def test_dependency_audit_is_read_only_and_does_not_persist_credentials():
    assert "permissions:\n  contents: read" in WORKFLOW
    assert "persist-credentials: false" in WORKFLOW
    assert "contents: write" not in WORKFLOW
    assert "pull-requests: write" not in WORKFLOW
    assert "actions: write" not in WORKFLOW
    assert "secrets." not in WORKFLOW
    assert "GH_TOKEN" not in WORKFLOW
    assert "git push" not in WORKFLOW
    assert "gh secret set" not in WORKFLOW
    assert "--fix" not in WORKFLOW


def test_audit_tool_is_pinned_and_reports_are_uploaded_even_on_failure():
    assert "pip-audit==2.10.1" in WORKFLOW
    assert "if: always()" in WORKFLOW
    assert "upload-artifact@v4" in WORKFLOW
    assert "retention-days: 30" in WORKFLOW
    assert "format json" in WORKFLOW


def test_matrix_covers_root_hf_space_and_legacy_python_requirements():
    assert "requirements-dev.txt" in WORKFLOW
    assert "hf_space/requirements.txt" in WORKFLOW
    assert "legacy/requirements_legacy.txt" in WORKFLOW
    assert "-r requirements.txt" in DEV_REQUIREMENTS
    assert ROOT_REQUIREMENTS.strip()
    assert HF_REQUIREMENTS.strip()
    assert LEGACY_REQUIREMENTS.strip()


def test_ci_registers_dependency_audit_workflow_regression_tests():
    assert "tests/test_dependency_audit_workflow.py" in CI
