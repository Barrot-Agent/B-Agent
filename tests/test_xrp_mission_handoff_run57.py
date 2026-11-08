from pathlib import Path


HANDOFF = Path(__file__).resolve().parents[1] / "BARROT_XRP_MISSION_HANDOFF.md"


def test_run57_handoff_is_latest_and_binds_current_repository_heads():
    text = HANDOFF.read_text(encoding="utf-8")
    lines = text.splitlines()

    assert lines[0] == "# Current integrated Barrot handoff — 2026-11-08T14:05:10Z"
    assert lines[2] == "## Run 57 — current repository, Bybit/Kraken spot receipt, and integration status"
    latest = "\n".join(lines[:110])
    assert "9100dbacb5f9f1b973b053a65ef1e91e96b64f72" in latest
    assert "1b5858ee21980b05d9b8fccbd56808bd344cec99" in latest
    assert "8e017085825cc4dfcff68f17d6d66764f297f621" in latest
    assert "b27b0643dcd5e5087223ae9d89ec92ced6f7d4d3" in latest
    assert "42488534267" in latest
    assert "fc4c4f4a4618bc95067c623775ac614c411b8afe" in latest
    assert "1,201 passed, 8 subtests passed" in latest
    assert "58.86%" in latest
    assert "42487509336" in latest
    assert "42488386422" in latest
    assert "NOT_ISSUED" in latest
    assert "## Run 56 — current repository and exact-head verification" in text
