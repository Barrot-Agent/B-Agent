"""
Data models for the Directive Platform.

All models support round-trip JSON serialisation via ``to_dict`` /
``from_dict`` so they can be persisted to disk without external dependencies.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

# ---------------------------------------------------------------------------
# Enumerations (plain string constants — no enum dependency)
# ---------------------------------------------------------------------------


class DirectiveType:
    """Categories of work a directive can represent."""

    LEARN = "learn"
    REFINE = "refine"
    ANALYZE = "analyze"
    COOPERATE = "cooperate"
    CROSS_CORROBORATE = "cross_corroborate"
    PROJECT = "project"

    ALL = [LEARN, REFINE, ANALYZE, COOPERATE, CROSS_CORROBORATE, PROJECT]

    _LABELS: dict[str, str] = {
        LEARN: "📚 Learn",
        REFINE: "🔧 Refine",
        ANALYZE: "🔬 Analyze",
        COOPERATE: "🤝 Cooperate",
        CROSS_CORROBORATE: "🔀 Cross-Corroborate",
        PROJECT: "🏗 Project",
    }

    @classmethod
    def label(cls, dtype: str) -> str:
        return cls._LABELS.get(dtype, dtype)


class DirectiveStatus:
    """Lifecycle stages of a directive."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

    ALL = [PENDING, ACTIVE, COMPLETED, FAILED]

    _LABELS: dict[str, str] = {
        PENDING: "⏳ Pending",
        ACTIVE: "🔄 Active",
        COMPLETED: "✅ Completed",
        FAILED: "❌ Failed",
    }

    @classmethod
    def label(cls, status: str) -> str:
        return cls._LABELS.get(status, status)


class AgentStatus:
    """Operating states of an agent."""

    IDLE = "idle"
    ACTIVE = "active"
    UNAVAILABLE = "unavailable"

    ALL = [IDLE, ACTIVE, UNAVAILABLE]

    _LABELS: dict[str, str] = {
        IDLE: "🟢 Idle",
        ACTIVE: "🔵 Active",
        UNAVAILABLE: "⚫ Unavailable",
    }

    @classmethod
    def label(cls, status: str) -> str:
        return cls._LABELS.get(status, status)


class MessageType:
    """Roles that a message can play inside a collaboration session."""

    DIRECTIVE = "directive"
    RESPONSE = "response"
    QUERY = "query"
    INSIGHT = "insight"
    RESULT = "result"
    HANDOFF = "handoff"

    ALL = [DIRECTIVE, RESPONSE, QUERY, INSIGHT, RESULT, HANDOFF]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------


class Agent:
    """
    An AI agent registered on the platform.

    Parameters
    ----------
    agent_id:
        Unique identifier (stable across restarts).
    name:
        Human-readable display name.
    description:
        What this agent is designed to do.
    capabilities:
        List of capability tags (e.g. ``["learn", "knowledge_synthesis"]``).
    status:
        Current operating status (see :class:`AgentStatus`).
    current_directive_id:
        ID of the directive this agent is currently working on, or ``None``.
    created_at:
        Unix timestamp of when the agent was registered.
    """

    def __init__(
        self,
        *,
        agent_id: str | None = None,
        name: str,
        description: str,
        capabilities: list[str],
        status: str = AgentStatus.IDLE,
        current_directive_id: str | None = None,
        created_at: float | None = None,
    ) -> None:
        self.agent_id = agent_id or str(uuid.uuid4())[:8]
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.status = status
        self.current_directive_id = current_directive_id
        self.created_at = created_at or time.time()

    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status,
            "current_directive_id": self.current_directive_id,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Agent":
        return cls(
            agent_id=data["agent_id"],
            name=data["name"],
            description=data["description"],
            capabilities=data.get("capabilities", []),
            status=data.get("status", AgentStatus.IDLE),
            current_directive_id=data.get("current_directive_id"),
            created_at=data.get("created_at"),
        )

    def __repr__(self) -> str:
        return f"Agent(id={self.agent_id!r}, name={self.name!r}, status={self.status!r})"


# ---------------------------------------------------------------------------
# Directive
# ---------------------------------------------------------------------------


