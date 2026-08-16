import json

from directive_platform.bundle import export_sessions, merge_sessions
from directive_platform.models import CollaborationSession, Message
from directive_platform.session import SessionManager


def test_export_and_merge_deduplicate_messages(tmp_path):
    sessions = tmp_path / "sessions"
    manager = SessionManager(sessions)
    session = manager.create_session("directive", ["agent"], repository="repo", branch="main", agent="a")
    manager.add_message(
        session.session_id,
        Message(session_id=session.session_id, sender_id="a", sender_name="A", content="hello"),
    )
    bundle_path = tmp_path / "bundle.json"
    export_sessions(sessions, bundle_path)

    report = merge_sessions(sessions, bundle_path, tmp_path / "report.json")

    assert report["imported"] == 1
    assert report["conflicts"] == []
    restored = CollaborationSession.from_dict(
        json.loads((sessions / f"{session.session_id}.json").read_text())
    )
    assert len(restored.messages) == 1
    assert restored.repository == "repo"


def test_merge_reports_conflicting_message(tmp_path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    session = CollaborationSession(session_id="same", directive_id="d", participant_ids=[])
    message = Message(
        message_id="message",
        session_id="same",
        sender_id="a",
        sender_name="A",
        content="original",
    )
    session.messages.append(message)
    (sessions / "same.json").write_text(json.dumps(session.to_dict()))
    bundle = {"version": 1, "sessions": [{**session.to_dict(), "messages": [
        {**message.to_dict(), "content": "changed"}
    ]}]}
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle))

    report = merge_sessions(sessions, bundle_path)

    assert report["conflicts"] == [{"session_id": "same", "message_id": "message"}]
