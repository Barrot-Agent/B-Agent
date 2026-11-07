from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T193840Z-sbi-circle-coinbase-ripple-institutional-relationship-graph.json"
)


def load_graph() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_primary_source_excerpt_hashes_match_the_append_only_correction() -> None:
    graph = load_graph()
    correction_path = (
        REPO_ROOT
        / "research"
        / "xrp_intelligence"
        / "20261107T194149Z-sbi-circle-ripple-source-excerpt-hash-correction.json"
    )
    correction = json.loads(correction_path.read_text(encoding="utf-8"))
    corrected = {item["source_id"]: item for item in correction["corrections"]}
    assert len(graph["source_receipts"]) >= 13
    assert len(corrected) == len(graph["source_receipts"])
    for receipt in graph["source_receipts"]:
        item = corrected[receipt["source_id"]]
        assert item["original_sha256"] == receipt["captured_excerpt_sha256"]
        assert hashlib.sha256(
            receipt["captured_excerpt_text"].encode("utf-8")
        ).hexdigest() == item["corrected_sha256"]


def test_sbi_circle_and_startale_equity_relationships_are_separate() -> None:
    edges = load_graph()["relationship_edges"]
    circle = next(x for x in edges if x["from"] == "SBI Holdings" and x["to"] == "Circle Internet Group")
    startale = next(x for x in edges if x["from"] == "SBI Group" and x["to"] == "Startale Group")
    assert circle["total_group_investment_usd_m"] == 50
    assert circle["amount_usd_m"] == 25
    assert circle["related_investor_amount_usd_m"] == 25
    assert startale["amount_usd_m"] == 50
    assert startale["equity_method_affiliate_expected"] is True


def test_sbi_arc_presale_amount_is_not_invented() -> None:
    edge = next(x for x in load_graph()["relationship_edges"] if x["to"] == "Circle Arc / ARC token")
    assert edge["relationship"] == "ARC token presale participation"
    assert edge["amount_usd"] is None
    assert edge["allocation_disclosed"] is False


def test_sctc_remains_rlusd_issuer_not_ripple_national_trust_bank() -> None:
    edges = load_graph()["relationship_edges"]
    rntb = next(x for x in edges if x["from"] == "Ripple National Trust Bank")
    assert rntb["issuer_of_rlusd"] is False
    assert rntb["rlusd_issuer"] == "Standard Custody & Trust Company LLC"
    distinctions = " ".join(load_graph()["key_distinctions"])
    assert "SCTC, not Ripple National Trust Bank" in distinctions


def test_coinbase_ripple_rlusd_collateral_status_is_not_misreported() -> None:
    edge = next(x for x in load_graph()["relationship_edges"] if x["from"] == "Ripple" and x["to"] == "Coinbase")
    assert "XRPL" in edge["networks"]
    assert "Base" in edge["networks"]
    assert "described as future at October 28 launch" in " ".join(load_graph()["key_distinctions"])


def test_standard_chartered_planned_collateral_is_conditioned() -> None:
    edge = next(x for x in load_graph()["relationship_edges"] if x["relationship"] == "planned collateral integration")
    assert edge["directness"] == "planned"
    assert len(edge["conditions"]) >= 5


def test_bny_xrp_custody_capability_does_not_imply_disclosed_balances() -> None:
    edge = next(x for x in load_graph()["relationship_edges"] if x["from"] == "BNY")
    assert edge["to"] == "XRP and RLUSD"
    assert edge["balances_disclosed"] is False


def test_smfg_five_percent_is_in_sbi_startale_marketing() -> None:
    edge = next(x for x in load_graph()["relationship_edges"] if x["from"] == "SMFG")
    assert edge["to"] == "SBI Startale Marketing"
    assert edge["stake_pct"] == 5
    assert edge["investee_is_sbi_holdings"] is False


def test_sbi_visa_rewards_are_not_mislabeled_as_payment_settlement() -> None:
    edge = next(x for x in load_graph()["relationship_edges"] if x["from"] == "SBI VC Trade, Aplus and Visa")
    assert edge["relationship"] == "credit-card reward points converted to crypto"
    assert "not Visa payment settlement" in edge["xrp_linkage"]


def test_competing_hypotheses_keep_counterevidence_and_disable_forecasts() -> None:
    graph = load_graph()
    hypotheses = graph["competing_hypotheses"]
    assert len(hypotheses) >= 3
    assert all(item["support"] and item["counterevidence"] for item in hypotheses)
    assert graph["model_admission"]["feature_admission"] is False
    assert graph["forecast_status"] == "NOT_ISSUED"
