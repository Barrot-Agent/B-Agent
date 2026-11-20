import hashlib
import json
from pathlib import Path


def test_evernorth_eloc_is_conditional_xrp_funding_not_actual_purchase():
    path = (
        Path(__file__).resolve().parents[1]
        / "research"
        / "xrp_intelligence"
        / "20261107T031158Z-evernorth-cantor-eloc-xrp-use-of-proceeds-and-math-correction.json"
    )
    artifact = json.loads(path.read_text(encoding="utf-8"))

    for source in artifact["source_records"]:
        assert hashlib.sha256(
            source["normalized_excerpt"].encode("utf-8")
        ).hexdigest() == source["normalized_excerpt_sha256"]

    facility = artifact["facility"]
    assert facility["instrument_class"].startswith("committed equity facility")
    assert facility["maximum_new_shares"] == 5_218_935
    assert facility["registration_conditions"]["sec_effective_at_utc"] == "2026-10-30T16:00:00Z"
    assert facility["registration_conditions"]["publicly_documented_conditions_met"] is True
    assert facility["draw_status"].startswith("NO_PURCHASE_NOTICE_OR_DRAW_DISCLOSED")
    assert facility["upfront_commitment_fee_usd"] == 521_893.5
    assert facility["fee_fully_earned_and_non_refundable"] is True
    assert facility["fee_payment_status"] == "NOT_VERIFIED_IN_REVIEWED_PUBLIC_FILINGS"

    use = artifact["xrp_use_of_proceeds"]
    assert "substantial portion" in use["issuer_statement"]
    assert use["actual_xrp_purchase_disclosed"] is False
    assert use["classification"] == "ISSUER_STATED_PROSPECTIVE_INTENTION"

    proceeds = artifact["proceeds_reconciliation"]
    assert proceeds["sec_424b3_summary_table_gross_usd"] == 80_700_000
    assert proceeds["sec_424b3_cover_gross_usd"] == 76_800_000
    assert proceeds["derived_arithmetic"]["ninety_seven_pct_at_14_71_usd"] == 74_467_417.8345
    assert "source-internal inconsistency" in proceeds["finding"]

    dilution = artifact["dilution"]
    assert dilution["pro_forma_total_if_all_issued"] == 31_313_615
    assert round(dilution["new_shares_pct_of_post_issue_total"], 2) == 16.67
    assert artifact["model_admission"]["eligible_as_price_feature"] is False
    assert artifact["model_admission"]["eligible_as_event_timeline"] is True
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["paper_trade_executed"] is False
    assert artifact["forecast"]["real_money_action"] is False
