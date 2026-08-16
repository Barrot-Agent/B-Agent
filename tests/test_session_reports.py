"""Tests for provenance-preserving session synthesis."""

from directive_platform import Message, MessageType, SessionManager


def test_analyze_session_extracts_categories_and_provenance(tmp_path):
    manager = SessionManager(tmp_path / "sessions")
    session = manager.create_session("directive-a", ["agent-a"])
    manager.add_message(session.session_id, Message(
        session_id=session.session_id, sender_id="agent-a", sender_name="A",
        content="Decision: use the shared dataset. Open question remains.",
        message_type=MessageType.INSIGHT, timestamp=10,
    ))

    analysis = manager.analyze_session(session.session_id)

    assert analysis.decisions[0]["author"] == "A"
    assert analysis.decisions[0]["source_session_id"] == session.session_id
    assert analysis.unresolved_items[0]["timestamp"] == 10


def test_unify_sessions_correlates_duplicate_claims_and_versions_reports(tmp_path):
    manager = SessionManager(tmp_path / "sessions")
    first = manager.create_session("directive-a", ["a"])
    second = manager.create_session("directive-a", ["b"])
    for session in (first, second):
        manager.add_message(session.session_id, Message(
            session_id=session.session_id, sender_id="agent", sender_name="Agent",
            content="The dataset is ready.", message_type=MessageType.RESULT,
        ))

    report = manager.unify_sessions([first.session_id, second.session_id])
    updated = manager.unify_sessions([first.session_id])

    assert report.knowledge_model["confirmed_agreements"] == 1
    assert len(report.agreements[0]["evidence"]) == 2
    assert updated.version == 2
    assert manager.get_latest_report().version == 2
    assert len(manager.list_reports()) == 2
