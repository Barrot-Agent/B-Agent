from pathlib import Path


def test_durable_xrp_handoff_contains_current_main_and_run12_depth_evidence():
    handoff = (
        Path(__file__).resolve().parents[1] / "BARROT_XRP_MISSION_HANDOFF.md"
    ).read_text(encoding="utf-8")

    assert "9100dbacb5f9f1b973b053a65ef1e91e96b64f72" in handoff
    assert "Fuelmaps' 18:00 six-venue spot-depth snapshot" in handoff
    assert (
        "research/xrp_intelligence/"
        "20261106T193345Z-xrp-binance-reserve-etf-flow-cross-source-reconciliation.json"
    ) in handoff
    assert "No directional forecast was issued" in handoff
    assert "Do not merge" in handoff
    assert "41799855489" in handoff
