"""Paid-issue kit: score candidates, package a PR, keep a 120-minute timebox."""

from .ledger import Candidate, Policy, Verdict, audit, evaluate, summarize, to_csv
from .pack import (
    build_evidence_pack,
    build_pr_body,
    validate_evidence_plan,
    validate_pr_body,
)
from .timebox import PHASES, TOTAL_MINUTES, Timebox

__all__ = [
    "Candidate",
    "Policy",
    "Verdict",
    "audit",
    "evaluate",
    "summarize",
    "to_csv",
    "build_pr_body",
    "validate_pr_body",
    "build_evidence_pack",
    "validate_evidence_plan",
    "PHASES",
    "TOTAL_MINUTES",
    "Timebox",
]

__version__ = "1.0.0"
