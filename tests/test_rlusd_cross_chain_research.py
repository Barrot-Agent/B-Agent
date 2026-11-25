from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from barrot_agent.evolution.rlusd_cross_chain_research import (
    SOURCE_ID,
    RlusdResearchIntegrityError,
    build_research_snapshot,
)

CAPTURED_AT = "2026-11-25T02:19:15Z"
CACHED_AT = 1795573087
SOURCE_URI = "https://xrpldashboard.com/rlusd"


def _html(
    *,
    cached_at: int = CACHED_AT,
    fresh: bool = True,
    events: list[dict[str, object]] | None = None,
    methodology: bool = True,
) -> bytes:
    event_payload = events if events is not None else [
        {
            "chain": "eth",
            "type": "transfer",
            "ts": CACHED_AT - 5,
            "tx": "0x" + "a" * 64,
            "amount": 10,
        },
        {"chain": "xrpl", "type": "trade", "ts": CACHED_AT - 2, "tx": "b" * 64, "amount": 20},
    ]
    markers = (
        "The live supply totals come from totalSupply() on Ethereum and gateway_balances on XRPL."
        if methodology
        else "The live supply totals are displayed here."
    )
    body = f"""<!doctype html><html><body><p>{markers}</p>
<script>
window.__RLUSD_INITIAL__ = {{
  ethSupply: 2027287574.9328895,
  xrplSupply: 762164546.0015165,
  ethMints24h: 549202.77,
  ethBurns24h: 16999999.99,
  xrplNet24h: 5941598.189999223,
  events: {json.dumps(event_payload)},
  cachedAt: {cached_at},
  fresh: {str(fresh).lower()},
}};
</script></body></html>"""
    return body.encode("utf-8")


def _archive(
    tmp_path: Path,
    *,
    html: bytes | None = None,
    captured_at: str = CAPTURED_AT,
    source_uri: str = SOURCE_URI,
    raw_bytes_retained: bool = True,
    payload_path: str | None = None,
    raw_hash_override: str | None = None,
    receipt_count: int = 1,
) -> Path:
    root = tmp_path / "artifact"
    raw_dir = root / "raw" / "sha256"
    raw_dir.mkdir(parents=True)
    payload = html if html is not None else _html()
    digest = hashlib.sha256(payload).hexdigest()
    relative_path = payload_path or f"raw/sha256/{digest}.json"
    if ".." not in Path(relative_path).parts:
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    receipt = {
        "source_id": SOURCE_ID,
        "source_uri": source_uri,
        "captured_at_utc": captured_at,
        "source_data_as_of_utc": None,
        "source_http_date": "Tue, 25 Nov 2026 02:19:15 GMT",
        "source_http_headers": {"age": "0", "content-type": "text/html"},
        "raw_bytes_retained": raw_bytes_retained,
        "raw_content_sha256": raw_hash_override or digest,
        "raw_payload_path": relative_path,
        "receipt_id": "receipt-rlusd-1",
    }
    receipts = [receipt for _ in range(receipt_count)]
    (root / "raw" / "receipts.jsonl").write_text(
        "".join(json.dumps(item) + "\n" for item in receipts), encoding="utf-8"
    )
    return root


def test_fresh_snapshot_is_structured_but_never_model_eligible(tmp_path: Path) -> None:
    result = build_research_snapshot(_archive(tmp_path))
    assert result["status"] == "RESEARCH_ONLY_FRESH"
    assert result["model_eligible"] is False
    assert result["feature_store_admitted"] is False
    observation = result["observations"][0]
    assert observation["source_id"] == SOURCE_ID
    assert observation["derived_source_data_as_of_utc"] == "2026-11-25T02:18:07Z"
    assert observation["cache_age_seconds"] == pytest.approx(68.0, abs=1.0)
    assert observation["quality_gates"]["raw_hash_verified"] is True
    assert observation["quality_gates"]["independent_direct_onchain_crosscheck"] is False
    assert observation["derived_values"]["covered_chain_supply_total_usd"] == pytest.approx(
        2789452120.934406
    )
    shares = (
        observation["derived_values"]["ethereum_share_of_covered_chains"]
        + observation["derived_values"]["xrpl_share_of_covered_chains"]
    )
    assert shares == pytest.approx(1.0)
    assert observation["event_sample"]["sample_count"] == 2
    assert "gross_volume_usd" not in observation["event_sample"]
    assert observation["chain_scope"] == ["Ethereum", "XRPL"]


