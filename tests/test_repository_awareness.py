
from pathlib import Path

from barrot_agent.evolution.repository_awareness import (
    RepositoryAwarenessEngine,
)


def test_repository_awareness_indexes_python_files(tmp_path):
    source = tmp_path / "barrot_agent"
    source.mkdir()

    (source / "example.py").write_text(
        """
from barrot_agent.trust import TrustEngine

class ExampleEngine:
    def execute(self):
        return True
""",
        encoding="utf-8",
    )

    engine = RepositoryAwarenessEngine(tmp_path)
    manifest = engine.build()

    assert manifest["schema"] == "BARROT-REPO-AWARENESS-1"
    assert manifest["statistics"]["python_files"] == 1

    file_data = manifest["files"][0]

    assert file_data["path"] == "barrot_agent/example.py"
    assert "barrot_agent.trust.TrustEngine" in file_data["imports"]
    assert file_data["classes"][0]["name"] == "ExampleEngine"


def test_repository_awareness_finds_components(tmp_path):
    source = tmp_path / "component.py"

    source.write_text(
        """
class TrustAdapter:
    def execute(self):
        return True
""",
        encoding="utf-8",
    )

    engine = RepositoryAwarenessEngine(tmp_path)

    matches = engine.find_component("TrustAdapter")

    assert len(matches) == 1
    assert matches[0]["type"] == "class"
    assert matches[0]["name"] == "TrustAdapter"


def test_cross_analysis_has_explicit_layers(tmp_path):
    (tmp_path / "trust.py").write_text(
        "class TrustEngine:\n    pass\n",
        encoding="utf-8",
    )

    engine = RepositoryAwarenessEngine(tmp_path)
    engine.build()

    analysis = engine.cross_analysis()

    assert analysis["schema"] == "BARROT-CROSS-ANALYSIS-1"
    assert "trust_layer" in analysis
    assert "integration_layer" in analysis
    assert "test_layer" in analysis
