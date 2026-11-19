"""Guard the full-suite coverage scope against package exclusions."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def test_full_repository_suite_measures_all_distributable_packages():
    content = WORKFLOW.read_text(encoding="utf-8")
    assert "  full-suite:" in content
    full_suite = content.split("  full-suite:", 1)[1]
    assert "source = barrot_agent,directive_platform,data" in full_suite
    for package in ("barrot_agent", "directive_platform", "data"):
        assert f"--cov={package}" in full_suite
    assert "--cov-config=" in full_suite
    assert "--cov-report=term-missing:skip-covered" in full_suite
    assert "fail_under = 62" in full_suite
    assert "--cov-fail-under=62" in full_suite
    for active_test_path in (
        "legacy/tests/test_email_integration.py",
        "legacy/tests/test_transformative_insights.py",
        ".barrot/autonomous_tasks/test_math_task.py",
    ):
        assert active_test_path in full_suite
    assert "--no-cov" not in full_suite
    core_gate_marker = "      - name: Preserve legacy core-package coverage floor"
    assert core_gate_marker in full_suite
    broad_coverage = full_suite.split(core_gate_marker, 1)[0]
    for package in ("agi", "ingestion", "analysis", "monetization", "orchestration"):
        assert f"barrot_agent/{package}/" not in broad_coverage

    core_gate = full_suite.split(core_gate_marker, 1)[1].split("      - name:", 1)[0]
    assert "python -m coverage report" in core_gate
    assert '--include="barrot_agent/*"' in core_gate
    assert "--fail-under=70" in core_gate
    for package in ("agi", "ingestion", "analysis", "monetization", "orchestration"):
        assert f"barrot_agent/{package}/*" in core_gate

    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'source = ["barrot_agent", "directive_platform", "data"]' in pyproject
    # Keep local/scoped pytest runs ungated; CI enforces the 62% full-suite floor.
    assert "fail_under = 0" in pyproject
    assert "# Full-suite thresholds are enforced in .github/workflows/ci.yml; local subset runs stay ungated." in pyproject
    package_discovery = pyproject.split("[tool.setuptools.packages.find]", 1)[1]
    for package in ('"barrot_agent"', '"directive_platform"', '"data"'):
        assert package in package_discovery

    audit = (ROOT / ".github" / "workflows" / "dependency-audit.yml").read_text(encoding="utf-8")
    ingestion = (ROOT / ".github" / "workflows" / "xrp-public-ingestion.yml").read_text(encoding="utf-8")
    setup_python_sha = "6d4fd22b20465ccc0f7354476588e8df7c9ca0e0"
    checkout_sha = "3d3c42e5aac5ba805825da76410c181273ba90b1"
    upload_artifact_sha = "cf430e030ddbb5b0abf93d22962f4752f3646cd9"
    cache_sha = "0057852bfaa89a56745cba8c7296529d2fc39830"
    for workflow in (content, audit, ingestion):
        assert f"actions/setup-python@{setup_python_sha}" in workflow
        assert "actions/setup-python@v7" not in workflow
        assert f"actions/checkout@{checkout_sha}" in workflow
        assert "actions/checkout@v7" not in workflow
    assert f"actions/upload-artifact@{upload_artifact_sha}" in ingestion
    assert "actions/upload-artifact@v7" not in ingestion
    assert f"actions/cache/restore@{cache_sha}" in ingestion
    assert f"actions/cache/save@{cache_sha}" in ingestion
    assert "actions/cache/restore@v4" not in ingestion
    assert "actions/cache/save@v4" not in ingestion


def test_integration_full_suite_runs_on_exact_push_and_pull_request_heads():
    content = WORKFLOW.read_text(encoding="utf-8")
    push = content.split("  push:", 1)[1].split("  pull_request:", 1)[0]
    pull_request = content.split("  pull_request:", 1)[1].split("  workflow_dispatch:", 1)[0]
    assert 'branches: [main, "integration/**"]' in push
    assert "branches: [main]" in pull_request
    assert "  full-suite:" in content

    # Both jobs must run on integration pushes and on the pull-request head.
    # A push-only success cannot verify the exact PR head, and skipping PR CI
    # would make the merge gate rely on a different event's run.
    for job_name in ("tests", "full-suite"):
        section = content.split(f"  {job_name}:", 1)[1].split("\\n  ", 1)[0]
        job_header = section.split("    steps:", 1)[0]
        assert "if:" not in job_header


def test_dependency_audit_runs_for_safety_and_ci_changes():
    audit = (ROOT / ".github" / "workflows" / "dependency-audit.yml").read_text(encoding="utf-8")
    triggers = audit.split("permissions:", 1)[0]
    assert 'branches: [main, "integration/**"]' in triggers
    assert "pull_request:\n    branches: [main]" in triggers
    assert "paths:" not in triggers
    assert "contents: read" in audit
    for manifest_command in (
        "pip-audit -r requirements.txt --strict",
        "pip-audit -r requirements-dev.txt --strict",
        "pip-audit -r requirements-integrations.txt --strict",
        "pip-audit -r hf_space/requirements.txt --strict",
        "pip-audit -r legacy/requirements_legacy.txt --strict",
        'pip-audit -r "$RUNNER_TEMP/pyproject-requirements.txt" --strict',
    ):
        assert manifest_command in audit
