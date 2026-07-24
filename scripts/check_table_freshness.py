#!/usr/bin/env python3
import os
import requests

host = os.environ["DATABRICKS_HOST"]
token = os.environ["DATABRICKS_TOKEN"]
warehouse = os.environ["DATABRICKS_WAREHOUSE_ID"]

import json

sql = "SELECT COUNT(*) AS row_count FROM workspace.barrot.brain"
r = requests.post(
    f"https://{host}/api/2.0/sql/statements",
    headers={"Authorization": f"Bearer {token}"},
    json={"warehouse_id": warehouse, "statement": sql, "wait_timeout": "20s"},
    timeout=30,
)
print("HTTP", r.status_code)
print(json.dumps(r.json(), indent=2))
