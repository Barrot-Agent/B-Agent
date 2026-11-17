"""Barrot geometry: typed representation, structural signature, relations.

Scope is deliberately small. This package composes existing mesh code; it
does not replace it. See ``barrot_agent.rendering.mesh_topology`` for the
topology implementation and ``barrot_agent.ingestion.mmi_contract`` for the
MMI provenance layer.
"""
from barrot_agent.geometry.object import GeomObject
from barrot_agent.geometry.relations import (
    Relation,
    RelationGraph,
    RelationType,
)
from barrot_agent.geometry.signature import (
    INVARIANT_SETS,
    SUPPORTED_TRANSFORMS,
    Signature,
    canonical_form,
    structural_signature,
)
from barrot_agent.geometry.states import (
    ConstraintResult,
    EvidenceState,
    TruthState,
    combine,
    evaluate_constraint,
    from_mmi_evidence,
    from_parse_state,
    from_stage_status,
    refuted_evidence,
    verified_evidence,
)

__all__ = [
    "GeomObject",
    "Relation",
    "RelationGraph",
    "RelationType",
    "INVARIANT_SETS",
    "SUPPORTED_TRANSFORMS",
    "Signature",
    "canonical_form",
    "structural_signature",
    "ConstraintResult",
    "EvidenceState",
    "TruthState",
    "combine",
    "evaluate_constraint",
    "from_mmi_evidence",
    "from_parse_state",
    "from_stage_status",
    "refuted_evidence",
    "verified_evidence",
]
