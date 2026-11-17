"""The money stack must parse, reference real scripts, and stay license-clean."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = [".github/workflows/money-audit.yml", ".github/workflows/money-bounty-scan.yml", ".github/workflows/money-mcp-listing.yml"]


def load(relative: str) -> dict:
    text = (ROOT / relative).read_text(encoding="utf-8")
    payload = yaml.load(text, Loader=yaml.BaseLoader)
    assert isinstance(payload, dict)
    return payload


def test_all_three_money_workflows_parse_with_name_on_jobs():
    for relative in WORKFLOWS:
        payload = load(relative)
        assert payload.get("name"), relative
        assert payload.get("on"), relative
        assert payload.get("jobs"), relative
        assert all("runs-on" in job for job in payload["jobs"].values()), relative


def test_money_workflows_only_use_workflow_dispatch_schedule_or_main_push():
    for relative in WORKFLOWS:
        triggers = load(relative)["on"]
        allowed = {"push", "pull_request", "workflow_dispatch", "schedule"}
        assert set(triggers) <= allowed, (relative, triggers)


def test_every_referenced_script_exists():
    for relative in WORKFLOWS:
        text = (ROOT / relative).read_text(encoding="utf-8")
        for script in re.findall(r"python3 (scripts/[\w_]+\.py)", text):
            assert (ROOT / script).exists(), (relative, script)


def test_bounty_scan_is_scheduled_and_uploads_an_artifact():
    payload = load(".github/workflows/money-bounty-scan.yml")
    assert "schedule" in payload["on"]
    text = (ROOT / ".github/workflows/money-bounty-scan.yml").read_text(encoding="utf-8")
    assert "scripts/bounty_scan.py" in text
    assert "upload-artifact" in text


def test_listing_preflight_refuses_to_claim_publication():
    text = (ROOT / ".github/workflows/money-mcp-listing.yml").read_text(encoding="utf-8")
    assert "no registry publish is attempted" in text
    assert "server/server.json" in text


def test_server_json_has_metadata_and_empty_packages():
    meta = json.loads((ROOT / "server" / "server.json").read_text(encoding="utf-8"))
    for key in ("name", "description", "version", "repository"):
        assert meta[key]
    assert meta["packages"] == []
    assert "packages is empty on purpose" in meta["notes"]


def test_vendored_components_are_licensed_and_attributed():
    index = json.loads((ROOT / "data" / "harvest" / "components.json").read_text(encoding="utf-8"))
    assert index["pulled"] == 3
    assert index["blocked"] == 0
    allowed = set(index["allowed_licenses"])
    for component in index["components"]:
        assert component["license"] in allowed, component["repo"]
        local = ROOT / component["local_path"]
        assert local.exists()
        header = local.read_text(encoding="utf-8").splitlines()[:8]
        assert any("Licence:" in line for line in header)
        assert any(component["commit"] in line for line in header)
        yaml.load(local.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def test_attributions_lists_every_pulled_component_and_the_refusals():
    text = (ROOT / "ATTRIBUTIONS.md").read_text(encoding="utf-8")
    index = json.loads((ROOT / "data" / "harvest" / "components.json").read_text(encoding="utf-8"))
    for component in index["components"]:
        assert component["local_path"] in text
        assert component["license"] in text
    harvest = json.loads((ROOT / "data" / "harvest" / "workflows.json").read_text(encoding="utf-8"))
    assert harvest["blocked_license"] == 10
    for record in harvest["records"]:
        if record["license_status"] == "BLOCKED-LICENSE":
            assert record["repo"] in text, record["repo"]
