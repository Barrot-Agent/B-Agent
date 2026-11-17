"""Registry guard for config/phoenix_sources.json.

The registry is only useful if every entry states what it teaches, what its
license allows, and when it was last probed. A source without those is a link, not
a source.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

REGISTRY = Path(__file__).resolve().parents[1] / "config" / "phoenix_sources.json"
REQUIRED = ("id", "url", "transport", "auth", "license", "teaches", "probe_status", "probed_at")


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_registry_parses_and_has_sources():
    data = load_registry()
    assert data["version"] == 1
    assert len(data["sources"]) >= 10
    ids = [s["id"] for s in data["sources"]]
    assert len(ids) == len(set(ids)), "duplicate source ids"


def test_every_source_states_its_licence_and_purpose():
    for source in load_registry()["sources"]:
        for field in REQUIRED:
            assert source.get(field) not in (None, ""), (source.get("id"), field)
        assert source["url"].startswith("https://")


def test_probe_status_is_recorded_not_assumed():
    for source in load_registry()["sources"]:
        assert source["probe_status"] == 200, source["id"]
        assert source["probed_at"] == "2026-11-17"


def test_policy_defaults_to_read_only():
    policy = load_registry()["policy"]
    assert policy["default"] == "read_only"
    assert policy["no_crawl_without_approval"] is True
    assert policy["record_provenance"]
