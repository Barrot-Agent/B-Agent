from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261103T223100Z-circle-ripple-coinbase-bank-charter-stablecoin-network.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_circle_q2_2026_sec_filing_uses_correct_10q_accession():
    data = load()
    url = data["source_corrections"]["corrected_sec_q2_2026_10q"]
    assert url.endswith("/000187604226000248/crcl-20260630.htm")
    assert "000187604226000045" in data["source_corrections"]["rejected_sec_accession"]
    assert "000187604226000045" not in url


def test_circle_occ_charter_is_finally_approved_and_effective():
    data = load()
    item = data["bank_charter_status"]["circle"]
    assert item["final_approval_announcement_date"] == "2026-07-10"
    assert item["occ_cas_effective_date"] == "2026-07-24"
    assert "D79Z71vmerN8" in item["sources"][0]
    assert "not an ordinary deposit-taking" in item["issuer_boundary"]


def test_ripple_occ_charter_is_effective_and_issuer_boundary_is_preserved():
    data = load()
    item = data["bank_charter_status"]["ripple"]
    assert item["final_approval_announcement_date"] == "2026-10-26"
    assert item["occ_cas_effective_date"] == "2026-10-26"
    assert "RjzoD2gxmYOv" in item["sources"][0]
    assert "Standard Custody & Trust Company" in item["issuer_boundary"]


def test_coinbase_occ_cas_effective_status_supersedes_conditional_only_snapshot():
    data = load()
    item = data["bank_charter_status"]["coinbase"]
    assert item["conditional_approval_date"] == "2026-04-02"
    assert item["occ_cas_effective_date"] == "2026-11-06"
    assert item["status"] == "OCC_CAS_CONSUMMATED_EFFECTIVE_2026_11_06"
    assert "NOT_LOCATED" in item["separate_final_approval_document"]
    assert "3RAoRRek6o4j" in item["sources"][0]


def test_three_national_trust_banks_have_distinct_occ_cas_records():
    data = load()
    ids = [
        "D79Z71vmerN8",
        "RjzoD2gxmYOv",
        "3RAoRRek6o4j",
    ]
    urls = data["source_corrections"]["occ_cas_records"]
    assert len(set(ids)) == 3
    assert "D79Z71vmerN8" in urls["circle"]
    assert "RjzoD2gxmYOv" in urls["ripple"]
    assert "3RAoRRek6o4j" in urls["coinbase"]


def test_ripple_press_release_urls_are_canonical_not_date_prefixed():
    data = load()
    urls = data["ripple_product_evidence"]["sources"]
    assert "https://ripple.com/ripple-press/ripple-receives-final-occ-approval-to-establish-national-trust-bank/" in urls
    assert "https://ripple.com/ripple-press/ripple-and-coinbase-partner-to-expand-access-to-rlusd/" in urls
    assert "https://ripple.com/ripple-press/ripple-expands-collaboration-with-bny-across-custody-and-tokenized-trade-finance/" in urls
    assert all("/ripple-press/2026/" not in url for url in urls)


def test_coinbase_rlusd_networks_and_global_exchange_collateral_are_separate():
    data = load()
    evidence = data["ripple_product_evidence"]["coinbase_distribution"]
    assert "XRPL, Base and Ethereum" in evidence
    assert "Coinbase Global Exchange" in evidence
    assert "future" in evidence.lower()


def test_rlusd_collateral_is_not_mislabeled_as_xrp_collateral():
    data = load()
    evidence = data["ripple_product_evidence"]["rlusd_collateral_use"]
    assert "RLUSD" in evidence
    assert "actual" in evidence.lower()
    boundary = data["strategic_graph"]["demand_boundary"]
    assert "proves incremental XRP spot purchases" in boundary


def test_c2fo_is_announcement_waitlist_not_verified_live_throughput():
    data = load()
    evidence = data["ripple_product_evidence"]["c2fo"]
    assert "waitlist" in evidence.lower()
    assert "not evidence of live transaction throughput" in evidence.lower()


def test_circle_sbi_jv_is_formed_50_50_and_operating_results_are_not_inferred():
    data = load()
    item = data["sbi_group_network"]["circle_jv"]
    assert "50:50" in item
    assert "2025-08-22" in item
    assert "no significant operating results" in item
    assert "$25M each" in item


def test_sbi_ai_and_rlusd_sources_are_not_misattributed():
    data = load()
    sources = data["sbi_group_network"]["sources"]
    assert "https://www.sbigroup.co.jp/news/2025/0501_15410.html" in sources
    assert "https://www.sbigroup.co.jp/news/2026/0602_16373.html" in sources
    assert "https://www.sbivc.co.jp/newsview/bsqs09vn_yzv" in sources
    assert "https://www.sbigroup.co.jp/news/2026/0602_16012.html" not in sources


def test_circle_and_ripple_are_not_claimed_as_direct_commercial_partners():
    data = load()
    assert "No direct Circle-Ripple commercial partnership" in data["strategic_graph"]["circle_ripple_direct_relationship"]


def test_charter_and_stablecoin_evidence_does_not_issue_an_xrp_forecast():
    data = load()
    assert data["safety"]["forecast_status"] == "NOT_ISSUED"
    assert data["safety"]["model_admission"] is False
