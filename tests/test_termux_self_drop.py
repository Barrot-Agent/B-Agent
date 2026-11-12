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


def test_termux_drop_round_trip_is_deterministic_and_idempotent(tmp_path):
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
    assert "no write or overwrite" in second.error.lower() or "no write or overwrite" in second.output.lower()
    assert first_content == content
    assert second_content == content
    assert first_content == second_content


def test_termux_drop_refuses_to_overwrite_existing_user_file(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path / "user_owned.txt"
    original = "USER DATA MUST SURVIVE\n"
    target.write_text(original, encoding="utf-8")

    action = Action(
        type="TERMUX_DROP",
        args={
            "path": str(target),
            "content": "REPLACEMENT MUST BE REJECTED\n",
        },
    )

    result = executor.execute(action)

    assert result.success is False
    assert "existing user data was preserved" in result.error.lower()
    assert target.read_text(encoding="utf-8") == original


def test_termux_drop_bytes_is_create_only_and_idempotent(tmp_path):
    bridge = TermuxBridge(allowed_roots=(str(tmp_path),))
    target = tmp_path / "binary_bundle.bin"

    first = bridge.drop_bytes(path=str(target), content=b"\x00\x01")
    repeated = bridge.drop_bytes(path=str(target), content=b"\x00\x01")
    conflict = bridge.drop_bytes(path=str(target), content=b"\x02\x03")

    assert first.success is True
    assert repeated.success is True
    assert "no write or overwrite" in repeated.reason.lower()
    assert conflict.success is False
    assert "existing user data was preserved" in conflict.reason.lower()
    assert target.read_bytes() == b"\x00\x01"


def test_termux_drop_rejects_symlink_target_without_mutating_referent(tmp_path):
    bridge = TermuxBridge(allowed_roots=(str(tmp_path),))
    referent = tmp_path / "user_owned.txt"
    referent.write_text("KEEP THIS FILE\n", encoding="utf-8")
    link = tmp_path / "bundle_link.txt"
    link.symlink_to(referent)

    result = bridge.drop_text(path=str(link), content="DO NOT FOLLOW SYMLINK\n")

    assert result.success is False
    assert "symlink" in result.reason.lower()
    assert referent.read_text(encoding="utf-8") == "KEEP THIS FILE\n"


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
