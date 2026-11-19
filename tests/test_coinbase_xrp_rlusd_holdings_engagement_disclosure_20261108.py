from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research/xrp_intelligence/20261108T203213Z-coinbase-xrp-rlusd-holdings-engagement-disclosure.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_coinbase_disclosure_excerpt_hash_and_vintage_are_reproducible():
    data = load_artifact()
    receipt = data["source_receipts"][0]
    excerpt = receipt["normalized_excerpt"]
    digest = hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
    assert digest == receipt["normalized_excerpt_sha256"]
    assert digest == "10ddd4cce09faf19d26568fd51f48cfe1e6243df485e967d8aebf0b4ef5961ea"
    assert len(excerpt.split()) <= 25
    assert data["disclosure_vintage"]["coinbase_holdings_as_of_date"] == "2026-03-31"
    assert data["source_capture"]["raw_http_wire_bytes_or_headers_captured"] is False


def test_coinbase_trading_asset_disclosure_marks_xrp_yes_yes():
    row = load_artifact()["observations"]["us_incl_ny_trading_assets"]["xrp"]
    assert row["coinbase_holding"] == "YES"
    assert row["commercial_engagement"] == "YES"


def test_coinbase_custody_table_distinguishes_xrp_cbxrp_and_rlusd():
    rows = load_artifact()["observations"]["coinbase_custody_trust_company"]
    assert rows["xrp"] == {"coinbase_holding": "YES", "commercial_engagement": "YES"}
    assert rows["cbxrp"] == {"coinbase_holding": "YES", "commercial_engagement": "YES"}
    assert rows["rlusd"] == {"coinbase_holding": "NO", "commercial_engagement": "YES"}


def test_commercial_engagement_does_not_prove_direct_ripple_contract():
    row = load_artifact()["commercial_engagement_definition"]
    assert "issuer or an affiliated party" in row["publisher_definition"]
    assert row["direct_counterparty_named"] == "NO"
    assert row["direct_ripple_contract_established"] == "NO"


def test_historical_holding_flags_do_not_establish_current_balances_or_capital():
    data = load_artifact()
    obs = data["observations"]
    assert obs["holdings_amounts_disclosed"] is False
    assert obs["customer_custody_balances_disclosed"] is False
    assert obs["xrp_collateral_balance_disclosed"] is False
    assert obs["rlusd_balance_disclosed"] is False
    assert obs["issuer_or_affiliate_counterparty_identified"] is False
    assert data["interpretation"]["vintage_limit"].find("2026-03-31") >= 0


def test_no_feature_admission_or_directional_forecast():
    data = load_artifact()
    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_probability_issued"] is False
    assert data["external_actions"]["feature_store_write"] is False
    assert data["external_actions"]["paper_trade"] is False
    assert data["external_actions"]["real_money"] is False
