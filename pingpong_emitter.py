import json
from datetime import datetime
from pathlib import Path


_PINGPONG_REQUEST_PATH = Path(__file__).resolve().parent / "data" / "pingpong_request.json"

def emit_pingpong_request(payload: dict):
    """
    Emit a pingpong request for the external 22-agent entanglement system.
    
    Args:
        payload: Dictionary containing the request payload
    
    Creates the canonical JSON file in data/ that can be committed to GitHub
    to trigger the external system.
    """
    request = {
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload,
        "origin": "barrot",
        "directive": "offload_pingpong",
        "notes": "Barrot defers to Sean's 22-agent entanglement system."
    }
    _PINGPONG_REQUEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_PINGPONG_REQUEST_PATH, "w") as f:
        json.dump(request, f, indent=2)
    print(f"Ping-Pong request emitted at {_PINGPONG_REQUEST_PATH}. Commit to GitHub to trigger external system.")
