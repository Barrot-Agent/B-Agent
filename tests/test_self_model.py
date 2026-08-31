from barrot_agent.evolution.self_model import BarrotSelfModel


def test_self_model_has_unified_schema(tmp_path):
    from barrot_agent.evolution.repository_awareness import (
        RepositoryAwarenessEngine,
    )

    engine = BarrotSelfModel(
        RepositoryAwarenessEngine(tmp_path)
    )

    snapshot = engine.snapshot()

    assert snapshot["schema"] == "BARROT-SELF-MODEL-1"
    assert "trust" in snapshot
    assert "architecture" in snapshot
    assert "evidence" in snapshot
    assert "calibration" in snapshot


def test_self_model_finds_component(tmp_path):
    from barrot_agent.evolution.repository_awareness import (
        RepositoryAwarenessEngine,
    )

    (tmp_path / "trust.py").write_text(
        "class TrustEngine:\\n    pass\\n",
        encoding="utf-8",
    )

    model = BarrotSelfModel(
        RepositoryAwarenessEngine(tmp_path)
    )

    result = model.component("TrustEngine")

    assert result["count"] == 1
    assert result["matches"][0]["name"] == "TrustEngine"


def test_self_model_ask_trust(tmp_path):
    from barrot_agent.evolution.repository_awareness import (
        RepositoryAwarenessEngine,
    )

    (tmp_path / "trust.py").write_text(
        "class TrustEngine:\\n    pass\\n",
        encoding="utf-8",
    )

    model = BarrotSelfModel(
        RepositoryAwarenessEngine(tmp_path)
    )

    result = model.ask("What does my trust architecture look like?")

    assert result["intent"] == "trust"
    assert "trust_architecture" in result["result"]
