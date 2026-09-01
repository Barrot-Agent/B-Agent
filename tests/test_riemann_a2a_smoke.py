import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


harvest = load_module("riemann_harvest", ROOT / "barrot_agent/ingestion" / "riemann_harvest.py")

assert harvest.classify_evidence("Numerical verification of zeros", "") == "computational_evidence"

assert harvest.classify_evidence("A new conjecture", "") == "conjecture_or_hypothesis"


assert corpus_file.exists(), "A2A corpus was not generated"

corpus_text = corpus_file.read_text(encoding="utf-8")
assert "RIEMANN_RESEARCH_CORPUS" in corpus_text
assert '"read_only": true' in corpus_text.lower()

worker = (ROOT / "a2a" / "worker.js").read_text(encoding="utf-8")
assert 'id: "riemann-research"' in worker
assert 'method === "research/riemann"' in worker
assert "RIEMANN_RESEARCH_CORPUS" in worker

print("RIEMANN + A2A INTEGRATION SMOKE TEST: PASS")
