"""Optional ping-pong refinement for explicitly classified derived data.

Offline deterministic refiners are the default. External LunaRoute calls
require dual opt-in and public-data classification. Canonical raw evidence,
receipts, feature snapshots, event timelines, and forecast ledgers are
immutable and must not pass through this component.
"""
from .engine import (
    REFINABLE_DATA_CLASSES, IMMUTABLE_DATA_CLASSES,
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
    EXTERNAL_REFINEMENT_ALLOWED_CLASSES, HeuristicRefiner,
    LunaRouteRefiner,
    Refiner,
    RefinementOutput,
    make_model_refiners,
)
from . import scoring

__all__ = [
    "REFINABLE_DATA_CLASSES", "IMMUTABLE_DATA_CLASSES",
    "EXTERNAL_REFINEMENT_ALLOWED_CLASSES",
    "DEFAULT_EPSILON",
    "DEFAULT_LEDGER",
    "DEFAULT_MAX_ROUNDS",
    "HeuristicRefiner",
    "LunaRouteRefiner",
    "PingPongRefiner",
    "Refiner",
    "RefinementOutput",
    "RefinementReport",
    "RoundRecord",
    "refine_data",
    "refine_json_file",
    "make_model_refiners",
    "scoring",
]
