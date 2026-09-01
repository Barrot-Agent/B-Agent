from barrot_agent.evolution.repository_awareness import (
    RepositoryAwarenessEngine,
)
from barrot_agent.evolution.self_consistency import (
    SelfConsistencyEngine,
)
from barrot_agent.evolution.self_model import (
    BarrotSelfModel,
)


def test_self_consistency_has_schema(tmp_path):
    model = BarrotSelfModel(
        RepositoryAwarenessEngine(tmp_path)
    )

    engine = SelfConsistencyEngine(model)

    result = engine.inspect()

    assert result["schema"] == (
        "BARROT-SELF-CONSISTENCY-1"
    )
    assert "issues" in result
    assert "statistics" in result


def test_self_consistency_detects_duplicate_components(
    tmp_path,
):
    (tmp_path / "a.py").write_text(
        "class TrustEngine:\n"
        "    pass\n",
        encoding="utf-8",
    )

    (tmp_path / "b.py").write_text(
        "class TrustEngine:\n"
        "    pass\n",
        encoding="utf-8",
    )

    model = BarrotSelfModel(
        RepositoryAwarenessEngine(tmp_path)
    )

    result = SelfConsistencyEngine(
        model
    ).inspect()

    duplicates = [
        issue
        for issue in result["issues"]
        if issue["type"]
        == "duplicate_component"
    ]

    assert duplicates
    assert duplicates[0]["name"] == "TrustEngine"
    assert duplicates[0]["component_type"] == "class"


def test_self_consistency_clean_repository(
    tmp_path,
):
    (tmp_path / "trust.py").write_text(
        "class TrustEngine:\n"
        "    pass\n",
        encoding="utf-8",
    )

    model = BarrotSelfModel(
        RepositoryAwarenessEngine(tmp_path)
    )

    result = SelfConsistencyEngine(
        model
    ).inspect()

    assert result["structurally_consistent"] is True
    assert result["issues"] == []
    assert result["statistics"]["duplicate_components"] == 0
    assert result["statistics"]["unparseable_files"] == 0
    assert (
        result["statistics"][
            "missing_internal_dependencies"
        ] == 0
    )


def test_self_consistency_detects_unparseable_file(
    tmp_path,
):
    (tmp_path / "broken.py").write_text(
        "class Broken(\n",
        encoding="utf-8",
    )

    model = BarrotSelfModel(
        RepositoryAwarenessEngine(tmp_path)
    )

    result = SelfConsistencyEngine(
        model
    ).inspect()

    assert result["structurally_consistent"] is False

    assert any(
        issue["type"] == "unparseable_file"
        for issue in result["issues"]
    )


def test_self_consistency_ignores_external_dependencies(
    tmp_path,
):
    (tmp_path / "app.py").write_text(
        "import json\n"
        "import pathlib\n"
        "import requests\n",
        encoding="utf-8",
    )

    model = BarrotSelfModel(
        RepositoryAwarenessEngine(tmp_path)
    )

    result = SelfConsistencyEngine(
        model
    ).inspect()

    assert result["structurally_consistent"] is True


def test_self_consistency_detects_missing_internal_dependency(
    tmp_path,
):
    (tmp_path / "app.py").write_text(
        "from barrot_agent.nonexistent import MissingThing\n",
        encoding="utf-8",
    )

    model = BarrotSelfModel(
        RepositoryAwarenessEngine(tmp_path)
    )

    result = SelfConsistencyEngine(
        model
    ).inspect()

    assert result["structurally_consistent"] is False

    assert any(
        issue["type"]
        == "missing_internal_dependency"
        for issue in result["issues"]
    )
