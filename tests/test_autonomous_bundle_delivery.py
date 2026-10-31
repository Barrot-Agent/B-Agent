from barrot_agent.orchestration.action_executor import BarrotActionExecutor
from barrot_agent.orchestration.autonomous_actions import deliver_autonomous_bundle


def test_autonomous_layer_can_deliver_bundle(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path / "autonomous_bundle.txt"
    content = "BARROT_AUTONOMOUS_BUNDLE_OK\n"

    result = deliver_autonomous_bundle(
        executor,
        path=str(target),
        content=content,
    )

    assert result.success is True
    assert target.exists()
    assert target.read_text(encoding="utf-8") == content


def test_autonomous_layer_preserves_workspace_boundary(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path.parent / "autonomous_escape.txt"

    result = deliver_autonomous_bundle(
        executor,
        path=str(target),
        content="MUST_NOT_ESCAPE\n",
    )

    assert result.success is False
    assert not target.exists()
