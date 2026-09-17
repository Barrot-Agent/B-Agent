"""Deterministic validation for Barrot implementation bundles."""

from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class BundleValidation:
    valid: bool
    path: str
    content_length: int
    sha256: str
    reason: str = ""


class BundleValidationError(ValueError):
    """Raised when a bundle fails deterministic validation."""


def validate_python_bundle(
    *,
    path: str,
    content: str,
) -> BundleValidation:
    if not isinstance(path, str) or not path.strip():
        raise BundleValidationError(
            "Bundle path must be a non-empty string"
        )

    if not isinstance(content, str):
        raise BundleValidationError(
            "Bundle content must be a string"
        )

    try:
        ast.parse(content, filename=path)
    except SyntaxError as exc:
        return BundleValidation(
            valid=False,
            path=path,
            content_length=len(content),
            sha256="",
            reason=f"Python syntax error: {exc}",
        )

    import hashlib

    digest = hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

    return BundleValidation(
        valid=True,
        path=path,
        content_length=len(content),
        sha256=f"sha256:{digest}",
    )
