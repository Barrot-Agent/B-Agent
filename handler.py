import json
from datetime import datetime

class EndpointHandler:
    def __init__(self):
        self.timestamp = datetime.utcnow().isoformat()
        self.status = "online"
        
    def __call__(self, payload):
        inputs = payload.get("inputs", "no input")
        params = payload.get("parameters", {})
        
        if "gemma" in inputs.lower() or "gemma 4" in inputs.lower():
            response = {
                "model": "gemma-4-adapter",
                "response": f"GEMMA 4 INTEGRATED: {inputs}",
                "timestamp": self.timestamp,
                "status": "gemma_activated"
            }
        else:
            response = {
                "model": "barrot_mrp",
                "response": f"MRP Engine: {inputs}",
                "frames": params.get("frames", []),
                "timestamp": self.timestamp,
                "status": "mrp_online"
            }
        
        return response
