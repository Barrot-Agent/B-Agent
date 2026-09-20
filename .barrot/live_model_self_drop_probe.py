import json
import os
import inspect
import sys
from pathlib import Path
from datetime import datetime, timezone

# The probe lives under .barrot/, so explicitly anchor imports
# to the repository root.
REPO_ROOT = Path(__file__).resolve().parents[1]
os.chdir(REPO_ROOT)

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("REPO", "Barrot-Agent/B-Agent")

from scripts.barrot_agent import ScriptBrain


def emit(name, value):
    print(f"{name}={value}")


brain = ScriptBrain()

emit("BRAIN_CLASS", type(brain).__name__)
emit("MODEL", getattr(brain, "model", "UNKNOWN"))
emit("MAX_TOOL_ROUNDS", getattr(brain, "MAX_TOOL_ROUNDS", "UNKNOWN"))

emit(
    "THINK_SIGNATURE",
    str(inspect.signature(brain.think)),
)

emit(
    "TOOL_RESULT_SIGNATURE",
    str(inspect.signature(brain._tool_result)),
)

tool_names = [
    x["function"]["name"]
    for x in getattr(brain, "tools", [])
    if isinstance(x, dict)
    and isinstance(x.get("function"), dict)
]

emit("TOOLS", ",".join(tool_names))

assert "self_drop" in tool_names
assert "self_drop" in brain.tool_funcs

# ------------------------------------------------------------
# First prove the controller's actual tool-result boundary.
# This is NOT the model call. It proves the exact function that
# the controller invokes after receiving a model tool call.
# ------------------------------------------------------------

tool_call = {
    "function": {
        "name": "self_drop",
        "arguments": json.dumps({
            "task_id": "live_tool_loop_controller_boundary",
            "action": "SELF_DROP_PROBE",
        }),
    }
}

boundary_result = brain._tool_result(tool_call)

assert isinstance(boundary_result, dict)
assert boundary_result.get("success") is True
assert boundary_result.get("returncode") == 0
assert boundary_result.get("repository_mutation") is False
assert boundary_result.get("arbitrary_shell_input") is False
assert boundary_result.get("bundle_sha256")
assert boundary_result.get("evidence_path")

emit("CONTROLLER_TOOL_BOUNDARY", "PASS")
emit("SELF_DROP_EXECUTION", "PASS")
emit("SHA256_EVIDENCE", "PASS")
emit("SAFETY_GUARDS", "PASS")

# ------------------------------------------------------------
# Now exercise ScriptBrain.think(use_tools=True).
#
# The prompt explicitly requires a self_drop call. If the
# configured model/provider cannot perform native tool calling,
# that fact is recorded rather than being converted into PASS.
# ------------------------------------------------------------

prompt = """
Barrot V3 live tool-loop verification.

You have access to the registered self_drop tool.

For this verification task, call the self_drop tool exactly once
with:
task_id = live_model_tool_loop
action = SELF_DROP_PROBE

Do not invent tool output.
After the tool returns, briefly state what the tool returned.
"""

emit("LIVE_MODEL_TOOL_CALL_ATTEMPT", "START")

try:
    result = brain.think(
        prompt,
        use_tools=True,
    )

    emit("LIVE_MODEL_THINK_RETURNED", "TRUE")
    emit(
        "LIVE_MODEL_RESULT_TYPE",
        type(result).__name__,
    )

    # Persist a bounded representation for evidence.
    rendered = repr(result)
    Path(".barrot/live_model_self_drop_result.txt").write_text(
        rendered[:20000] + "\n",
        encoding="utf-8",
    )

    # Do NOT infer a successful model tool call merely because
    # think() returned. Search the returned structure/text for
    # concrete evidence of the self_drop invocation.
    blob = json.dumps(result, default=str)
    tool_seen = (
        '"self_drop"' in blob
        and "live_model_tool_loop" in blob
    )

    if tool_seen:
        emit("LIVE_MODEL_SELF_DROP_CALL", "OBSERVED")
    else:
        emit("LIVE_MODEL_SELF_DROP_CALL", "NOT_CONFIRMED")

except Exception as exc:
    Path(".barrot/live_model_self_drop_exception.txt").write_text(
        repr(exc) + "\n",
        encoding="utf-8",
    )
    emit("LIVE_MODEL_TOOL_CALL_EXCEPTION", type(exc).__name__)
    emit("LIVE_MODEL_TOOL_CALL_ERROR", str(exc)[:1000])

# ------------------------------------------------------------
# Repository reconciliation snapshot.
# This is deliberately observational: no files are deleted,
# reset, cleaned, stashed, or overwritten.
# ------------------------------------------------------------

status = os.popen(
    "git status --short"
).read()

diff_stat = os.popen(
    "git diff --stat"
).read()

untracked_count = len([
    line for line in status.splitlines()
    if line.startswith("?? ")
])

modified_count = len([
    line for line in status.splitlines()
    if line and not line.startswith("?? ")
])

reconciliation = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "head": os.popen("git rev-parse HEAD").read().strip(),
    "branch": os.popen("git branch --show-current").read().strip(),
    "modified_entries": modified_count,
    "untracked_entries": untracked_count,
    "status": status,
    "diff_stat": diff_stat,
    "policy": {
        "delete": False,
        "reset": False,
        "clean": False,
        "stash": False,
        "overwrite": False,
    },
}

Path(".barrot/work_reconciliation_snapshot.json").write_text(
    json.dumps(reconciliation, indent=2),
    encoding="utf-8",
)

emit("WORK_RECONCILIATION_SNAPSHOT", "PASS")
emit("DESTRUCTIVE_OPERATIONS", "NONE")
emit("PRESERVATION_POLICY", "PASS")

print()
print("=== LIVE LOOP PROBE COMPLETE ===")
