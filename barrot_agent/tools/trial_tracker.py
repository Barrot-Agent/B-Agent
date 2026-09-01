"""
Compatibility wrapper.

Canonical implementation:
barrot_agent.monetization.trial_tracker
"""

from barrot_agent.monetization.trial_tracker import (
    TrialMetadata,
    ParticipantCohort,
    EfficacyAnalyzer,
    SafetyMonitor,
    DiscoveryExtractor,
)

__all__ = [
    "TrialMetadata",
    "ParticipantCohort",
    "EfficacyAnalyzer",
    "SafetyMonitor",
    "DiscoveryExtractor",
]
