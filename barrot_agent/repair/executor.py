import json


def generate_repair(
    llm,
    subsystem_name,
    context,
    plan,
):
    prompt = f"""
You are repairing ONE repository subsystem.

SUBSYSTEM:
{subsystem_name}

REPOSITORY CONTEXT:
{context}

REPAIR PLAN:
{json.dumps(plan, indent=2)}

Return ONLY valid JSON.

Schema:

{{
  "changes": {{
    "path/to/file.py": "FULL NEW FILE CONTENT"
  }},
  "explanation": "..."
}}

Rules:

- Only include files explicitly justified by the repair plan.
- Preserve unrelated code.
- Return complete file contents.
- Do not include Markdown fences.
- Do not include secrets.
"""

    response = llm.chat([
        {
            "role": "user",
            "content": prompt,
        }
    ])

    return json.loads(response)
