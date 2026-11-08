from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T061536Z-rlusd-usdc-jpysc-custody-collateral-reconciliation.json"


def _artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_normalized_excerpt_hashes_and_capture_limits_are_explicit():
    data = _artifact()
    assert data["append_only"] is True
    assert data["source_capture_policy"]["raw_http_bytes_preserved"] is False
    assert data["source_capture_policy"]["model_eligible"] is False
    for source in data["source_registry"]:
        excerpt = source["captured_excerpt_text"].encode("utf-8")
        assert hashlib.sha256(excerpt).hexdigest() == source["captured_excerpt_sha256"]
        assert "not page HTML or raw HTTP bytes" in source["hash_scope"]


def test_rlusd_november_snapshot_is_not_misrepresented_as_attestation():
    data = _artifact()
    value = data["balance_snapshot"]["rlusd"]
    assert value["as_of_date"] == "2026-11-05"
    assert value["circulating_supply_m"] == 2632.9
    assert value["reserve_funds_m"] == 2748.0
    assert math.isclose(value["reported_reserve_funds_excess_m"], 115.1, abs_tol=1e-9)
    assert math.isclose(value["reported_reserve_funds_to_circulation_ratio_pct"], 104.37160545406205, rel_tol=1e-12)
    assert "not itself a monthly CPA attestation" in value["interpretation"]
    assert value["model_eligible"] is False


def test_jpysc_lending_balance_is_included_in_handling_total():
    value = _artifact()["balance_snapshot"]["jpysc"]
    assert value["handling_balance_threshold"] == 30_000_000_000
    assert value["lending_balance_threshold"] == 10_000_000_000
    assert value["handling_balance_includes_lending_balance"] is True
    assert value["lending_balance_is_additive_to_handling_balance"] is False
    assert value["exact_balance_disclosed"] is False
    assert value["public_chain_circulation_status"] == "FUTURE_OBJECTIVE_SUBJECT_TO_LEGAL_CHANGES"


def test_entity_roles_and_collateral_status_are_not_conflated():
    data = _artifact()
    roles = data["entity_roles"]
    assert roles["rlusd_issuer"] == "Standard Custody & Trust Company LLC, a Ripple subsidiary and NYDFS-chartered limited-purpose trust company."
    assert "Separate Ripple group" in roles["ripple_national_trust_bank"]
    status = data["custody_collateral_state"]
    assert status["coinbase_global_exchange_rlusd_collateral"] == "FUTURE_NOT_LIVE_IN_LAUNCH_ANNOUNCEMENT"
    assert status["lmax_rlusd_collateral_mirroring"] == "PLANNED_NOT_LIVE"
    assert status["standard_chartered_rlusd_custody_on_xrpl"] == "LIVE_REPORTED"
    assert status["sbi_vctrade_rlusd_chain_support_at_launch"] == ["Ethereum"]
    assert status["sbi_vctrade_xrpl_rlusd_deposits_withdrawals"] == "NOT_CONFIRMED_BY_REVIEWED_PRIMARY_NOTICE"
    assert status["ripple_national_trust_bank_customer_operations"] == "NOT_VERIFIED_COMMENCED"


def test_usdc_secondary_transcription_and_rlusd_supply_event_remain_unconfirmed():
    data = _artifact()
    usdc = data["balance_snapshot"]["usdc"]
    assert usdc["primary_numeric_balance_visible_in_rendered_capture"] is False
    assert usdc["secondary_source_id"] == "cryptoeconomics_usdc_secondary_20261105"
    assert usdc["rlusd_to_usdc_supply_ratio_secondary_pct"] < 4.0
    coindaro = next(s for s in data["source_registry"] if s["id"] == "coindaro_rlusd_xrpl_supply_event_20261102")
    assert coindaro["source_type"] == "secondary_onchain_analysis"
    assert any("not independently reproduced" in v for v in coindaro["limitations"])
    assert data["model_admission"]["forecast_status"] == "NOT_ISSUED"
