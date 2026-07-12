"""
Apex Lattice — sandbox-based data processing and analysis system.

Public API
----------
    from apex_lattice import CycleManager, AuditTrail
    from apex_lattice import SandboxPipeline, FindingGenerator
    from apex_lattice import RecommendationEngine, PRFramework

CLI
---
    python -m apex_lattice               # single analysis cycle
    python -m apex_lattice --schedule 3600  # recurring every hour
    python -m apex_lattice --status      # view audit log
    python -m apex_lattice --findings    # list findings
    python -m apex_lattice --recs        # list recommendations
"""

from .audit import AuditTrail
from .pipeline import SandboxPipeline
from .findings import Finding, FindingGenerator
from .recommendations import Recommendation, RecommendationEngine
from .pr_framework import PRFramework
from .cycle import CycleManager, CycleResult

__all__ = [
    "AuditTrail",
    "SandboxPipeline",
    "Finding",
    "FindingGenerator",
    "Recommendation",
    "RecommendationEngine",
    "PRFramework",
    "CycleManager",
    "CycleResult",
]
