"""Tests for pingpong emitter longevity topic support."""

from __future__ import annotations

import json
from pathlib import Path

import pingpong_emitter


def test_emit_aging_research_pingpong_request(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "pingpong_request.json"
    monkeypatch.setattr(pingpong_emitter, "_PINGPONG_REQUEST_PATH", target)

    pingpong_emitter.emit_aging_research_pingpong_request(
        payload={"signal": "longevity"},
        breakthroughs=[{"type": "efficacy_breakthrough"}],
    )

    data = json.loads(target.read_text(encoding="utf-8"))
    assert data["topic"] == "aging_research"
    assert data["payload"]["mmi_breakthroughs"][0]["type"] == "efficacy_breakthrough"
