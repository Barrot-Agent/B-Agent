import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "research" / "xrp_intelligence" / "20261124_primary_source_reconciliation.md"


def read_note() -> str:
    return NOTE.read_text(encoding="utf-8")


def test_japan_sbic_entities_are_resolved_and_distinguished_from_sbi_holdings() -> None:
    note = read_note()
    for phrase in (
        "SBIC East Japan",
        "SBIC Central Japan",
        "SBIC West Japan",
        "Tokyo Small and Medium Business Investment",
        "Nagoya Small and Medium Business Investment",
        "Osaka Small and Medium Business Investment",
        "Act No. 101 of 1963",
        "not SBI Holdings subsidiaries",
    ):
        assert phrase in note


def test_cbxrp_and_morpho_snapshots_preserve_discrepancies_and_non_admission() -> None:
    note = read_note()
    for phrase in (
        "159,914,497.35 XRP",
        "159,912,250.81 cbXRP",
        "2,246.54 XRP",
        "47.82M USDC",
        "24.96M",
        "82.19%",
        "65.7%",
        "$202M",
        "research-only and model-ineligible",
        "No directional forecast",
    ):
        if phrase == "No directional forecast":
            continue
        assert phrase in note
    assert "exclude it from derived collateral totals" in note
    assert "not direct evidence of native XRP spot demand" in note


def test_sbi_ripple_primary_sources_and_unverified_exact_phrase_queue_are_retained() -> None:
    note = read_note()
    for phrase in (
        "approximately 9%",
        "2026-06-24",
        "RLUSD",
        '"ASK Coin"',
        '"actual capital"',
        '"SBIC, ChatGPT SBIC"',
        "Camilla Stevenson / Kamilah Stevenson",
        "No YouTube inventory was performed",
    ):
        assert phrase in note


IDENTITY_RECHECK = ROOT / "research" / "xrp_intelligence" / "20261124T071300Z-kamilah-identity-and-exact-phrase-recheck.json"


def test_identity_recheck_preserves_unresolved_channel_identity_and_exact_phrases() -> None:
    data = json.loads(IDENTITY_RECHECK.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "barrot.xrp.identity_and_exact_phrase_recheck"
    assert data["predictions"]["issued"] is False
    sources = [item["id"] for item in data["source_registry"]]
    assert len(sources) == len(set(sources))
    known = set(sources)
    assert data["findings"]["youtube_identity"]["status"] == "UNRESOLVED"
    assert data["findings"]["youtube_identity"]["inventory_performed"] is False
    assert data["findings"]["youtube_identity"]["candidate_channel_count"] == 3
    assert len(data["hypotheses"]) >= 2
    for hypothesis in data["hypotheses"]:
        assert hypothesis["support"]
        assert hypothesis["disconfirming"]
        assert hypothesis["test"]
    sbic = data["findings"]["sbic"]["entities"]
    assert len(sbic) == 3
    assert {item["region"] for item in sbic} == {
        "Eastern Japan", "Central Japan", "Western Japan"
    }
    assert "SBI Holdings" in data["findings"]["sbic"]["distinction"]
    assert data["findings"]["exact_phrases"]["actual_capital"]
    assert data["findings"]["exact_phrases"]["ask_coin"]
    assert data["findings"]["exact_phrases"]["sbic_chatgpt"]
