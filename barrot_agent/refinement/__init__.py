"""Optional ping-pong refinement for explicitly classified derived data."""
from .engine import (
    REFINABLE_DATA_CLASSES, IMMUTABLE_DATA_CLASSES,
    DEFAULT_EPSILON, DEFAULT_LEDGER, DEFAULT_MAX_ROUNDS,
    PingPongRefiner, RefinementReport, RoundRecord, refine_data, refine_json_file,
)
from .refiners import HeuristicRefiner, Refiner, RefinementOutput
from . import scoring
from . import paths as ref_paths
from .segmentation import DocumentAudit, Slot, audit_document, segment_document
from .patches import (
    BatchResult, Patch, VerificationReport, apply_patches, detect_conflicts,
    make_delete, make_replace, make_set, make_splice, rollback,
    verify_against_original,
)
from .semantics import (
    CALIBRATION_CASES, LLMSemanticJudge, SemanticVerdict,
    calibrate, evaluate, heuristic_semantic_eval,
)
from .pipeline import (
    IMPLEMENTATION_VERSION, RefinementPipeline, RunState, SectionState,
    find_completed, load_run, refine_document,
)

__all__ = [
    "REFINABLE_DATA_CLASSES", "IMMUTABLE_DATA_CLASSES",
    "DEFAULT_EPSILON",
    "DEFAULT_LEDGER", "DEFAULT_MAX_ROUNDS", "PingPongRefiner",
    "RefinementReport", "RoundRecord", "refine_data", "refine_json_file",
    "HeuristicRefiner", "Refiner", "RefinementOutput", "scoring", "ref_paths", "DocumentAudit", "Slot",
    "audit_document", "segment_document", "BatchResult", "Patch",
    "VerificationReport", "apply_patches", "detect_conflicts", "make_delete",
    "make_replace", "make_set", "make_splice", "rollback",
    "verify_against_original", "CALIBRATION_CASES", "LLMSemanticJudge",
    "SemanticVerdict", "calibrate", "evaluate", "heuristic_semantic_eval",
    "IMPLEMENTATION_VERSION", "RefinementPipeline", "RunState",
    "SectionState", "find_completed", "load_run", "refine_document",
]
