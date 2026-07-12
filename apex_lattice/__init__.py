"""
Apex Lattice – Sandbox-based data processing system for Barrot.

Provides an analysis pipeline that runs inside isolated sandbox environments
within the .apex_lattice working directory.  Results are persisted as
structured JSON findings, human-readable recommendations and full audit logs.
"""

from apex_lattice.audit import AuditTrail
from apex_lattice.sandbox import SandboxPipeline
from apex_lattice.findings import FindingGenerator
from apex_lattice.recommendations import RecommendationEngine
from apex_lattice.pr_framework import PRFramework
from apex_lattice.cycle import CycleManager
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
    "FindingGenerator",
    "RecommendationEngine",
    "PRFramework",
    "CycleManager",
    "Finding",
    "FindingGenerator",
    "Recommendation",
    "RecommendationEngine",
    "PRFramework",
    "CycleManager",
    "CycleResult",
]