def test_stale_or_not_fresh_snapshot_is_blocked(tmp_path: Path) -> None:
    stale_html = _html(
        cached_at=CACHED_AT - 600,
        events=[{"chain": "eth", "type": "transfer", "ts": CACHED_AT - 605}],
    )
    result = build_research_snapshot(_archive(tmp_path, html=stale_html))
    assert result["status"] == "BLOCKED_STALE"
    assert result["model_eligible"] is False

    result_false = build_research_snapshot(
        _archive(tmp_path / "false", html=_html(fresh=False))
    )
    assert result_false["status"] == "BLOCKED_STALE"


def test_missing_receipt_is_blocked(tmp_path: Path) -> None:
    root = tmp_path / "empty"
    (root / "raw").mkdir(parents=True)
    (root / "raw" / "receipts.jsonl").write_text("{}\n", encoding="utf-8")
    result = build_research_snapshot(root)
    assert result["status"] == "BLOCKED_MISSING_RECEIPT"
    assert result["observations"] == []


def test_schema_or_methodology_change_is_blocked(tmp_path: Path) -> None:
    result = build_research_snapshot(_archive(tmp_path, html=_html(methodology=False)))
    assert result["status"] == "BLOCKED_SCHEMA_CHANGE"
    assert result["model_eligible"] is False


def test_raw_hash_mismatch_fails_closed(tmp_path: Path) -> None:
    root = _archive(tmp_path, raw_hash_override="0" * 64)
    with pytest.raises(RlusdResearchIntegrityError, match="SHA-256"):
        build_research_snapshot(root)


def test_path_traversal_fails_closed(tmp_path: Path) -> None:
    root = _archive(tmp_path, payload_path="../../outside.json")
    with pytest.raises(RlusdResearchIntegrityError, match="escapes"):
        build_research_snapshot(root)


def test_ambiguous_receipt_is_blocked(tmp_path: Path) -> None:
    result = build_research_snapshot(_archive(tmp_path, receipt_count=2))
    assert result["status"] == "BLOCKED_AMBIGUOUS_RECEIPT"


def test_future_event_timestamp_is_blocked(tmp_path: Path) -> None:
    events = [{"chain": "eth", "type": "transfer", "ts": CACHED_AT + 60}]
    result = build_research_snapshot(_archive(tmp_path, html=_html(events=events)))
    assert result["status"] == "BLOCKED_EVENT_TIME_MISMATCH"


def test_future_dashboard_cache_timestamp_is_blocked(tmp_path: Path) -> None:
    result = build_research_snapshot(_archive(tmp_path, html=_html(cached_at=CACHED_AT + 120)))
    assert result["status"] == "BLOCKED_FUTURE_CACHE_TIME"
    assert result["model_eligible"] is False


def test_source_uri_mismatch_is_blocked(tmp_path: Path) -> None:
    result = build_research_snapshot(
        _archive(tmp_path, source_uri="https://example.invalid/rlusd")
    )
    assert result["status"] == "BLOCKED_SOURCE_URI_MISMATCH"


def test_unretained_raw_payload_is_blocked(tmp_path: Path) -> None:
    result = build_research_snapshot(_archive(tmp_path, raw_bytes_retained=False))
    assert result["status"] == "BLOCKED_RAW_BYTES_NOT_RETAINED"
