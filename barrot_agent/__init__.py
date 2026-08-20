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
KimiClient
    Kimi 3 model integration for paradigm-shifting feedback.
RecursiveFeedbackLoop
    Self-improving recursive feedback loop orchestrator.
SessionInsightAggregator
    Aggregates insights from all GitHub agent sessions with cross-analysis.
"""

from .kimi_integration import KimiClient
from .recursive_feedback import (
    FeedbackIteration,
    RecursiveFeedbackLoop,
    RecursiveFeedbackReport,
)
from .session_insight_aggregator import (
    CrossAnalysisResult,
    SessionInsight,
    SessionInsightAggregator,
    SessionInsightDatabase,
)
from .smart_agent import (
    AgentEvent,
    AgentEventType,
    PlanStep,
    SmartAgent,
    ToolCall,
    ToolResult,
)
from .upgrade_flywheel import (
    ActionResult,
    FlywheelCycleResult,
    FlywheelReport,
    ObservationResult,
    ReasoningResult,
    UpgradeFlywheel,
    VerificationResult,
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
    "ActionResult",
    "FlywheelCycleResult",
    "FlywheelReport",
    "ObservationResult",
    "ReasoningResult",
    "UpgradeFlywheel",
    "VerificationResult",
    "KimiClient",
    "RecursiveFeedbackLoop",
    "RecursiveFeedbackReport",
    "FeedbackIteration",
    "SessionInsightAggregator",
    "SessionInsightDatabase",
    "SessionInsight",
    "CrossAnalysisResult",
    "data_registry",
]

if _rendering_available:
    __all__ += ["DatasetManager", "AssetLoader", "DatasetAnalytics"]
