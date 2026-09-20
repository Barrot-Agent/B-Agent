
from pathlib import Path
import json
import traceback
from datetime import datetime, timezone

repo = Path.cwd()
evidence_dir = repo / ".barrot"
evidence_dir.mkdir(parents=True, exist_ok=True)

for name in (
    "live_model_self_drop_result.txt",
    "live_model_self_drop_exception.txt",
    "live_model_self_drop_clean_evidence.json",
    "live_model_payload_capture.json",
    "live_model_tool_execution.json",
):
    path = evidence_dir / name
    if path.exists():
        path.unlink()

payload_capture = evidence_dir / "live_model_payload_capture.json"
tool_capture = evidence_dir / "live_model_tool_execution.json"
final_evidence = evidence_dir / "live_model_self_drop_clean_evidence.json"

print("==============================================")
print("BARROT CLEAN LIVE SELF-DROP TEST")
print("==============================================")
print(f"REPO={repo}")
print("STALE_PROBE_OUTPUT=CLEARED")

try:
    import sys
sys.path.insert(0, str(repo / "scripts"))
from barrot_agent import ScriptBrain

    captured = {
        "request_count": 0,
        "payloads": [],
        "tool_calls": [],
    }

    original_sender = ScriptBrain._send_groq_request

    def capture_sender(self, payload):
        captured["request_count"] += 1
        captured["payloads"].append(
            json.loads(json.dumps(payload, default=str))
        )
        payload_capture.write_text(
            json.dumps(
                captured["payloads"],
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return original_sender(self, payload)

    ScriptBrain._send_groq_request = capture_sender

    brain = ScriptBrain()

    original_tool_result = brain._tool_result

    def capture_tool_result(tool_call):
        result = original_tool_result(tool_call)

        captured["tool_calls"].append({
            "tool_call": json.loads(
                json.dumps(tool_call, default=str)
            ),
            "result_type": type(result).__name__,
            "result": json.loads(
                json.dumps(result, default=str)
            ),
        })

        tool_capture.write_text(
            json.dumps(
                captured["tool_calls"],
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return result

    brain._tool_result = capture_tool_result

    prompt = """
Perform exactly ONE autonomous self-drop probe.

You MUST actually invoke the self_drop tool.
Do not merely describe it.
Do not simulate it.
Do not call any other tool.

task_id: clean_live_model_self_drop_probe
action: SELF_DROP_PROBE

After the tool call completes, briefly report the result.
"""

    print("LIVE_MODEL_TOOL_CALL_ATTEMPT=START")

    returned = brain.think(prompt)

    tool_call_observed = any(
        isinstance(item.get("tool_call"), dict)
        and (
            item["tool_call"].get("function", {}).get("name")
            == "self_drop"
            or item["tool_call"].get("name") == "self_drop"
        )
        for item in captured["tool_calls"]
    )

    successful_self_drop = any(
        isinstance(item.get("result"), dict)
        and item["result"].get("success") is True
        for item in captured["tool_calls"]
    )

    evidence = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "repository": str(repo),
        "task_id": "clean_live_model_self_drop_probe",
        "action": "SELF_DROP_PROBE",
        "model_returned": True,
        "model_result_type": type(returned).__name__,
        "request_count": captured["request_count"],
        "controller_tool_call_count": len(captured["tool_calls"]),
        "tool_call_observed": tool_call_observed,
        "successful_self_drop": successful_self_drop,
        "payload_capture": str(payload_capture),
        "tool_capture": str(tool_capture),
        "returned_text": str(returned),
    }

    final_evidence.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("LIVE_MODEL_THINK_RETURNED=TRUE")
    print(f"LIVE_MODEL_RESULT_TYPE={type(returned).__name__}")
    print(f"MODEL_REQUEST_COUNT={captured['request_count']}")
    print(f"CONTROLLER_TOOL_CALL_COUNT={len(captured['tool_calls'])}")
    print("")
    print("==============================================")
    print("FRESH LIVE EVIDENCE")
    print("==============================================")
    print(f"TOOL_CALL_OBSERVED={tool_call_observed}")
    print(f"SUCCESSFUL_SELF_DROP={successful_self_drop}")
    print(f"EVIDENCE={final_evidence}")

    if tool_call_observed and successful_self_drop:
        print("LIVE_MODEL_SELF_DROP=CONFIRMED")
    elif tool_call_observed:
        print("LIVE_MODEL_SELF_DROP=TOOL_CALLED_BUT_RESULT_NOT_SUCCESS")
    else:
        print("LIVE_MODEL_SELF_DROP=NOT_CONFIRMED")

except Exception as exc:
    error = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "exception_type": type(exc).__name__,
        "exception": str(exc),
        "traceback": traceback.format_exc(),
    }

    final_evidence.write_text(
        json.dumps(error, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("==============================================")
    print("LIVE TEST EXCEPTION")
    print("==============================================")
    print(f"EXCEPTION_TYPE={type(exc).__name__}")
    print(f"EXCEPTION={exc}")
    print(f"EVIDENCE={final_evidence}")
    raise
