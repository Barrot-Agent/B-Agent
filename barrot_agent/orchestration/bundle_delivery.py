"""Validated delivery of Barrot-generated implementation bundles."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .action_executor import ActionResult, BarrotActionExecutor

from .actions import Action


@dataclass(frozen=True)
class BundleDelivery:
    path: str
    content: str


class BundleDeliveryError(ValueError):
    """Raised when a bundle cannot be safely delivered."""


def deliver_bundle(
    executor: Any,
    bundle: BundleDelivery,
) -> ActionResult:
    path = bundle.path
    content = bundle.content

    if not isinstance(path, str) or not path.strip():
        raise BundleDeliveryError("Bundle path must be a non-empty string")

    if not isinstance(content, str):
        raise BundleDeliveryError("Bundle content must be a string")

    action = Action(
        type="TERMUX_DROP",
        args={
            "path": path,
            "content": content,
        },
    )

    return executor.execute(action)


def deliver_bundle_file(
    executor: Any,
    *,
    path: str,
    content: str,
) -> ActionResult:
    return deliver_bundle(
        executor,
        BundleDelivery(path=path, content=content),
    )


def verify_delivery(result: ActionResult, path: str) -> Path:
    if not result.success:
        raise BundleDeliveryError(
            f"Bundle delivery failed: {result.error}"
        )

    target = Path(path).expanduser().resolve()

    if not target.exists():
        raise BundleDeliveryError(
            f"Bundle delivery reported success but file is missing: {target}"
        )

    return target
