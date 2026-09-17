from barrot_agent.orchestration.action_executor import BarrotActionExecutor
from barrot_agent.orchestration.actions import Action
from barrot_agent.termux import TermuxBridge


def test_termux_drop_writes_bundle_file(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path / "barrot_drop_probe.txt"
    content = "BARROT_SELF_DROP_OK\n"

    action = Action(
        type="TERMUX_DROP",
        args={
            "path": str(target),
            "content": content,
        },
    )

    result = executor.execute(action)

    assert result.success is True
    assert target.exists()
    assert target.read_text(encoding="utf-8") == content


def test_termux_drop_round_trip_is_deterministic(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path / "barrot_drop_round_trip.txt"
    content = "BARROT_ROUND_TRIP_OK\n"

    action = Action(
        type="TERMUX_DROP",
        args={
            "path": str(target),
            "content": content,
        },
    )

    first = executor.execute(action)
    first_content = target.read_text(encoding="utf-8")

    second = executor.execute(action)
    second_content = target.read_text(encoding="utf-8")

    assert first.success is True
    assert second.success is True
    assert first_content == content
    assert second_content == content
    assert first_content == second_content


def test_termux_drop_rejects_path_outside_workspace(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path.parent / "barrot_escape_probe.txt"

    action = Action(
        type="TERMUX_DROP",
        args={
            "path": str(target),
            "content": "SHOULD_NOT_BE_WRITTEN\n",
        },
    )

    result = executor.execute(action)

    assert result.success is False
    assert not target.exists()
    assert "outside approved" in result.error.lower()
