from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_run174_mainline_successor_preserves_mainline_and_xrp_mission() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Barrot in OpenCode" in readme
    assert (ROOT / ".github" / "FUNDING.yml").is_file()
    assert (ROOT / "MEMORY.md").is_file()

    mission = json.loads(
        (ROOT / "barrot_agent" / "data" / "missions" / "primary_mission.json").read_text(
            encoding="utf-8"
        )
    )
    assert mission["mission_id"] == "xrp_intelligence_prediction_engine"
    assert mission["priority"] == 1
    assert mission["status"] == "active"

    audit = json.loads(
        (
            ROOT
            / "research"
            / "xrp_intelligence"
            / "20261115T210147Z-run174-mainline-successor-recovery-audit.json"
        ).read_text(encoding="utf-8")
    )
    assert audit["run_id"] == "Run174"
    assert audit["repository"]["current_main_sha"] == "5b2a9c46eb878250dfec99190e294909cd5835bf"
    assert audit["repository"]["successor_branch"] == "integration/xrp-v3-mainline-successor-20261115T2101Z"
    assert audit["prediction_engine"]["forecast_status"] == "NOT_ISSUED"
    assert audit["prediction_engine"]["accuracy_status"] == "NOT_EVALUATED"

    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF_LATEST.md").read_text(encoding="utf-8")
    assert "Run174" in handoff
    assert "5b2a9c46eb878250dfec99190e294909cd5835bf" in handoff
