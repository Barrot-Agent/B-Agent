import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/research/riemann_hypothesis_harvest.json"

subprocess.run(
    [sys.executable,
     str(ROOT / "barrot_agent/ingestion/corroborate_riemann_research.py")],
    check=True,
)

data = json.loads(SOURCE.read_text(encoding="utf-8"))
assert data.get("records"), "No Riemann research records found"
assert data["corroboration_policy"]["mathematical_verification"] is False

for record in data["records"]:
    c = record.get("corroboration", {})
    assert c.get("mathematical_verification") is False
    assert c.get("status") in {
        "metadata_corroborated",
        "single_source_metadata",
    }

print("RIEMANN CORROBORATION SMOKE TEST: PASS")
