"""Deprecated duplicate — import shim only.

Canonical: barrot_agent/monetization/trial_tracker.py
This file was byte-identical to that module (sha256 9f4bb6b0…ac7229d58d6).

Canonical chosen because the live importer uses the monetization path:
.barrot/disabled_tests/test_longevity_modules.py imports
DiscoveryExtractor, EfficacyAnalyzer, ParticipantCohort, SafetyMonitor from
barrot_agent.monetization.trial_tracker.
Do not add logic here.
"""
from __future__ import annotations

from barrot_agent.monetization.trial_tracker import *  # noqa: F401,F403
from barrot_agent.monetization.trial_tracker import (  # noqa: F401
    DiscoveryExtractor,
    EfficacyAnalyzer,
    ParticipantCohort,
    SafetyMonitor,
)
