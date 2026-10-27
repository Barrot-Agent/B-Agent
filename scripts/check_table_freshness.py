#!/usr/bin/env python3
import os
import requests

host = os.environ["DATABRICKS_HOST"]
token = os.environ["DATABRICKS_TOKEN"]
warehouse = os.environ["DATABRICKS_WAREHOUSE_ID"]

import json

def run(sql, label):
    r = requests.post(
        f"https://{host}/api/2.0/sql/statements",
        headers={"Authorization": f"Bearer {token}"},
        json={"warehouse_id": warehouse, "statement": sql, "wait_timeout": "20s"},
        timeout=30,
    )
    d = r.json()
    print(f"=== {label} ===")
    for row in d.get("result", {}).get("data_array", []):
        print(row)
    print()

run(
    "SELECT topic, COUNT(*) AS n FROM workspace.barrot.brain GROUP BY topic ORDER BY n DESC LIMIT 20",
    "top 20 topics by frequency",
)
run(
    "SELECT MIN(timestamp), MAX(timestamp), COUNT(DISTINCT session) AS distinct_sessions FROM workspace.barrot.brain",
    "date range and session count",
)
run(
    "SELECT COUNT(*) FROM workspace.barrot.brain WHERE insight LIKE '%error%' OR insight LIKE '%Rate limit%'",
    "rows that look like error/failure noise",
)
run(
    "SELECT timestamp, topic, insight, session FROM workspace.barrot.brain WHERE insight NOT LIKE '%error%' AND insight NOT LIKE '%Rate limit%' ORDER BY RAND() LIMIT 8",
    "random sample of non-error rows",
)
