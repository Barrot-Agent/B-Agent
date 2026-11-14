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
    assert "fail_under = 62" in pyproject
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


def test_integration_full_suite_runs_once_on_push_not_duplicate_pull_request():
    content = WORKFLOW.read_text(encoding="utf-8")
    push = content.split("  push:", 1)[1].split("  pull_request:", 1)[0]
    pull_request = content.split("  pull_request:", 1)[1].split("  workflow_dispatch:", 1)[0]
    assert 'branches: [main, "integration/**"]' in push
    assert "branches: [main]" in pull_request
    integration_pr_skip = "if: github.event_name != 'pull_request' || !startsWith(github.head_ref, 'integration/')"
    tests = content.split("  tests:", 1)[1].split("  full-suite:", 1)[0]
    full_suite = content.split("  full-suite:", 1)[1]
    assert integration_pr_skip in tests
    assert integration_pr_skip in full_suite
    assert "  full-suite:" in content


def test_dependency_audit_runs_for_safety_and_ci_changes():
    audit = (ROOT / ".github" / "workflows" / "dependency-audit.yml").read_text(encoding="utf-8")
    required_paths = (
        ".github/workflows/ci.yml",
        ".github/workflows/coinbase-paper-trader.yml",
        "barrot_agent/orchestration/mcp_orchestrator.py",
        "legacy/app_legacy.py",
        "scripts/coinbase_paper_trader.py",
        "tests/test_mcp_orchestrator_safety.py",
        "tests/test_paper_trader_*.py",
        "tests/test_ci_coverage_scope.py",
    )
    for path in required_paths:
        assert audit.count(f'"{path}"') >= 2, f"dependency audit path filter missing push/PR coverage: {path}"
