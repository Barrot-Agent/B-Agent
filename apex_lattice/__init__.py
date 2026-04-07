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

__all__ = [
    "AuditTrail",
    "SandboxPipeline",
    "FindingGenerator",
    "RecommendationEngine",
    "PRFramework",
    "CycleManager",
]
