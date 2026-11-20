from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORRECTION = ROOT / "research/xrp_intelligence/20261108T071027Z-xrp-exchange-wallet-reserve-component-disagreement-correction.json"
ORIGINAL = ROOT / "research/xrp_intelligence/20261108T070200Z-xrp-market-etf-exchange-derivatives-macro-reconciliation.json"


def test_exchange_reserve_component_disagreement_is_preserved_not_averaged() -> None:
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    original = json.loads(ORIGINAL.read_text(encoding="utf-8"))

    assert correction["original_artifact_preserved"] is True
    assert ORIGINAL.exists()
    assert correction["source_internal_disagreement"]["status"] == "UNRESOLVED_SOURCE_INTERNAL_DISAGREEMENT"
    assert correction["source_internal_disagreement"]["table_section"]["binance_peg_xrp_reserve"] == 327_400_000
    assert correction["source_internal_disagreement"]["methodology_section"]["binance_peg_xrp_reserve"] == 325_800_000
    assert correction["source_internal_disagreement"]["methodology_section"]["stated_non_customer_reserve_total"] == 487_800_000
    assert correction["source_internal_disagreement"]["derived_reconciliation"]["table_component_sum_xrp"] == 489_400_000
    assert correction["source_internal_disagreement"]["derived_reconciliation"]["methodology_component_sum_xrp"] == 487_800_000
    assert correction["source_internal_disagreement"]["derived_reconciliation"]["binance_component_difference_xrp"] == 1_600_000
    assert correction["model_admission"]["eligible"] is False
    assert correction["forecast_status"] == "NOT_ISSUED"

    for receipt in correction["source_receipts"]:
        actual = hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest()
        assert actual == receipt["excerpt_sha256"]

    assert original["exchange_wallets"]["exchange_balances"][2]["includes_binance_peg_reserve_xrp"] == 327_400_000
    assert original["exchange_wallets"]["non_customer_reserve_total_xrp"] == 487_800_000
