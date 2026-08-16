"""
Directive Platform — a multi-agent collaboration system.

Human operators issue *directives* (goals, tasks, learning objectives) and
the platform routes them to one or more AI agents that cooperate to fulfil
them.

Public API
----------
    from directive_platform import DirectivePlatform
    from directive_platform import AgentRegistry, DirectiveManager, SessionManager
    from directive_platform import Directive, Agent, CollaborationSession, Message
    from directive_platform import DirectiveType, DirectiveStatus, AgentStatus

Typical usage
-------------
    platform = DirectivePlatform()
    directive = platform.issue_directive(
        title="Learn about Riemann Hypothesis",
        description="Summarise current progress and open sub-problems.",
        directive_type=DirectiveType.LEARN,
        agent_ids=["learner-agent", "analyst-agent"],
        human_author="Alice",
    )
    session = platform.run_directive(directive.directive_id)
"""

from .models import (
    DirectiveType,
    DirectiveStatus,
    AgentStatus,
    MessageType,
    Agent,
    Directive,
    Message,
    CollaborationSession,
    SessionAnalysis,
    UnifiedReport,
)
from .registry import AgentRegistry
from .directives import DirectiveManager
from .session import SessionManager
from .platform import DirectivePlatform

__all__ = [
    # Enums / constants
    "DirectiveType",
    "DirectiveStatus",
    "AgentStatus",
    "MessageType",
    # Data models
    "Agent",
    "Directive",
    "Message",
    "CollaborationSession",
    "SessionAnalysis",
    "UnifiedReport",
    # Managers
    "AgentRegistry",
    "DirectiveManager",
    "SessionManager",
    # Orchestrator
    "DirectivePlatform",
]
