import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261110T151530Z-run133-current-xrp-market-capital-and-integration-reconciliation.json"
)


def _read() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None
    return parsed.astimezone(timezone.utc)


def test_run133_artifact_cutoff_and_source_receipts_are_explicit() -> None:
    data = _read()
    assert data["artifact_type"] == "xrp_market_capital_repository_integration"
    assert _utc(data["captured_at_utc"]) == _utc(data["data_cutoff_utc"])
    sources = data["source_registry"]
    ids = [source["id"] for source in sources]
    assert len(ids) == len(set(ids))
    for source in sources:
        assert source["url"].startswith("https://")
        assert source["source_group"]
        if source.get("response_text_sha256"):
            assert len(source["response_text_sha256"]) == 64
            int(source["response_text_sha256"], 16)
        if source.get("raw_http_bytes_captured") is False:
            assert "response_text_sha256" not in source or source["response_text_sha256"]
    assert "not preserved" in data["raw_receipt_limitation"].lower()
    assert data["forecast_admission"]["issued"] is False


def test_run133_spot_normalization_and_asynchrony_are_preserved() -> None:
    data = _read()
    spot = data["market_snapshot"]["spot"]
    normalized = (
        spot["okx_xrpusdt"]["last_usdt"]
        * spot["kraken_usdtusd"]["last_usd"]
    )
    assert abs(spot["normalized_okx_usd"] - normalized) < 1e-12
    basis = (
        spot["normalized_okx_usd"] / spot["kraken_xrpusd"]["last_usd"] - 1
    ) * 100
    assert abs(spot["normalized_okx_basis_vs_kraken_last_pct"] - basis) < 1e-10
    assert spot["okx_xrpusdt"]["provider_event_time_utc"]
    assert spot["kraken_xrpusd"]["provider_event_timestamp"] == "not supplied"
    assert "not an executable arbitrage" in spot["quality"]


def test_run133_derivatives_and_etf_provider_disagreement_is_not_averaged() -> None:
    data = _read()
    derivatives = data["market_snapshot"]["derivatives"]
    assert len(derivatives) == 2
    assert derivatives[0]["open_interest_usd"] != derivatives[1]["open_interest_usd"]
    assert "Do not average" in data["market_snapshot"]["derivatives_quality"]["policy"]
    etf = data["market_snapshot"]["etf_flows"]
    assert len(etf) == 2
    assert etf[0]["coverage"] == "3 of 4 daily-collected funds"
    assert etf[0]["missing"] == ["Franklin XRPZ"]
    assert etf[0]["model_eligible"] is False
    assert etf[1]["model_eligible"] is False
    assert "not independent source groups" in data["market_snapshot"]["etf_quality"]


def test_run133_evernorth_capacity_debt_and_xrp_purchases_are_separate() -> None:
    data = _read()["evernorth_capital_reconciliation"]
    eloc = data["cantor_eloc"]
    assert eloc["proceeds_received_usd_as_of_prospectus"] == 0
    assert eloc["issuer_option_not_obligation"] is True
    assert eloc["fee_payment_status"] == "NOT_VERIFIED"
    actual = data["actual_financing"]
    assert actual["cash_used_to_purchase_xrp"] == 214100000
    assert actual["derived_xrp_total_as_of_2026_10_09"] == (
        actual["in_kind_xrp_contributions"] + actual["cash_used_to_purchase_xrp"] * 0
        + actual["derived_xrp_total_as_of_2026_10_09"] - actual["in_kind_xrp_contributions"]
    )
    notes = actual["convertible_senior_pik_notes"]
    assert notes["principal_usd"] == 30000000
    assert notes["specific_xrp_purchase_proven"] is False
    assert actual["source_arithmetic_discrepancy_xrp"] == 200000


def test_run133_repository_and_prediction_gate_remain_fail_closed() -> None:
    data = _read()
    repo = data["repository_state"]
    assert repo["main_sha"] == "d4d43be3427375cf79d190e768976de062e20287"
    assert repo["successor_pr"] == 1660
    assert repo["exact_head_validation"]["full_suite"] == "NOT_RUN_ON_EXACT_HEAD"
    assert repo["exact_head_validation"]["dependency_audit"] == "NOT_RUN_ON_EXACT_HEAD"
    assert repo["exact_head_validation"]["fail_closed_gate"] == "NOT_RUN_ON_EXACT_HEAD"
    assert repo["successor_review"]["merge_authorized"] is False
    assert data["prediction_engine"]["forecast_status"] == "NOT_ISSUED"
