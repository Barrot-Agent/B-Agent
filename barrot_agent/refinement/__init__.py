"""barrot_agent.refinement — ping-pong model refinement, the baseline of
all data processing.

Data is refined by alternating models until it can be refined no further
(measured fixed point via barrot_agent.refinement.scoring). Every round is
ledgered to JSONL for provenance.

Large documents (above the segmentation threshold) are refined through the
patch pipeline (pipeline.py): SOURCE -> AUDIT -> SEGMENT -> REFINE ->
GENERATE PATCHES -> VALIDATE -> APPLY -> SEMANTIC EVALUATION -> REGRESSION
TEST -> RECORD RESULTS — with rollback, resumability and a persistent
learning history. Semantic evaluation lives in semantics.py (independent
judge + deterministic core); mechanical scoring in scoring.py.
"""
from .engine import (
    DEFAULT_EPSILON,
    DEFAULT_LEDGER,
    DEFAULT_MAX_ROUNDS,
    PingPongRefiner,
    RefinementReport,
    RoundRecord,
    refine_data,
    refine_json_file,
)
from .refiners import (
    HeuristicRefiner,
    OpenCodeRefiner,
    Refiner,
    RefinementOutput,
    make_model_refiners,
)
from . import scoring
from . import paths as ref_paths
from .segmentation import (
    DocumentAudit,
    Slot,
    audit_document,
    segment_document,
)
from .patches import (
    BatchResult,
    Patch,
    VerificationReport,
    apply_patches,
    detect_conflicts,
    make_delete,
    make_replace,
    make_set,
    make_splice,
    rollback,
    verify_against_original,
)
from .semantics import (
    CALIBRATION_CASES,
    LLMSemanticJudge,
    SemanticVerdict,
    calibrate,
    evaluate,
    heuristic_semantic_eval,
)
from .pipeline import (
    IMPLEMENTATION_VERSION,
    RefinementPipeline,
    RunState,
    SectionState,
    find_completed,
    load_run,
    refine_document,
)

__all__ = [
    "DEFAULT_EPSILON",
    "DEFAULT_LEDGER",
    "DEFAULT_MAX_ROUNDS",
    "HeuristicRefiner",
    "OpenCodeRefiner",
    "PingPongRefiner",
    "Refiner",
    "RefinementOutput",
    "RefinementReport",
    "RoundRecord",
    "refine_data",
    "refine_json_file",
    "make_model_refiners",
    "scoring",
    "ref_paths",
    "DocumentAudit",
    "Slot",
    "audit_document",
    "segment_document",
    "BatchResult",
    "Patch",
    "VerificationReport",
    "apply_patches",
    "detect_conflicts",
    "make_delete",
    "make_replace",
    "make_set",
    "make_splice",
    "rollback",
    "verify_against_original",
    "CALIBRATION_CASES",
    "LLMSemanticJudge",
    "SemanticVerdict",
    "calibrate",
    "evaluate",
    "heuristic_semantic_eval",
    "IMPLEMENTATION_VERSION",
    "RefinementPipeline",
    "RunState",
    "SectionState",
    "find_completed",
    "load_run",
    "refine_document",
]
