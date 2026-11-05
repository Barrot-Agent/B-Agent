"""Guard the full-suite coverage scope against package exclusions."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def test_full_repository_suite_measures_all_barrot_agent_packages():
    content = WORKFLOW.read_text(encoding="utf-8")
    assert "  full-suite:" in content
    full_suite = content.split("  full-suite:", 1)[1]
    assert "source = barrot_agent" in full_suite
    assert "--cov=barrot_agent" in full_suite
    assert "--cov-config=" in full_suite
    assert "--cov-report=term-missing:skip-covered" in full_suite
    assert "fail_under = 50" in full_suite
    assert "--cov-fail-under=50" in full_suite
    assert "--no-cov" not in full_suite
    for package in ("agi", "ingestion", "analysis", "monetization", "orchestration"):
        assert f"barrot_agent/{package}/" not in full_suite

    audit = (ROOT / ".github" / "workflows" / "dependency-audit.yml").read_text(encoding="utf-8")
    ingestion = (ROOT / ".github" / "workflows" / "xrp-public-ingestion.yml").read_text(encoding="utf-8")
    for workflow in (content, audit, ingestion):
        assert "actions/setup-python@v7" in workflow
        assert "actions/setup-python@v5" not in workflow
    assert "actions/checkout@v7" in ingestion
    assert "actions/checkout@v4" not in ingestion


def test_default_pyproject_coverage_config_includes_major_packages():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'omit = ["*/__pycache__/*", "tests/*"]' in pyproject
    assert "fail_under = 50" in pyproject
    for package in ("agi", "ingestion", "analysis", "monetization", "orchestration", "rendering"):
        assert f'"barrot_agent/{package}/*"' not in pyproject
    assert '"barrot_agent/smart_agent.py"' not in pyproject
