from barrot_agent.orchestration.action_executor import BarrotActionExecutor
from barrot_agent.orchestration.bundle_delivery import (
    BundleDelivery,
    BundleDeliveryError,
    deliver_bundle,
    verify_delivery,
)


def test_barrot_can_deliver_bundle_through_existing_termux_drop(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path / "barrot_generated_bundle.txt"
    content = "BARROT_GENERATED_BUNDLE_OK\n"

    result = deliver_bundle(
        executor,
        BundleDelivery(
            path=str(target),
            content=content,
        ),
    )

    assert result.success is True
    delivered = verify_delivery(result, str(target))
    assert delivered.read_text(encoding="utf-8") == content


def test_bundle_delivery_preserves_termux_workspace_safety(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path.parent / "barrot_bundle_escape.txt"

    result = deliver_bundle(
        executor,
        BundleDelivery(
            path=str(target),
            content="MUST_NOT_ESCAPE\n",
        ),
    )

    assert result.success is False
    assert not target.exists()


def test_bundle_delivery_rejects_invalid_path(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    try:
        deliver_bundle(
            executor,
            BundleDelivery(
                path="",
                content="invalid",
            ),
        )
    except BundleDeliveryError as exc:
        assert "path" in str(exc).lower()
    else:
        raise AssertionError("Expected BundleDeliveryError")
