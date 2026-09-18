"""Validated, delivered, and hash-verified Barrot implementation bundles."""

from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .action_executor import ActionResult, BarrotActionExecutor

from .bundle_delivery import BundleDelivery, deliver_bundle
from .bundle_evidence import BundleDeliveryEvidence, verify_bundle_delivery
from .bundle_validation import BundleValidation, validate_python_bundle


@dataclass(frozen=True)
class VerifiedBundleDelivery:
    validation: BundleValidation
    delivery: Any
    evidence: BundleDeliveryEvidence


def deliver_verified_bundle(
    executor: Any,
    *,
    path: str,
    content: str,
) -> VerifiedBundleDelivery:
    validation = validate_python_bundle(
        path=path,
        content=content,
    )

    if not validation.valid:
        raise ValueError(
            f"Bundle validation failed: {validation.reason}"
        )

    delivery = deliver_bundle(
        executor,
        BundleDelivery(
            path=path,
            content=content,
        ),
    )

    evidence = verify_bundle_delivery(
        path=path,
        content=content,
    )

    return VerifiedBundleDelivery(
        validation=validation,
        delivery=delivery,
        evidence=evidence,
    )
