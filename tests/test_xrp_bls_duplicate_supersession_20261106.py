from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORRECTION = ROOT / "research" / "xrp_intelligence" / "20261106T1350Z-bls-event-duplicate-supersession.json"


def _load(path: str) -> tuple[dict, str]:
    raw = (ROOT / path).read_text(encoding="utf-8")
    return json.loads(raw), raw


def _git_blob_sha(raw: str) -> str:
    payload = raw.encode("utf-8")
    header = f"blob {len(payload)}\\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def test_duplicate_bls_capture_is_preserved_but_not_counted_twice() -> None:
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    duplicate_ref = correction["source_artifacts"][0]
    canonical_ref = correction["source_artifacts"][1]
    duplicate, duplicate_raw = _load(duplicate_ref["path"])
    canonical, canonical_raw = _load(canonical_ref["path"])

    assert _git_blob_sha(duplicate_raw) == duplicate_ref["git_blob_sha1"]
    assert _git_blob_sha(canonical_raw) == canonical_ref["git_blob_sha1"]
    assert duplicate["event"]["release_id"] == correction["duplicate_comparison"]["bls_release_id"]
    assert canonical["macro"]["release"] == "US Employment Situation — October 2026"
    assert duplicate["xrp_market_observation"]["raw_response_rendered_sha256"] == correction["duplicate_comparison"]["kraken_rendered_response_sha256"]
    canonical_kraken = next(
        source for source in canonical["source_registry"]
        if source["id"] == "kraken_xrp_usd_post_release_ticker"
    )
    assert canonical_kraken["receipt"]["digest"] == correction["duplicate_comparison"]["kraken_rendered_response_sha256"]
    assert correction["duplicate_comparison"]["duplicate_and_canonical_market_response_digest_matches"] is True
    assert correction["application_contract"]["original_artifacts_mutated"] is False
    assert correction["application_contract"]["duplicate_artifact_deleted"] is False
    assert "Count only the canonical artifact" in correction["application_contract"]["archive_view_rule"]
    assert correction["application_contract"]["model_eligible"] is False
    assert correction["forecast_status"] == "NOT_ISSUED"
    assert canonical["model_admission"]["eligible_for_feature_store"] is False
    assert canonical["forecast"]["status"] == "NOT_ISSUED"
