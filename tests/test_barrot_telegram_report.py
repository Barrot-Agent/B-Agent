from __future__ import annotations

import sys
from pathlib import Path

import pytest

from scripts import barrot_telegram_report


def test_report_refuses_to_infer_telegram_recipient(monkeypatch, capsys) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    monkeypatch.setattr(sys, "argv", ["barrot_telegram_report.py"])
    monkeypatch.setattr(
        barrot_telegram_report,
        "build_report",
        lambda *args, **kwargs: pytest.fail("report must not be built without an explicit recipient"),
    )
    monkeypatch.setattr(
        barrot_telegram_report,
        "send_telegram",
        lambda *args, **kwargs: pytest.fail("no Telegram message may be sent without an explicit recipient"),
    )

    assert barrot_telegram_report.main() == 1
    assert "TELEGRAM_CHAT_ID" in capsys.readouterr().err


def test_telegram_workflow_is_manual_and_requires_confirmation() -> None:
    workflow = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "barrot-telegram-report.yml"
    text = workflow.read_text(encoding="utf-8")
    assert "schedule:" not in text
    assert "confirm_send:" in text
    assert "if: ${{ inputs.confirm_send == true }}" in text
    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1" in text
    assert "actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0" in text
