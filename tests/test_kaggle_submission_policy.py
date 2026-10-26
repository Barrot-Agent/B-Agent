"""Regression tests for explicit opt-in before external Kaggle submissions."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from kaggle_submission_policy import submissions_allowed


def test_submissions_disabled_when_environment_is_missing(monkeypatch):
    monkeypatch.delenv("KAGGLE_ALLOW_SUBMISSIONS", raising=False)
    assert submissions_allowed() is False


def test_submissions_disabled_for_false_like_values():
    for value in (None, "", "0", "false", "no", "off", "False "):
        assert submissions_allowed(value) is False


def test_submissions_enabled_only_for_explicit_true_values():
    for value in ("1", "true", "TRUE", "yes", True):
        assert submissions_allowed(value) is True


def test_environment_opt_in_is_respected(monkeypatch):
    monkeypatch.setenv("KAGGLE_ALLOW_SUBMISSIONS", "true")
    assert submissions_allowed() is True
    monkeypatch.setenv("KAGGLE_ALLOW_SUBMISSIONS", "false")
    assert submissions_allowed() is False
