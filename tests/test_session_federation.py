"""Tests for local transcript import and session federation."""

import json

import pytest

from directive_platform import Message, SessionManager


def test_import_json_transcript_preserves_provenance(tmp_path):
    source = tmp_path / "copilot.json"
    source.write_text(
        json.dumps(
            {
                "session_id": "copilot-1",
                "messages": [
                    {"sender_name": "User", "content": "Investigate the API"},
                    {"sender_name": "Copilot", "content": "I found the endpoint."},
                ],
            }
        ),
        encoding="utf-8",
    )

    manager = SessionManager(tmp_path / "sessions")
    session = manager.import_transcript(source, source_kind="copilot")

    assert [message.content for message in session.messages] == [
        "Investigate the API",
        "I found the endpoint.",
    ]
    assert all(message.source_kind == "copilot" for message in session.messages)
    assert all(message.source_session_id == "copilot" for message in session.messages)


def test_merge_sessions_is_ordered_deduplicated_and_non_destructive(tmp_path):
    manager = SessionManager(tmp_path / "sessions")
    first = manager.create_session("directive-a", ["human"])
    second = manager.create_session("directive-b", ["copilot"])
    shared = Message(
        session_id=first.session_id,
        sender_id="human",
        sender_name="Human",
        content="same",
        timestamp=1,
    )
    manager.add_message(first.session_id, shared)
    manager.add_message(
        second.session_id,
        Message(
            session_id=second.session_id,
            sender_id="copilot",
            sender_name="Copilot",
            content="later",
            timestamp=2,
        ),
    )
    manager.add_message(
        second.session_id,
        Message(
            session_id=second.session_id,
            sender_id="human",
            sender_name="Human",
            content="same",
            timestamp=1,
        ),
    )

    merged = manager.merge_sessions([first.session_id, second.session_id])

    assert [message.content for message in merged.messages] == ["same", "later"]
    assert merged.messages[0].source_session_id == first.session_id
    assert merged.messages[1].source_session_id == second.session_id
    assert len(manager.get_session(first.session_id).messages) == 1


def test_import_rejects_missing_and_oversized_sources(tmp_path):
    manager = SessionManager(tmp_path / "sessions")
    with pytest.raises(FileNotFoundError):
        manager.import_transcript(tmp_path / "missing.md")

    source = tmp_path / "large.txt"
    source.write_bytes(b"x" * (5 * 1024 * 1024 + 1))
    with pytest.raises(ValueError, match="5 MiB"):
        manager.import_transcript(source)
