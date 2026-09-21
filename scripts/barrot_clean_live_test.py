import json
import os
from pathlib import Path
from datetime import datetime, timezone

repo = Path.cwd()
os.environ["REPO"] = str(repo)
os.environ["PYTHONPATH"] = str(repo)

from scripts.barrot_agent import ScriptBrain

print("==============================================")
print("BARROT PROVIDER-NEUTRAL SELF-DROP BOUNDARY TEST")
print("==============================================")
print("NETWORK_MODEL_CALL=NONE")

captured = {}

def fake_provider(payload):
    captured["payload"] = json.loads(json.dumps(payload, default=str))
    return {
        "choices": [
            {
                "message": {
                    "content": "provider boundary test",
                    "tool_calls": [],
                }
            }
        ]
    }

brain = ScriptBrain(request_sender=fake_provider)

result = brain.think(
    "Provider boundary test. Do not invoke any tool.",
    use_tools=False,
)

assert result == "provider boundary test"
assert "payload" in captured
assert captured["payload"].get("messages")

evidence = repo / ".barrot" / "provider_boundary_evidence.json"
evidence.parent.mkdir(parents=True, exist_ok=True)
evidence.write_text(
    json.dumps(
        {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "provider_boundary": "PASS",
            "request_sender_injection": "PASS",
            "think_path": "PASS",
            "network_model_call": False,
            "result": result,
        },
        indent=2,
    ),
    encoding="utf-8",
)

print("SCRIPTBRAIN_IMPORT=PASS")
print("SCRIPTBRAIN_INIT=PASS")
print("REQUEST_SENDER_INJECTION=PASS")
print("THINK_PROVIDER_BOUNDARY=PASS")
print("NETWORK_MODEL_CALL=NONE")
print(f"EVIDENCE={evidence}")
print("PROVIDER_NEUTRAL_CONTROLLER=CONFIRMED")
