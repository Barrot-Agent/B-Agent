"""Evidence records for Barrot-generated bundle delivery."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BundleDeliveryEvidence:
    path: str
    content_hash: str
    delivered_hash: str
    verified: bool
    reason: str = ""


def content_sha256(content: str) -> str:
    return "sha256:" + hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def file_sha256(path: str | Path) -> str:
    data = Path(path).read_bytes()
    return "sha256:" + hashlib.sha256(data).hexdigest()


def verify_bundle_delivery(
    *,
    path: str,
    content: str,
) -> BundleDeliveryEvidence:
    expected = content_sha256(content)
    target = Path(path).expanduser().resolve()

    if not target.exists():
        return BundleDeliveryEvidence(
            path=str(target),
            content_hash=expected,
            delivered_hash="",
            verified=False,
            reason="Delivered bundle file does not exist.",
        )

    actual = file_sha256(target)

    if actual != expected:
        return BundleDeliveryEvidence(
            path=str(target),
            content_hash=expected,
            delivered_hash=actual,
            verified=False,
            reason="Delivered bundle hash does not match source content.",
        )

    return BundleDeliveryEvidence(
        path=str(target),
        content_hash=expected,
        delivered_hash=actual,
        verified=True,
    )
