"""barrot_agent.refinement — ping-pong model refinement, the baseline of
all data processing.

Data is refined by alternating models until it can be refined no further
(measured fixed point via barrot_agent.refinement.scoring). Every round is
ledgered to JSONL for provenance.
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
]
