"""
Barrot Agent — core AI agent package.

Exports
-------
SmartAgent
    Autonomous plan-act-observe agent with built-in tools.
AgentEvent, AgentEventType, PlanStep, ToolCall, ToolResult
    Supporting data models for the agent loop.
DatasetManager, AssetLoader, DatasetAnalytics
    3D dataset absorption and rendering utilities.
data_registry
    Central data access layer for all canonical JSON datasets.
"""

from .smart_agent import (
    AgentEvent,
    AgentEventType,
    PlanStep,
    SmartAgent,
    ToolCall,
    ToolResult,
)
from .millennium_reasoning import (
    CapabilityTargets,
    ClaimAssessment,
    FindingImpactReport,
    FormalArtifact,
    GovernanceDecision,
    HypothesisExperiment,
    KnowledgeAsset,
    MillenniumReasoningEngine,
)

__version__ = "2.0.0"
__author__ = "Barrot-Agent"
__license__ = "Apache-2.0"

try:
    from barrot_agent.rendering import AssetLoader, DatasetAnalytics, DatasetManager

    _rendering_available = True
except Exception:
    _rendering_available = False

# Expose the central data registry so callers can do:
#   from barrot_agent import data_registry
#   data_registry.load_millennium_problems()
try:
    from data import registry as data_registry

    _registry_available = True
except Exception:
    _registry_available = False

__all__ = [
    "AgentEvent",
    "AgentEventType",
    "PlanStep",
    "ToolCall",
    "ToolResult",
    "SmartAgent",
    "data_registry",
    "CapabilityTargets",
    "KnowledgeAsset",
    "FormalArtifact",
    "HypothesisExperiment",
    "ClaimAssessment",
    "FindingImpactReport",
    "GovernanceDecision",
    "MillenniumReasoningEngine",
]

if _rendering_available:
    __all__ += ["DatasetManager", "AssetLoader", "DatasetAnalytics"]
