#!/usr/bin/env python3
import os
import requests

host = os.environ["DATABRICKS_HOST"]
token = os.environ["DATABRICKS_TOKEN"]
warehouse = os.environ["DATABRICKS_WAREHOUSE_ID"]

import json

# describe columns first
r = requests.post(
    f"https://{host}/api/2.0/sql/statements",
    headers={"Authorization": f"Bearer {token}"},
    json={"warehouse_id": warehouse, "statement": "DESCRIBE workspace.barrot.brain", "wait_timeout": "20s"},
    timeout=30,
)
d = r.json()
print("=== brain columns ===")
for row in d.get("result", {}).get("data_array", []):
    print(row)

r = requests.post(
    f"https://{host}/api/2.0/sql/statements",
    headers={"Authorization": f"Bearer {token}"},
    json={"warehouse_id": warehouse, "statement": "SELECT * FROM workspace.barrot.brain LIMIT 5", "wait_timeout": "20s"},
    timeout=30,
)
d = r.json()
print("=== brain sample rows ===")
print(json.dumps(d.get("result", {}).get("data_array", []), indent=2))
print("=== brain sample column order ===")
print([c["name"] for c in d.get("manifest", {}).get("schema", {}).get("columns", [])])
