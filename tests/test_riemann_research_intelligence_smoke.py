from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
worker = (ROOT / "a2a" / "worker.js").read_text(encoding="utf-8")

required = [
    'method === "research/riemann"',
    "params.evidence_classes",
    "params.query",
    "allowedClasses",
    "mathematical_truth_assessment: false",
    "Returned records are research metadata",
]

for item in required:
    assert item in worker, f"Missing A2A intelligence feature: {item}"

print("RIEMANN RESEARCH INTELLIGENCE SMOKE TEST: PASS")
