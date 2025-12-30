import json
from datetime import datetime, timezone

def emit_pingpong_request(payload: dict):
    """
    Emit a ping-pong request to defer processing to an external system.
    
    Creates a JSON request file with a timestamp, payload, and metadata
    indicating that Barrot defers to Sean's 22-agent entanglement system.
    
    Args:
        payload: A dictionary containing the request payload data.
        
    Side Effects:
        - Writes a JSON file named 'pingpong_request.json' in the current directory
        - Prints a confirmation message to stdout
    """
    request = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
        "origin": "barrot",
        "directive": "offload_pingpong",
        "notes": "Barrot defers to Sean's 22-agent entanglement system."
    }
    with open("pingpong_request.json", "w") as f:
        json.dump(request, f, indent=2)
    print("Ping-Pong request emitted. Commit to GitHub to trigger external system.")
