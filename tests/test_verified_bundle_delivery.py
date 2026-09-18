from barrot_agent.orchestration.action_executor import BarrotActionExecutor
from barrot_agent.orchestration.verified_bundle_delivery import (
    deliver_verified_bundle,
)


def test_verified_bundle_delivery_completes_full_chain(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path / "verified_bundle.py"
    content = '''def probe():
    return "VERIFIED_BUNDLE_OK"
'''

    result = deliver_verified_bundle(
        executor,
        path=str(target),
        content=content,
    )

    assert result.validation.valid is True
    assert result.validation.sha256.startswith("sha256:")

    assert result.delivery.success is True

    assert result.evidence.verified is True
    assert result.evidence.content_hash == result.evidence.delivered_hash

    namespace = {}
    exec(
        compile(
            target.read_text(encoding="utf-8"),
            str(target),
            "exec",
        ),
        namespace,
    )

    assert namespace["probe"]() == "VERIFIED_BUNDLE_OK"


def test_verified_bundle_delivery_rejects_invalid_python(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path / "invalid_verified_bundle.py"

    try:
        deliver_verified_bundle(
            executor,
            path=str(target),
            content="def broken(:\n",
        )
    except ValueError as exc:
        assert "validation failed" in str(exc).lower()
    else:
        raise AssertionError("Expected validation failure")

    assert not target.exists()


def test_verified_bundle_delivery_preserves_workspace_boundary(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path.parent / "verified_bundle_escape.py"

    result = deliver_verified_bundle(
        executor,
        path=str(target),
        content='x = "SAFE"\n',
    )

    assert result.delivery.success is False
    assert result.evidence.verified is False
    assert not target.exists()
