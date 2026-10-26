"""Small, dependency-free policy gate for external Kaggle submissions."""
from __future__ import annotations

import os

_TRUE_VALUES = {"1", "true", "yes"}


def submissions_allowed(value: str | bool | None = None) -> bool:
    """Return True only for an explicit opt-in; default is always False."""
    if value is None:
        value = os.environ.get("KAGGLE_ALLOW_SUBMISSIONS", "")
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in _TRUE_VALUES
