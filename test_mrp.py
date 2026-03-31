from handler import EndpointHandler
import json

h = EndpointHandler()

payload = {
    "inputs": "Stupid Sindy monetization optimization",
    "parameters": {
        "frames": [
            {"data": "HF_Space", "priority": 0.82},
            {"data": "Databricks", "priority": 0.71},
            {"data": "GitHub", "priority": 0.65}
        ]
    }
}

result = h(payload)
print(json.dumps(result, indent=2))
