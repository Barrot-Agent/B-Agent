from __future__ import annotations

from pathlib import Path

from barrot_agent.repository.causality import RepositoryCausality

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_causality_excludes_nested_git_repository(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()

    target = root / "barrot_agent" / "target.py"
    target.parent.mkdir(parents=True)
    target.write_text("VALUE = 1\n", encoding="utf-8")

    dependent = root / "barrot_agent" / "consumer.py"
    dependent.write_text(
        "from barrot_agent.target import VALUE\n",
        encoding="utf-8",
    )

    nested = root / "B-Agent"
    nested.mkdir()
    (nested / ".git").mkdir()
    (nested / "nested.py").write_text(
        "from barrot_agent.target import VALUE\n",
        encoding="utf-8",
    )

    causality = RepositoryCausality(root)

    assert all("B-Agent" not in str(path) for path in causality.python_files)

    impact = causality.analyze("barrot_agent/target.py")

    assert impact.target == "barrot_agent/target.py"
    assert "barrot_agent.consumer" in impact.dependents
    assert not any("B-Agent" in value for value in impact.dependents)


def test_causality_builds_dependencies_and_related_tests(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    target = root / "barrot_agent" / "target.py"
    target.parent.mkdir(parents=True)
    target.write_text(
        "import json\nfrom pathlib import Path\n",
        encoding="utf-8",
    )

    test_file = root / "tests" / "test_target.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text(
        "def test_target():\n    pass\n",
        encoding="utf-8",
    )

    causality = RepositoryCausality(root)
    impact = causality.analyze("barrot_agent/target.py")

    assert "json" in impact.dependencies
    assert "pathlib" in impact.dependencies
    assert impact.related_tests == ["tests/test_target.py"]
    assert impact.risk_level == "low"


def _load_repo_script(path: Path, name: str):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scheduled_issue_and_metrics_workflows_are_read_only() -> None:
    workflows = REPO_ROOT / ".github" / "workflows"
    auto_resolve = (workflows / "auto-resolve-issues.yml").read_text(encoding="utf-8")
    autonomous = (workflows / "barrot-autonomous-resolver.yml").read_text(encoding="utf-8")
    digest = (workflows / "daily-digest.yml").read_text(encoding="utf-8")
    self_schedule = (workflows / "self-schedule.yml").read_text(encoding="utf-8")
    gumroad = (workflows / "gumroad-metrics.yml").read_text(encoding="utf-8")

    assert "issues: write" not in auto_resolve
    assert "--apply" not in auto_resolve
    assert "issues: write" not in autonomous
    assert "pull-requests: write" not in autonomous
    assert "gh issue create" not in autonomous
    assert "gh issue edit" not in autonomous
    assert "gh pr edit" not in autonomous
    assert "AUTO_ASSIGNEE" not in autonomous
    assert "issues: write" not in digest
    assert "gh issue create" not in digest
    assert "issues: write" not in self_schedule
    assert "--apply" not in self_schedule
    assert "contents: write" not in gumroad
    assert "git push" not in gumroad
    assert "git commit" not in gumroad
    for workflow in (auto_resolve, autonomous, digest, self_schedule, gumroad):
        assert "actions/upload-artifact@v4" in workflow


def test_issue_resolver_defaults_to_no_external_mutation(monkeypatch) -> None:
    module = _load_repo_script(REPO_ROOT / "scripts" / "resolve_issue.py", "resolve_issue_dry_run_test")
    calls: list[tuple[str, ...]] = []
    monkeypatch.setattr(module, "get_issue", lambda number: {
        "number": number,
        "title": "[Auto] Workflow failing: CI",
        "body": "",
        "state": "OPEN",
    })
    monkeypatch.setattr(module, "find_workflow_file", lambda name: {"name": name, "id": 7, "path": ".github/workflows/ci.yml"})
    monkeypatch.setattr(module, "get_latest_run_status", lambda workflow_id: {
        "conclusion": "success",
        "id": 99,
        "html_url": "https://example.invalid/actions/runs/99",
    })
    monkeypatch.setattr(module, "gh", lambda *args: calls.append(tuple(args)) or "")

    module.resolve(123)

    assert calls == []

    module.resolve(123, apply=True)

    assert calls[0][:4] == ("issue", "comment", "123", "--body")
    assert ("issue", "close", "123") in calls


def test_self_scheduler_defaults_to_no_issue_creation(monkeypatch) -> None:
    module = _load_repo_script(REPO_ROOT / "scripts" / "self_schedule.py", "self_schedule_dry_run_test")
    calls: list[tuple[str, ...]] = []

    class Result:
        returncode = 0
        stdout = "https://example.invalid/issues/1"
        stderr = ""

    monkeypatch.setattr(module.subprocess, "run", lambda command, **kwargs: calls.append(tuple(command)) or Result())

    module.open_gap_issue("rss", 8.0, 6)

    assert calls == []

    module.open_gap_issue("rss", 8.0, 6, apply=True)

    assert calls[0][:3] == ("gh", "issue", "create")
    assert calls[1][:3] == ("gh", "issue", "edit")


def test_gumroad_metrics_never_logs_raw_product_response(tmp_path: Path, monkeypatch, capsys) -> None:
    import json

    module = _load_repo_script(REPO_ROOT / "scripts" / "gumroad_metrics.py", "gumroad_metrics_privacy_test")
    monkeypatch.setattr(module, "TOKEN", "test-token")
    monkeypatch.setattr(module, "OUT_PATH", str(tmp_path / "metrics.json"))
    monkeypatch.setattr(module, "fetch_products", lambda: {
        "success": True,
        "products": [{
            "name": "XRP Signal Service",
            "short_url": "https://gumroad.com/l/opvxi",
            "sales_count": 4,
            "price": 2500,
            "currency": "usd",
            "published": True,
            "private_provider_field": "MUST_NOT_APPEAR_IN_LOGS",
        }],
    })

    module.main()

    output = capsys.readouterr().out
    assert "MUST_NOT_APPEAR_IN_LOGS" not in output
    aggregate = json.loads((tmp_path / "metrics.json").read_text(encoding="utf-8"))
    assert aggregate["sales_count"] == 4
    assert "private_provider_field" not in aggregate
