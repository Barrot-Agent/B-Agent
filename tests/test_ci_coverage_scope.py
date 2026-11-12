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
    assert "fail_under = 53" in full_suite
    assert "--cov-fail-under=53" in full_suite
    assert "--no-cov" not in full_suite
    for package in ("agi", "ingestion", "analysis", "monetization", "orchestration"):
        assert f"barrot_agent/{package}/" not in full_suite

    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'source = ["barrot_agent", "directive_platform", "data"]' in pyproject
    package_discovery = pyproject.split("[tool.setuptools.packages.find]", 1)[1]
    for package in ('"barrot_agent"', '"directive_platform"', '"data"'):
        assert package in package_discovery

    audit = (ROOT / ".github" / "workflows" / "dependency-audit.yml").read_text(encoding="utf-8")
    ingestion = (ROOT / ".github" / "workflows" / "xrp-public-ingestion.yml").read_text(encoding="utf-8")
    for workflow in (content, audit, ingestion):
        assert "actions/setup-python@v7" in workflow
        assert "actions/setup-python@v5" not in workflow
    assert "actions/checkout@v7" in ingestion
    assert "actions/checkout@v4" not in ingestion


def test_integration_full_suite_runs_once_on_pull_request_not_duplicate_push():
    content = WORKFLOW.read_text(encoding="utf-8")
    push = content.split("  push:", 1)[1].split("  pull_request:", 1)[0]
    pull_request = content.split("  pull_request:", 1)[1].split("  workflow_dispatch:", 1)[0]
    assert "branches: [main]" in push
    assert "integration/**" not in push
    assert "branches: [main]" in pull_request
    assert "  full-suite:" in content
