import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHARD = ROOT / "data" / "xrp_intelligence" / "ledger_archive" / "v1" / "sources-124-of-124.json"


def test_sbic_east_japan_legal_identity_is_not_inferred_from_sbi_initials():
    shard = json.loads(SOURCE_SHARD.read_text(encoding="utf-8"))
    record = next(x for x in shard["records"] if x["id"] == "SRC-20261031T121200Z-SBI-EAST-JAPAN-PROFILE")
    assert "Tokyo Small and Medium Business Investment & Consultation" in record["title"]
    assert "SBIC East Japan" in record["title"]
    assert "9011001030621" in record["notes"]
    assert "not evidence of an SBI Holdings or SBI VC Trade affiliation" in record["notes"]
