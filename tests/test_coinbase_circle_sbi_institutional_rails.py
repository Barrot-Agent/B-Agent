import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "xrp_intelligence"


def load(path):
    return json.loads((DATA / path).read_text(encoding="utf-8"))


def test_coinbase_rlusd_listing_separates_network_access_from_xrp_demand():
    snapshot = load("snapshots/20261031T150000Z-coinbase-circle-sbi-ripple-institutional-rails.json")
    rlusd = snapshot["institutional_rails"]["coinbase_rlusd"]
    assert rlusd["status"] == "LAUNCHED_IN_SUPPORTED_REGIONS"
    assert set(rlusd["supported_networks"]) == {"XRP Ledger", "Base", "Ethereum"}
    assert rlusd["global_exchange_rlusd_collateral"] == "PLANNED_NOT_AVAILABLE_AT_LAUNCH"
    assert rlusd["actual_xrp_purchase_or_collateral"] == "NOT_ESTABLISHED"


def test_coinbase_q3_metrics_are_platform_context_not_xrp_metrics():
    snapshot = load("snapshots/20261031T150000Z-coinbase-circle-sbi-ripple-institutional-rails.json")
    q3 = snapshot["institutional_rails"]["coinbase_q3_2026"]
    assert q3["crypto_trading_volume_market_share_percent"] == 10.7
    assert q3["average_usdc_held_usd"] == 22_000_000_000
    assert q3["stablecoin_revenue_usd"] == 307_000_000
    assert q3["xrp_specific_revenue_or_volume"] == "NOT_DISCLOSED"


def test_ripple_trust_bank_charter_does_not_imply_xrp_reserves():
    snapshot = load("snapshots/20261031T150000Z-coinbase-circle-sbi-ripple-institutional-rails.json")
    bank = snapshot["institutional_rails"]["ripple_national_trust_bank"]
    assert bank["charter_number"] == "25364"
    assert bank["consummated_effective_date"] == "2026-10-26"
    assert bank["trust_powers_requested"] is True
    assert bank["xrp_reserve_or_collateral"] == "NOT_ESTABLISHED"


def test_aviva_fund_investment_is_not_classified_as_xrp_capital():
    snapshot = load("snapshots/20261031T150000Z-coinbase-circle-sbi-ripple-institutional-rails.json")
    aviva = snapshot["institutional_rails"]["aviva_xrpl_tokenized_gbp_fund"]
    assert aviva["investment_in_new_tokenized_share_class_gbp"] == 50_000_000
    assert aviva["underlying_fund_aum_gbp_approx"] == 22_000_000_000
    assert aviva["structure"].startswith("DIGITAL_TWIN")
    assert aviva["xrp_purchased_gbp"] == "UNKNOWN"


def test_standard_chartered_custody_is_live_but_lmax_collateral_is_planned():
    snapshot = load("snapshots/20261031T150000Z-coinbase-circle-sbi-ripple-institutional-rails.json")
    sc = snapshot["institutional_rails"]["standard_chartered_rlusd"]
    assert sc["custody_status"] == "LIVE_FOR_ELIGIBLE_CLIENTS"
    assert sc["lmax_collateral_mirroring"] == "PLANNED_NOT_LIVE"


def test_sbi_reward_products_do_not_claim_market_purchases():
    snapshot = load("snapshots/20261031T150000Z-coinbase-circle-sbi-ripple-institutional-rails.json")
    sbi = snapshot["institutional_rails"]["sbi_distribution"]
    assert "XRP" in sbi["visa_card"]["selectable_assets"]
    assert sbi["visa_card"]["realized_xrp_reward_units"] == "UNKNOWN"
    assert sbi["visa_card"]["inventory_source"] == "UNKNOWN"
    assert sbi["accumulation_amount_and_xrp_units"] == "UNKNOWN"


def test_graph_edges_reference_registered_or_prior_sbi_sources():
    graph = load("relationship_graph_addenda/20261031T150000Z-coinbase-circle-sbi-ripple-institutional-rails.json")
    bundle = load("sources/coinbase_circle_sbi_institutional_rails_20261031.json")
    ids = {source["source_id"] for source in bundle["sources"]}
    ids.update({
        "SRC-SBI-VISA-CRYPTO-CARD-CURRENT-TERMS-20261031",
        "SRC-SBI-VC-TRADE-ACCUMULATION-20261031",
        "SRC-SBI-ORICO-XRP-POINTS-20260731",
        "SRC-SBI-RLUSD-LISTING-20260624",
        "SRC-SBI-CIRCLE-JV-20250822",
        "SRC-CIRCLE-ARC-SBI-VALIDATOR-20260916",
    })
    assert graph["edges"]
    assert all(set(edge["source_ids"]).issubset(ids) for edge in graph["edges"])


def test_hypotheses_preserve_disconfirming_evidence_and_no_forecast():
    snapshot = load("snapshots/20261031T150000Z-coinbase-circle-sbi-ripple-institutional-rails.json")
    assert snapshot["hypotheses"]
    assert all(h["disconfirming_evidence"] for h in snapshot["hypotheses"])
    assert snapshot["feature_admission"]["forecast_status"] == "NOT_ISSUED"
    assert snapshot["feature_admission"]["xrp_directional_feature"] == "NOT_ADMITTED"


def test_source_bundle_has_primary_provenance_and_limitations():
    bundle = load("sources/coinbase_circle_sbi_institutional_rails_20261031.json")
    assert len(bundle["sources"]) >= 10
    assert all(source["url"].startswith("https://") for source in bundle["sources"])
    assert all(source["limitations"] for source in bundle["sources"])
    assert len({source["independence_group"] for source in bundle["sources"]}) >= 6
