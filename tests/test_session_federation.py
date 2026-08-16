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
    assert all(message.source_session_id == "copilot-1" for message in session.messages)
    assert session.source_session_ids == ["copilot-1"]


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
    assert merged.source_session_ids == [first.session_id, second.session_id]
    assert len(manager.get_session(first.session_id).messages) == 1


def test_import_rejects_missing_and_oversized_sources(tmp_path):
    manager = SessionManager(tmp_path / "sessions")
    with pytest.raises(FileNotFoundError):
        manager.import_transcript(tmp_path / "missing.md")

    source = tmp_path / "large.txt"
    source.write_bytes(b"x" * (5 * 1024 * 1024 + 1))
    with pytest.raises(ValueError, match="5 MiB"):
        manager.import_transcript(source)


def test_repository_merge_discovers_only_conversation_transcripts(tmp_path):
    transcript = tmp_path / "copilot-session.md"
    transcript.write_text(
        "User: Build a unified context.\nCopilot: I will preserve each source session.",
        encoding="utf-8",
    )
    (tmp_path / "generated.md").write_text(
        "Copilot coordinates workflows and stores useful knowledge.",
        encoding="utf-8",
    )

    manager = SessionManager(tmp_path / "sessions")
    assert manager.discover_transcripts(tmp_path) == [transcript]

    merged = manager.merge_repository_sessions(tmp_path)

    assert len(merged.messages) == 2
    assert merged.source_session_ids
    assert all(message.source_kind == "copilot" for message in merged.messages)
    assert manager.get_latest_report().session_ids != [merged.session_id]


def test_inventory_reports_scope_validation_duplicates_and_session_metadata(tmp_path):
    transcript = tmp_path / "session.json"
    transcript.write_text(
        json.dumps({
            "session_id": "session-1",
            "directive_id": "build",
            "status": "completed",
            "started_at": 10,
            "ended_at": 20,
            "messages": [
                {"sender_id": "human", "content": "Plan"},
                {"sender_id": "copilot", "content": "Done"},
            ],
        }),
        encoding="utf-8",
    )
    (tmp_path / "duplicate.json").write_text(transcript.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "notes.md").write_text("ordinary project notes", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "hidden.md").write_text("User: no\nCopilot: no", encoding="utf-8")

    inventory = SessionManager(tmp_path / "sessions").inventory_repository_sessions(tmp_path)

    assert inventory["included"][0]["source_session_id"] == "session-1"
    assert inventory["included"][0]["participants"] == ["copilot", "human"]
    reasons = {item["reason"] for item in inventory["excluded"]}
    assert {"duplicate", "unrelated", "excluded_path"} <= reasons


def test_repository_merge_publishes_reviewable_audit_without_deleting_sources(tmp_path):
    transcript = tmp_path / "copilot.md"
    transcript.write_text("User: Plan\nCopilot: Decision: proceed", encoding="utf-8")
    manager = SessionManager(tmp_path / "sessions")

    merged = manager.merge_repository_sessions(tmp_path)
    audit_path = tmp_path / "reports" / "session-audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))

    assert audit["approval_required"] is True
    assert audit["approved"] is False
    assert audit["merged_session_id"] == merged.session_id
    assert audit["report_version"] == 1
    assert transcript.exists()
