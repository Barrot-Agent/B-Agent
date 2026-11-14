"""Ping-pong relay emitter for the external agent system.

Restores the module that ``quantum_entanglement.py`` always expected
(``from emit_pingpong import emit_pingpong_request``); the original file was
removed from the repository while its call site survived behind the
``pingpong_integration_enabled`` flag.

Contract:
- ``emit_pingpong_request(payload)`` appends one JSON line per call to
  ``ping-pongings/knowledge-base/pingpong_relay_log.jsonl`` (the house JSONL
  knowledge-base pattern used by scripts/audio_ingest.py et al.).
- Never raises: a broken/missing log directory must not break reasoning
  pipelines. Returns True when the record was written, False otherwise.
- Stdlib only, side-effect free apart from the log append.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Union

logger = logging.getLogger(__name__)

# barrot_agent/agi/emit_pingpong.py -> repository root is three levels up.
REPO_ROOT = Path(__file__).resolve().parents[2]
RELAY_LOG = REPO_ROOT / "ping-pongings" / "knowledge-base" / "pingpong_relay_log.jsonl"


def emit_pingpong_request(payload: Dict[str, Any]) -> bool:
    """Append *payload* to the ping-pong relay log; never raises.

    A ``relayed_at`` UTC timestamp is added for traceability. Unknown inputs
    are serialized defensively (``default=str``) so dataclass payloads from
    :mod:`barrot_agent.agi.quantum_entanglement` do not crash the emit.
    """
    try:
        record = dict(payload or {})
        record.setdefault("relayed_at", datetime.now(timezone.utc).isoformat())
        RELAY_LOG.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, sort_keys=True, default=str)
        with RELAY_LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        return True
    except Exception:  # pragma: no cover - defensive: logging must not break callers
        logger.debug("pingpong relay emit failed", exc_info=True)
        return False


__all__ = ["emit_pingpong_request", "RELAY_LOG"]
