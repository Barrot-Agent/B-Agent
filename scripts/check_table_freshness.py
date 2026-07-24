#!/usr/bin/env python3
import os
import requests

host = os.environ["DATABRICKS_HOST"]
token = os.environ["DATABRICKS_TOKEN"]
warehouse = os.environ["DATABRICKS_WAREHOUSE_ID"]

sql = (
    "SELECT COUNT(*) AS total_rows, "
    "MAX(timestamp) AS latest_row, "
    "SUM(CASE WHEN timestamp > current_timestamp() - INTERVAL 24 HOURS THEN 1 ELSE 0 END) AS rows_last_24h "
    "FROM barrot_omega.xrp_liquidity_signals"
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
print(data.get("result", {}).get("data_array"))
