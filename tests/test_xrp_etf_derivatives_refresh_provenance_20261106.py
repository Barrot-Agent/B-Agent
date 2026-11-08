import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T051458Z-xrp-etf-and-derivatives-refresh.json"
)


def test_refresh_keeps_shared_issuer_inputs_in_one_independence_group():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    sources = {item["id"]: item for item in data["source_registry"]}
    assert (
        sources["CRYPTOKEYHOLE_XRP_ETF_20261106T0443Z"]["independence_group"]
        == sources["XRP_INSIGHTS_XRP_ETF_20261106T040632Z"]["independence_group"]
    )
    assert (
        sources["TRADRADAR_XRP_PERPETUALS_20261106T0355Z"]["independence_group"]
        != sources["CRYPTOKEYHOLE_XRP_ETF_20261106T0443Z"]["independence_group"]
    )


def test_refresh_is_research_only_without_raw_receipts_or_synchronized_cutoff():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["capture"]["synchronized_model_cutoff_utc"] is None
    assert data["capture"]["raw_http_wire_bytes_captured"] is False
    assert all(item["raw_source_bytes_captured"] is False for item in data["source_registry"])
    assert all(item["model_eligible"] is False for item in data["source_registry"])
    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["issued"] is False
