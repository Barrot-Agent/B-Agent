#!/usr/bin/env python3
import os
import requests

host = os.environ["DATABRICKS_HOST"]
token = os.environ["DATABRICKS_TOKEN"]
warehouse = os.environ["DATABRICKS_WAREHOUSE_ID"]

import json

tables = [
    "brain", "memory", "model_abstraction_layer", "protocol_anchors",
    "protocol_lexicon", "sandbox_results", "strategic_intelligence",
]

for t in tables:
    sql = f"SELECT COUNT(*) AS row_count FROM workspace.barrot.{t}"
    r = requests.post(
        f"https://{host}/api/2.0/sql/statements",
        headers={"Authorization": f"Bearer {token}"},
        json={"warehouse_id": warehouse, "statement": sql, "wait_timeout": "20s"},
        timeout=30,
    )
    try:
        data = r.json()
        state = data.get("status", {}).get("state")
        if state == "SUCCEEDED":
            row_count = data["result"]["data_array"][0][0]
            print(f"{t}: {row_count} rows")
        else:
            err = data.get("status", {}).get("error", {}).get("message", "unknown")
            print(f"{t}: ERROR - {err[:150]}")
    except Exception as e:
        print(f"{t}: EXCEPTION - {e}")
