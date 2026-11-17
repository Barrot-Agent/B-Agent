"""Environment detection: OS, distro, device, shell, surface, tools.

The point is behaviour, not a report: on a phone-shaped device output stays short,
and nothing may assume an interactive Enter key when there is no TTY.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from barrot_agent.environment import Environment, describe, detect, load, save


def test_detect_returns_every_field():
    env = detect()
    data = env.__dict__
    for name in (
        "platform",
        "distro_family",
        "distro_name",
        "arch",
        "device_model",
        "shell",
        "surface",
        "tools",
    ):
        assert name in data
    assert env.platform in {"linux", "darwin", "windows", "unknown"}
    assert env.surface in {
        "opencode-tui",
        "opencode-run",
        "interactive-shell",
        "non-interactive",
        "unknown",
    }


def test_cache_roundtrip(tmp_path):
    env = detect()
    path = tmp_path / "environment.json"
    save(env, path)
    restored = load(path)
    assert restored is not None
    assert restored.platform == env.platform
    assert restored.arch == env.arch
    assert restored.surface == env.surface


def test_behaviour_flags_are_derived_not_guessed():
    phone = Environment(device_model="moto g7 power", surface="opencode-run")
    assert phone.lightweight is True
    assert phone.enter_safe is False

    desktop = Environment(device_model="unknown", surface="opencode-tui")
    assert desktop.lightweight is False
    assert desktop.enter_safe is True


def test_banner_is_plain_ascii():
    banner = describe(Environment(device_model="moto g7", surface="opencode-run"))
    assert banner.startswith("ENVIRONMENT")
    assert all(ord(ch) < 128 for ch in banner)


def test_cache_file_is_valid_json_when_present(tmp_path):
    env = detect()
    path = save(env, tmp_path / "environment.json")
    json.loads(path.read_text())
