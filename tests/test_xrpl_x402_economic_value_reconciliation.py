from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/xrp_intelligence/snapshots/20261102T000046Z-xrpl-x402-economic-value-reconciliation.json"


def load_snapshot():
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def test_t54_count_and_settled_value_are_separate_metrics():
    d = load_snapshot()["t54_dashboard"]
    assert d["reported_all_time_settled_transactions"] == 14_850_938
    assert d["reported_all_time_settled_value_usd"] == 48_848.00
    assert d["reported_registered_merchants"] == 183
    assert d["reported_live_services"] == 5_318
    assert 0.0032 < d["calculated_mean_settled_value_per_reported_transaction_usd"] < 0.0034
    assert any("not independently reconciled" in x for x in d["limitations"])


def test_three_address_overlap_does_not_claim_same_transaction_identity():
    d = load_snapshot()["address_overlap"]
    assert d["status"] == "CONFIRMED_DESTINATION_ADDRESS_OVERLAP"
    assert d["same_transaction_identity"] == "UNVERIFIED"
    assert d["raw_source_tag_join_performed"] is False
    assert d["facilitator_source_tag"] == 804681468
    assert d["operator_attribution"] == "UNKNOWN"
    assert {x["address"] for x in d["addresses"]} == {
        "rBi1QrVjwaNofisZAQnovoXdHkS73FG1tJ",
        "ra9b6JX5aPVbdJhogDDddsRAcasWg7gzC3",
        "rMPwy3Ntx56Nyc2fKGNm7VRWdmpHSB92Z7",
    }


def test_bitquery_gross_volume_is_not_net_capital_or_xrp_demand():
    d = load_snapshot()["bitquery_rlusd_window"]
    assert d["share_to_three_collectors_pct"] == 99.6
    assert d["total_rlusd_carried_by_dust_payments"] == 7722
    assert d["gross_value_of_payments_at_least_1_rlusd_usd"] == 7_330_000_000
    assert d["top_ten_sender_share_pct"] == 82
    assert d["round_trip_gross_volume_contribution_rlusd"] == 848_000_000
    assert any("not net external capital" in x for x in d["limitations"])


def test_t54_directory_and_homepage_counts_are_not_conflated():
    d = load_snapshot()
    assert d["t54_dashboard"]["reported_registered_merchants"] == 183
    assert d["t54_directory"]["reported_merchant_addresses"] == 157
    assert d["t54_dashboard"]["reported_live_services"] == 5318
    assert d["t54_directory"]["reported_service_entries"] == 33
    assert d["t54_directory"]["limitations"]


def test_ask_surf_is_not_permission_coin_ask():
    d = load_snapshot()["ask_coin_disambiguation"]
    assert d["t54_directory_merchant"] == "AskSurf"
    assert d["relationship_to_permission_coin_ask"] == "NO_RELATIONSHIP_ESTABLISHED"
    assert "not evidence" in d["note"]
