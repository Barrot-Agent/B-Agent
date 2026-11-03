from __future__ import annotations

from pathlib import Path

from barrot_agent.repository.causality import RepositoryCausality


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


def test_cross_analysis_workflow_is_read_only_and_artifact_based() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    workflow = (
        repo_root / ".github" / "workflows" / "cross-analysis.yml"
    ).read_text(encoding="utf-8")
    lowered = workflow.lower()

    assert "permissions:\\n  contents: read" in workflow
    assert "persist-credentials: false" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "retention-days: 30" in workflow
    assert "if-no-files-found: error" in workflow
    assert "conclusion == 'success'" in workflow

    for output in (
        "ping-pongings/knowledge-base/entity_cooccurrence.json",
        "ping-pongings/knowledge-base/sentiment_shift.json",
        "ping-pongings/knowledge-base/entity_sentiment_profile.json",
        "web/entity_cooccurrence.json",
        "web/sentiment_shift.json",
        "web/entity_sentiment_profile.json",
    ):
        assert output in workflow

    for forbidden in (
        "contents: write",
        "git add",
        "git commit",
        "git push",
        "persist-credentials: true",
        "secrets.",
    ):
        assert forbidden not in lowered
