"""Smoke tests for the canonical data registry."""

from data import registry


def test_registry_imports():
    assert registry is not None
