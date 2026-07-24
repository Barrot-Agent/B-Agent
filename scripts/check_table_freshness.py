#!/usr/bin/env python3
import os
import requests

host = os.environ["DATABRICKS_HOST"]
token = os.environ["DATABRICKS_TOKEN"]
warehouse = os.environ["DATABRICKS_WAREHOUSE_ID"]

sql = (
    "SELECT table_catalog, table_schema, table_name "
    "FROM system.information_schema.tables "
    "WHERE table_name ILIKE '%liquidity%' OR table_schema ILIKE '%barrot%'"
)

r = requests.post(
    f"https://{host}/api/2.0/sql/statements",
    headers={"Authorization": f"Bearer {token}"},
    json={"warehouse_id": warehouse, "statement": sql, "wait_timeout": "20s"},
    timeout=30,
)
r.raise_for_status()
data = r.json()
print("HTTP", r.status_code)
import json
print(json.dumps(data, indent=2))
