import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/research/riemann_hypothesis_harvest.json"

subprocess.run(
    [sys.executable, str(ROOT / "barrot_agent/ingestion/validate_riemann_research.py")], check=True
)

data = json.loads(SOURCE.read_text(encoding="utf-8"))
records = data.get("records", [])

assert records, "No research records available"
assert data["cross_source_validation"]["independent_mathematical_verification"] is False

for record in records:
    validation = record.get("validation", {})
    assert validation["independent_mathematical_verification"] is False
    assert validation["corroboration_status"] == "source_metadata_only"

print("RIEMANN VALIDATION SMOKE TEST: PASS")
