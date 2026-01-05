import json
from datetime import datetime

def emit_pingpong_request(payload: dict):
    """
    Emit a pingpong request for the external 22-agent entanglement system.
    
    Args:
        payload: Dictionary containing the request payload
    
    Creates a JSON file that can be committed to GitHub to trigger the external system.
    """
    request = {
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload,
        "origin": "barrot",
        "directive": "offload_pingpong",
        "notes": "Barrot defers to Sean's 22-agent entanglement system."
    }
    with open("pingpong_request.json", "w") as f:
        json.dump(request, f, indent=2)
    print("Ping-Pong request emitted. Commit to GitHub to trigger external system.")