class Directive:
    """
    A task or goal issued by a human operator to one or more AI agents.

    Parameters
    ----------
    directive_id:
        Unique identifier.
    title:
        Short descriptive title.
    description:
        Detailed description of what should be accomplished.
    directive_type:
        Category of work (see :class:`DirectiveType`).
    assigned_agent_ids:
        IDs of agents assigned to fulfil this directive.
    human_author:
        Name of the human who issued the directive.
    status:
        Current lifecycle status (see :class:`DirectiveStatus`).
    results:
        List of result records appended by agents as they complete work.
    created_at / updated_at:
        Unix timestamps.
    """

    def __init__(
        self,
        *,
        directive_id: str | None = None,
        title: str,
        description: str,
        directive_type: str,
        assigned_agent_ids: list[str],
        human_author: str,
        status: str = DirectiveStatus.PENDING,
        results: list[dict[str, Any]] | None = None,
        created_at: float | None = None,
        updated_at: float | None = None,
    ) -> None:
        self.directive_id = directive_id or str(uuid.uuid4())[:8]
        self.title = title
        self.description = description
        self.directive_type = directive_type
        self.assigned_agent_ids = assigned_agent_ids
        self.human_author = human_author
        self.status = status
        self.results: list[dict[str, Any]] = results or []
        now = time.time()
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "directive_id": self.directive_id,
            "title": self.title,
            "description": self.description,
            "directive_type": self.directive_type,
            "assigned_agent_ids": self.assigned_agent_ids,
            "human_author": self.human_author,
            "status": self.status,
            "results": self.results,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Directive":
        return cls(
            directive_id=data["directive_id"],
            title=data["title"],
            description=data["description"],
            directive_type=data["directive_type"],
            assigned_agent_ids=data.get("assigned_agent_ids", []),
            human_author=data.get("human_author", "Unknown"),
            status=data.get("status", DirectiveStatus.PENDING),
            results=data.get("results", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __repr__(self) -> str:
        return (
            f"Directive(id={self.directive_id!r}, title={self.title!r}, "
            f"type={self.directive_type!r}, status={self.status!r})"
        )


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------


class Message:
    """
    A single message within a :class:`CollaborationSession`.

    Parameters
    ----------
    message_id:
        Unique identifier.
    session_id:
        ID of the containing session.
    sender_id:
        ``agent_id`` of the sending agent, or ``"human"`` for operator messages.
    sender_name:
        Display name of the sender.
    content:
        Text content of the message.
    message_type:
        Semantic role of the message (see :class:`MessageType`).
    timestamp:
        Unix timestamp.
    """

    def __init__(
        self,
        *,
        message_id: str | None = None,
        session_id: str,
        sender_id: str,
        sender_name: str,
        content: str,
        message_type: str = MessageType.RESPONSE,
        timestamp: float | None = None,
    ) -> None:
        self.message_id = message_id or str(uuid.uuid4())[:8]
        self.session_id = session_id
        self.sender_id = sender_id
        self.sender_name = sender_name
        self.content = content
        self.message_type = message_type
        self.timestamp = timestamp or time.time()

    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "message_id": self.message_id,
            "session_id": self.session_id,
            "sender_id": self.sender_id,
            "sender_name": self.sender_name,
            "content": self.content,
            "message_type": self.message_type,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Message":
        return cls(
            message_id=data["message_id"],
            session_id=data["session_id"],
            sender_id=data["sender_id"],
            sender_name=data["sender_name"],
            content=data["content"],
            message_type=data.get("message_type", MessageType.RESPONSE),
            timestamp=data.get("timestamp"),
        )


# ---------------------------------------------------------------------------
# CollaborationSession
# ---------------------------------------------------------------------------


class CollaborationSession:
    """
    A bounded multi-agent working session for a single directive.

    Parameters
    ----------
    session_id:
        Unique identifier.
    directive_id:
        The directive this session is resolving.
    participant_ids:
        IDs of agents (and optionally ``"human"``) participating.
    messages:
        Ordered list of :class:`Message` objects exchanged so far.
    status:
        ``"active"`` while work is in progress, ``"completed"`` or
        ``"failed"`` when finished.
    started_at / ended_at:
        Unix timestamps.
    """

    def __init__(
        self,
        *,
        session_id: str | None = None,
        directive_id: str,
        participant_ids: list[str],
        messages: list[Message] | None = None,
        status: str = "active",
        started_at: float | None = None,
        ended_at: float | None = None,
        repository: str | None = None,
        branch: str | None = None,
        agent: str | None = None,
        source_session_id: str | None = None,
    ) -> None:
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.directive_id = directive_id
        self.participant_ids = participant_ids
        self.messages: list[Message] = messages or []
        self.status = status
        self.started_at = started_at or time.time()
        self.ended_at = ended_at
        self.repository = repository
        self.branch = branch
        self.agent = agent
        self.source_session_id = source_session_id or self.session_id

    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "directive_id": self.directive_id,
            "participant_ids": self.participant_ids,
            "messages": [m.to_dict() for m in self.messages],
            "status": self.status,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "repository": self.repository,
            "branch": self.branch,
            "agent": self.agent,
            "source_session_id": self.source_session_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CollaborationSession":
        messages = [Message.from_dict(m) for m in data.get("messages", [])]
        return cls(
            session_id=data["session_id"],
            directive_id=data["directive_id"],
            participant_ids=data.get("participant_ids", []),
            messages=messages,
            status=data.get("status", "active"),
            started_at=data.get("started_at"),
            ended_at=data.get("ended_at"),
            repository=data.get("repository"),
            branch=data.get("branch"),
            agent=data.get("agent"),
            source_session_id=data.get("source_session_id", data["session_id"]),
        )

    def __repr__(self) -> str:
        return (
            f"CollaborationSession(id={self.session_id!r}, "
            f"directive={self.directive_id!r}, "
            f"messages={len(self.messages)}, status={self.status!r})"
        )
