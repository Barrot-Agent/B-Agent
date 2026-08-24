import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/research/riemann_hypothesis_harvest.json"

subprocess.run(
    [sys.executable,
     str(ROOT / "barrot_agent/ingestion/score_riemann_research.py")],
    check=True,
)

data = json.loads(SOURCE.read_text(encoding="utf-8"))
assert data.get("records"), "No research records found"
assert data["quality_gate_policy"]["mathematical_verification"] is False

for record in data["records"]:
    gate = record.get("quality_gate", {})
    assert 0 <= gate.get("metadata_quality_score", -1) <= 100
    assert gate.get("mathematical_truth_assessment") is False

print("RIEMANN QUALITY GATE SMOKE TEST: PASS")
