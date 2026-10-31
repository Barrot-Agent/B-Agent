from barrot_agent.orchestration.action_executor import BarrotActionExecutor
from barrot_agent.orchestration.autonomous_actions import deliver_autonomous_bundle


def test_barrot_can_drop_and_execute_real_python_bundle(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path / "generated_bundle.py"

    content = '''def barrot_bundle_probe():
    return "BARROT_REAL_BUNDLE_EXECUTED"
'''

    result = deliver_autonomous_bundle(
        executor,
        path=str(target),
        content=content,
    )

    assert result.success is True
    assert target.exists()

    namespace = {}
    exec(
        compile(
            target.read_text(encoding="utf-8"),
            str(target),
            "exec",
        ),
        namespace,
    )

    assert namespace["barrot_bundle_probe"]() == "BARROT_REAL_BUNDLE_EXECUTED"


def test_autonomous_bundle_rejects_invalid_python(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path / "invalid_bundle.py"

    from barrot_agent.orchestration.bundle_validation import BundleValidationError

    try:
        deliver_autonomous_bundle(
            executor,
            path=str(target),
            content="def broken(:\n",
        )
    except BundleValidationError as exc:
        assert "syntax error" in str(exc).lower()
    else:
        raise AssertionError("Expected BundleValidationError")

    assert not target.exists()
