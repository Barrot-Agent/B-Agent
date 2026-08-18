import json
from datetime import datetime, timezone
from pathlib import Path

_PINGPONG_REQUEST_PATH = Path(__file__).resolve().parent / "data" / "pingpong_request.json"


def emit_pingpong_request(payload: dict):
    """
    Emit a ping-pong request to defer processing to an external system.

    Creates a JSON request file with a timestamp, payload, and metadata
    indicating that Barrot defers to Sean's 22-agent entanglement system.

    Args:
        payload: A dictionary containing the request payload data.

    Side Effects:
        - Writes the canonical JSON request file in data/pingpong_request.json
        - Prints a confirmation message to stdout
    """
    request = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
        "origin": "barrot",
        "directive": "offload_pingpong",
        "notes": "Barrot defers to Sean's 22-agent entanglement system.",
    }
    _PINGPONG_REQUEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_PINGPONG_REQUEST_PATH, "w") as f:
        json.dump(request, f, indent=2)
    print(
        f"Ping-Pong request emitted at {_PINGPONG_REQUEST_PATH}. "
        "Commit to GitHub to trigger external system."
    )
