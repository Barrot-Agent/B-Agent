import json


def build_repair_plan(llm, subsystem_name, audit, dependencies):
    prompt = f"""
You are planning repairs for ONE repository subsystem.

SUBSYSTEM:
{subsystem_name}

AUDIT:
{audit}

DEPENDENCIES:
{json.dumps(dependencies, indent=2)}

Return ONLY valid JSON.

Schema:

{{
  "subsystem": "...",
  "safe_to_modify": true,
  "actions": [
    {{
      "priority": 1,
      "path": "existing/or/new/file",
      "action": "modify|create|delete|move",
      "reason": "...",
      "validation": [
        "python -m py_compile ..."
      ]
    }}
  ],
  "risks": [],
  "blocked_by": []
}}

Rules:

- Do not invent repository files.
- Prefer small reversible changes.
- Do not delete files without evidence.
- Do not modify secrets.
- Do not change unrelated subsystems.
- Every action must have validation.
"""

    response = llm.chat([
        {
            "role": "user",
            "content": prompt,
        }
    ])

    return json.loads(response)
