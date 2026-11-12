import hashlib
import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research/xrp_intelligence/20261108T121933Z-coinbase-xpm-and-sbi-arc-validator-correction.json"
)
COINBASE_TARGET = (
    Path(__file__).resolve().parents[1]
    / "research/xrp_intelligence/20261104T114254Z-coinbase-circle-ripple-collateral-stablecoin-network.json"
)
SBI_ARC_TARGET = (
    Path(__file__).resolve().parents[1]
    / "research/xrp_intelligence/20261104T131226Z-circle-q3-coinbase-ripple-bny-sbic-market-addendum.json"
)


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_correction_source_excerpt_hashes_verify():
    data = _load(ARTIFACT)
    assert data["source_count"] == 4
    for source in data["source_records"]:
        assert source["raw_http_bytes_captured"] is False
        assert hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest() == source["excerpt_sha256"]
        assert source["model_eligible"] is False


def test_coinbase_xpm_dash_is_null_not_zero():
    original = _load(COINBASE_TARGET)
    correction = _load(ARTIFACT)
    prior = original["product_scope_matrix"][1]
    assert prior["haircut_cross_portfolio_margin_pct"] == 0
    corrected = correction["corrected_views"]["coinbase_global_derivatives_xrp"]
    assert corrected["xrp_accepted_as_cross_collateral"] is True
    assert corrected["xpm_haircut_pct"] is None
    assert corrected["xpm_haircut_status"] == "NOT_NUMERICALLY_SPECIFIED_DASH_IN_SOURCE"
    assert corrected["xsm_haircut_pct"] == 15
    source = next(x for x in correction["source_records"] if x["id"] == "coinbase_global_derivatives_cross_collateral_20261108")
    assert source["excerpt"] == "XRP ✓ - - 15%"


def test_sbi_arc_validator_has_primary_circle_support_but_not_live_node_proof():
    original = _load(SBI_ARC_TARGET)
    correction = _load(ARTIFACT)
    edge = next(x for x in original["relationships"] if x["from"] == "SBI Group" and x["to"] == "Circle Arc")
    assert edge["evidence_source_ids"] == ["circle_q3_2026_presentation", "sbi_circle_jv"]
    corrected = correction["corrected_views"]["sbi_circle_arc"]
    assert corrected["validator_designation"] == "NAMED_FOUNDING_VALIDATOR_BY_CIRCLE"
    assert corrected["live_node_operation_independently_verified"] is False
    assert corrected["network_is_xrpl"] is False
    assert corrected["arc_native_fee_asset"] == "USDC"
    assert "circle_arc_founding_validator_20260805" in corrected["source_ids"]
    assert "circle_arc_mainnet_launch_20260916" in corrected["source_ids"]


def test_sbi_arc_presale_total_is_not_attributed_to_sbi():
    corrected = _load(ARTIFACT)["corrected_views"]["sbi_arc_presale"]
    assert corrected["participation_through_consolidated_subsidiary"] is True
    assert corrected["consortium_raise_usd_m"] == 222
    assert corrected["sbi_individual_allocation_usd"] is None
    assert corrected["allocation_status"] == "UNDISCLOSED"
    assert corrected["xrp_purchase"] is False


def test_arc_and_coinbase_collateral_are_not_misreported_as_xrp_demand():
    data = _load(ARTIFACT)
    relevance = data["xrp_relevance"]
    assert relevance["arc_is_xrpl"] is False
    assert relevance["direct_xrp_demand_from_arc_validator_role_proven"] is False
    assert relevance["direct_xrp_demand_from_arc_presale_proven"] is False
    assert relevance["actual_coinbase_xrp_collateral_balances_disclosed"] is False
    assert data["model_admission"]["eligible"] is False
    assert data["forecast_status"] == "NOT_ISSUED"
