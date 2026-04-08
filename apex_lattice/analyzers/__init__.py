"""
Analyzers sub-package for Apex Lattice.

Each analyzer exposes a single ``analyze(artefact)`` method that
returns a list of raw finding dicts (without ``finding_id`` /
``artefact_id`` — those are added by FindingGenerator).
"""

from __future__ import annotations

from .code_patterns import CodePatternAnalyzer
from .performance import PerformanceAnalyzer
from .security import SecurityAnalyzer
from .dependencies import DependencyAnalyzer
from .architecture import ArchitectureAnalyzer
from .capabilities import CapabilityAnalyzer

ALL_ANALYZERS = [
    CodePatternAnalyzer(),
    PerformanceAnalyzer(),
    SecurityAnalyzer(),
    DependencyAnalyzer(),
    ArchitectureAnalyzer(),
    CapabilityAnalyzer(),
]

__all__ = [
    "CodePatternAnalyzer",
    "PerformanceAnalyzer",
    "SecurityAnalyzer",
    "DependencyAnalyzer",
    "ArchitectureAnalyzer",
    "CapabilityAnalyzer",
    "ALL_ANALYZERS",
]
