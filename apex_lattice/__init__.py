"""
Apex Lattice - sandbox-based data processing and analysis system for Barrot.

Public API
----------
    from apex_lattice import CycleManager, AuditTrail
    from apex_lattice import SandboxPipeline, FindingGenerator
    from apex_lattice import RecommendationEngine, PRFramework

CLI
---
    python -m apex_lattice               # single analysis cycle
    python -m apex_lattice --schedule 3600  # recurring every hour
"""

from apex_lattice.audit import AuditTrail
from apex_lattice.sandbox import SandboxPipeline, select_analyzers
from apex_lattice.findings import Finding, FindingGenerator
from apex_lattice.recommendations import Recommendation, RecommendationEngine
from apex_lattice.pr_framework import PRFramework
from apex_lattice.cycle import CycleManager

__all__ = [
    "AuditTrail",
    "SandboxPipeline",
    "select_analyzers",
    "Finding",
    "FindingGenerator",
    "Recommendation",
    "RecommendationEngine",
    "PRFramework",
    "CycleManager",
]
