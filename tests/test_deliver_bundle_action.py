from barrot_agent.orchestration.action_executor import BarrotActionExecutor
from barrot_agent.orchestration.actions import Action, parse_actions


def test_deliver_bundle_action_is_allowed():
    actions = parse_actions(
        {
            "actions": [
                {
                    "type": "DELIVER_BUNDLE",
                    "args": {
                        "path": "generated.py",
                        "content": 'x = "OK"\n',
                    },
                }
            ]
        }
    )

    assert len(actions) == 1
    assert actions[0].type == "DELIVER_BUNDLE"


def test_deliver_bundle_action_validates_delivers_and_verifies(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path / "generated.py"

    action = Action(
        type="DELIVER_BUNDLE",
        args={
            "path": str(target),
            "content": 'def probe():\n    return "DELIVER_BUNDLE_OK"\n',
        },
    )

    result = executor.execute(action)

    assert result.success is True
    assert target.exists()
    assert "sha256:" in result.output


def test_deliver_bundle_action_rejects_invalid_python(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path / "invalid.py"

    action = Action(
        type="DELIVER_BUNDLE",
        args={
            "path": str(target),
            "content": "def broken(:\n",
        },
    )

    result = executor.execute(action)

    assert result.success is False
    assert not target.exists()


def test_deliver_bundle_action_preserves_workspace_boundary(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path.parent / "escape.py"

    action = Action(
        type="DELIVER_BUNDLE",
        args={
            "path": str(target),
            "content": 'x = "NO_ESCAPE"\n',
        },
    )

    result = executor.execute(action)

    assert result.success is False
    assert not target.exists()
