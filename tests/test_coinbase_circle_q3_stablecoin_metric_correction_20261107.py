import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "research/xrp_intelligence/20261107T180947Z-coinbase-circle-sbi-q3-network-economics-update.json"
CORRECTION = ROOT / "research/xrp_intelligence/20261107T181119Z-coinbase-circle-q3-stablecoin-metric-correction.json"


def test_correction_is_append_only_and_binds_the_original_artifact():
    original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    assert correction["append_only"] is True
    assert correction["supersedes_artifact_path"] == str(ORIGINAL.relative_to(ROOT))
    assert correction["supersedes_artifact_git_blob_sha1"] == "10a50efc8863ba318fe944e37f2ef7f7a637ea92"
    assert original["q3_2026_economics"]["coinbase"]["total_stablecoin_revenue_usd"] == 328_000_000


def test_official_coinbase_sec_exhibit_controls_q3_stablecoin_revenue():
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    primary = correction["corrected_primary_source"]
    assert primary["q3_stablecoin_revenue_usd"] == 307_000_000
    assert primary["q3_stablecoin_revenue_growth_qoq_percent"] == 5
    assert primary["average_usdc_held_in_coinbase_products_usd"] == 22_000_000_000
    assert primary["average_off_platform_usdc_balances_usd"] == 51_000_000_000
    assert primary["revenue_split_on_vs_off_platform_disclosed"] is False
    assert "202 million" not in primary["exact_interpretation"].lower()


def test_circle_costs_and_coinbase_revenue_are_not_netted():
    circle = json.loads(CORRECTION.read_text(encoding="utf-8"))["circle_side_unchanged"]
    assert circle["q3_coinbase_related_distribution_costs_usd"] == 331_300_000
    assert circle["nine_month_coinbase_related_distribution_costs_usd"] == 986_600_000
    assert "not Coinbase profit/loss" in circle["comparability"]


def test_corrected_receipts_match_exact_excerpt_hashes():
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    for receipt in correction["source_receipts"]:
        assert receipt["receipt_kind"] == "normalized_text_excerpt"
        assert re.fullmatch(r"[0-9a-f]{64}", receipt["sha256"])
        assert hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest() == receipt["sha256"]


def test_correction_remains_model_ineligible_and_does_not_issue_forecast():
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    assert correction["model_admission"] is False
    assert correction["forecast_status"] == "NOT_ISSUED"
