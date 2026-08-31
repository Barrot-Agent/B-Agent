"""
PingPong request emitter.

Writes requests for the external agent-entanglement system to a JSON file.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def emit_pingpong_request(payload: Dict[str, Any]) -> Path:
    """Persist a PingPong request and return its path."""
    request = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }

    output = Path("pingpong_request.json")
    output.write_text(json.dumps(request, indent=2, default=str))
    return output
