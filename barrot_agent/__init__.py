"""
Barrot Agent — core AI agent package.

Exports
-------
SmartAgent
    Autonomous plan-act-observe agent with built-in tools.
AgentEvent, AgentEventType, PlanStep, ToolCall, ToolResult
    Supporting data models for the agent loop.
"""

from .smart_agent import (
    AgentEvent,
    AgentEventType,
    PlanStep,
    ToolCall,
    ToolResult,
    SmartAgent,
)

__all__ = [
    "AgentEvent",
    "AgentEventType",
    "PlanStep",
    "ToolCall",
    "ToolResult",
    "SmartAgent",
]
