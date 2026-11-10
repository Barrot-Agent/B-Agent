import json
from decimal import Decimal, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261108T150549Z-xrp-historical-daily-open-and-evernorth-debt-correction.json"
KRAKEN_PRIOR = ROOT / "research/xrp_intelligence/20261104T113845Z-live-spot-derivatives-etf-reconciliation.json"
CIRCLE_PRIOR = ROOT / "research/xrp_intelligence/20261104T131226Z-circle-q3-coinbase-ripple-bny-sbic-market-addendum.json"
EVERNORTH_PRIOR = ROOT / "research/xrp_intelligence/20261104T134706Z-evernorth-close-actual-capital-sbi-ownership-reconciliation.json"
COST_CORRECTION = ROOT / "research/xrp_intelligence/20261107T113335Z-evernorth-c07-average-cost-correction-supersession.json"
CAPITAL_RECONCILIATION = ROOT / "research/xrp_intelligence/20261108T140510Z-evernorth-closing-capital-and-xrp-flow-reconciliation.json"
FINAL_DEBT_RECONCILIATION = ROOT / "research/xrp_intelligence/20261108T044733Z-evernorth-capital-structure-final-reconciliation.json"
ARC_CORRECTION = ROOT / "research/xrp_intelligence/20261108T121933Z-coinbase-xpm-and-sbi-arc-validator-correction.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_kraken_utc_daily_open_semantics_supersede_both_legacy_labels():
    overlay = load(ARTIFACT)
    prior_kraken = load(KRAKEN_PRIOR)
    prior_circle = load(CIRCLE_PRIOR)
    correction = next(x for x in overlay["corrections"] if x["correction_id"] == "kraken_utc_daily_open_semantics")
    assert prior_kraken["market_snapshot"]["spot"][0]["open_24h_usd"] == 1.27513
    assert prior_kraken["market_snapshot"]["spot"][0]["last_vs_open_pct"] is not None
    assert prior_circle["market_observations"][0]["open_24h_usd"] == 1.27513
    mappings = {(x["target_artifact"], x["json_pointer"]): x for x in correction["field_mappings"]}
    assert mappings[(str(KRAKEN_PRIOR.relative_to(ROOT)), "/market_snapshot/spot/0/open_24h_usd")]["canonical_semantic_name"] == "utc_daily_open_usd"
    assert mappings[(str(KRAKEN_PRIOR.relative_to(ROOT)), "/market_snapshot/spot/0/last_vs_open_pct")]["canonical_semantic_name"] == "last_vs_utc_daily_open_pct"
    assert mappings[(str(CIRCLE_PRIOR.relative_to(ROOT)), "/market_observations/0/open_24h_usd")]["canonical_semantic_name"] == "utc_daily_open_usd"
    assert "not the price exactly 24 hours" in correction["canonical_interpretation"]


def test_evernorth_one_million_facility_is_ripple_debt_not_kyobo_note():
    overlay = load(ARTIFACT)
    prior = load(EVERNORTH_PRIOR)
    final = load(FINAL_DEBT_RECONCILIATION)
    correction = next(x for x in overlay["corrections"] if x["correction_id"] == "evernorth_facility_counterparty_and_graph_deduplication")
    assert prior["capital_reconciliation"]["additional_debt_capital"][2]["source"].startswith("NH Investment")
    assert prior["additional_credit_facilities"][0]["lender"] == "Ripple Labs Inc."
    assert correction["field_correction"]["canonical_value"] == "Ripple Labs Inc."
    assert final["entity_liquidity_and_debt"]["evernorth_facility"]["lender"] == "Ripple Labs Inc."
    assert final["entity_liquidity_and_debt"]["evernorth_facility"]["borrowed_as_of_2026_06_30_usd"] == 0
    assert final["entity_liquidity_and_debt"]["convertible_notes"]["principal_usd"] == 30_000_000
    note = correction["canonical_debt_view"]["separate_convertible_note"]
    assert note["principal_usd"] == 30_000_000
    assert note["purchaser"].startswith("NH Investment & Securities")


def test_duplicate_ripple_facility_edges_are_counted_once():
    overlay = load(ARTIFACT)
    prior = load(EVERNORTH_PRIOR)
    graph = prior["ownership_and_relationship_graph"]
    correction = next(x for x in overlay["corrections"] if x["correction_id"] == "evernorth_facility_counterparty_and_graph_deduplication")
    assert graph[9]["to"] == graph[13]["to"] == "Evernorth Holdings Inc. (Pubco)"
    assert graph[10]["to"] == graph[12]["to"] == "Pathfinder Digital Assets LLC"
    assert correction["graph_deduplication"] == [
        {"prior_array_indices": [9, 13], "from": "Ripple Labs", "to": "Evernorth Holdings Inc. (Pubco)", "facility_id": "evernorth_facility_1m", "canonical_edge_id": "ripple_to_pubco_evernorth_facility_1m", "count_once": True},
        {"prior_array_indices": [10, 12], "from": "Ripple Labs", "to": "Pathfinder Digital Assets LLC", "facility_id": "pathfinder_company_facility_10m", "canonical_edge_id": "ripple_to_pathfinder_company_facility_10m", "count_once": True},
    ]
    ids = [x["edge_id"] for x in correction["canonical_debt_view"]["canonical_relationship_edges"]]
    assert len(ids) == len(set(ids)) == 4


def test_existing_purchase_cost_and_arc_validator_corrections_remain_canonical():
    overlay = load(ARTIFACT)
    cost = load(COST_CORRECTION)
    capital = load(CAPITAL_RECONCILIATION)
    arc = load(ARC_CORRECTION)
    assert cost["correction"]["canonical_value"] == 2.53657058
    with localcontext() as context:
        context.prec = 50
        exact = Decimal("214000000") / Decimal("84365876.3625")
        stored = Decimal(str(cost["correction"]["exact_unrounded_recomputed_value"]))
        assert abs(stored - exact) < Decimal("0.000000000000001")
        assert stored.quantize(Decimal("0.00000001")) == Decimal("2.53657058")
    assert capital["capital_ledger"]["actual_xrp_purchase"]["cash_used_usd"] == 214_000_000
    assert capital["capital_ledger"]["actual_xrp_purchase"]["xrp_purchased"] == 84_365_876.3625
    assert capital["capital_ledger"]["actual_xrp_purchase"]["average_price_usd"] == 2.53657058
    assert arc["corrected_views"]["sbi_circle_arc"]["source_ids"] == ["circle_arc_founding_validator_20260805", "circle_arc_mainnet_launch_20260916"]
    assert overlay["append_only"] is True


def test_corrections_remain_model_ineligible_and_issue_no_forecast():
    overlay = load(ARTIFACT)
    assert overlay["model_admission"]["eligible"] is False
    assert overlay["forecast_status"] == "NOT_ISSUED"
