from pathlib import Path


HANDOFF = Path(__file__).resolve().parents[1] / "BARROT_XRP_MISSION_HANDOFF.md"


def test_run57_and_run58_handoff_history_is_preserved_under_run60():
    text = HANDOFF.read_text(encoding="utf-8")
    lines = text.splitlines()

    assert lines[0] == "# Current integrated Barrot handoff — 2026-11-08T17:01:21Z"
    assert lines[2] == "## Run 60 — current repository, exact-head verification and institutional-rails correction"
    latest = "\n".join(lines[:180])
    assert "9100dbacb5f9f1b973b053a65ef1e91e96b64f72" in latest
    assert "eeb4950d6cbda6a32870dfe074f671c4ccbc843e" in latest
    assert "674919abe365e915877e7f1f4211df347dfc39a9" in latest
    assert "1,208 passed, 8 subtests passed" in latest
    assert "2,472 passed, 8 subtests passed" in latest
    assert "58.98%" in latest
    assert "42494136348" in latest
    assert "42494763390" in latest
    assert "35 endpoint records, of which 33 are scheduled" in latest
    assert "Forecast status: NOT_ISSUED" in text
    assert "No merge was performed" in text

    assert "## Run 58 — current repository, endpoint inventory correction, exact-head verification and merge gate" in text
    assert "## Run 59 —" in text
    assert "## Run 57 — current repository, Bybit/Kraken spot receipt, and integration status" in text
    assert "1b5858ee21980b05d9b8fccbd56808bd344cec99" in text
    assert "8e017085825cc4dfcff68f17d6d66764f297f621" in text
    assert "b27b0643dcd5e5087223ae9d89ec92ced6f7d4d3" in text
    assert "## Run 56 — current repository and exact-head verification" in text
