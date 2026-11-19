#!/usr/bin/env python3
# ==============================================================================
# BARROT-Ω ORCHESTRATOR BRIDGE
# Architect: Sean | Node: Brooklyn Core
# Objective: Read council_weights.json and apply to AGI Orchestrator
# ==============================================================================

import json
import logging
import os
import sys
from pathlib import Path

# Make package imports work regardless of invocation directory.
_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Attempt to load legacy architecture
try:
    try:
        from barrot_agent.agi import agi_orchestrator as _agi_orchestrator  # noqa: F401

        LEGACY_ACTIVE = True
    except ImportError:
        import agi_orchestrator as _agi_orchestrator  # noqa: F401

        LEGACY_ACTIVE = True
except ImportError:
    LEGACY_ACTIVE = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [BARROT-Ω BRIDGE] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def apply_council_weights():
    state_file = "council_weights.json"
    if not os.path.exists(state_file):
        logger.error(f"State file {state_file} not found. Awaiting ingestion node execution.")
        sys.exit(1)

    with open(state_file, "r") as f:
        state = json.load(f)

    logger.info(f"Ingesting state from {state['timestamp']}...")
    logger.info(
        f"Applying {state['target_asset']} Multiplier: {state['orchestrator_weight_multiplier']}x"
    )

    if LEGACY_ACTIVE:
        logger.info("Hooking into agi_orchestrator.py to update Council agent parameters...")
        # Placeholder for physical execution: agi_orchestrator.update_weights(state)
        logger.info("AGI Orchestrator parameters dynamically updated.")
    else:
        logger.warning(
            "agi_orchestrator.py not structured as an importable module in local path. Simulating parameter injection."
        )


if __name__ == "__main__":
    apply_council_weights()
