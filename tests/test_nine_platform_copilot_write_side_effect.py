import json
from pathlib import Path


def test_nine_platform_map_records_copilot_branch_write_side_effect_and_remediation():
    root = Path(__file__).resolve().parents[1]
    path = root / "research" / "xrp_intelligence" / "20261105T072000Z-nine-platform-capability-authentication-map.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))

    assert artifact["platform_count"] == 9
    assert artifact["verified_live_platform_count"] == 1
    assert artifact["verified_live_platforms"] == ["ChatGPT current session"]

    copilot = next(item for item in artifact["platforms"] if item["name"] == "Copilot")
    assert "BRANCH_WRITE_SIDE_EFFECT" in copilot["connection_status"]
    assert any("test-only commit" in item for item in copilot["permissions"]["observed"])
    assert any("read-only" in item and "no edits" in item for item in copilot["permissions"]["observed"])
    assert "not a persistent Copilot connector" in copilot["data_flow"]

    assert artifact["safety"]["no_unapproved_external_mutation"] is False
    assert artifact["safety"]["unexpected_agent_branch_write_occurred"] is True
    assert artifact["safety"]["unexpected_agent_branch_write_scope"].startswith("One non-destructive test-only commit")

    findings = {item["id"]: item for item in artifact["agent_review_findings"]}
    assert findings["COPILOT-REDIRECT-01"]["severity"] == "blocking"
    assert findings["COPILOT-REDIRECT-01"]["remediation_commit"] == "a18484dbb6cc5924327335f43ef2195188a9f554"
    assert findings["COPILOT-RECEIPT-02"]["remediation_commit"] == "a18484dbb6cc5924327335f43ef2195188a9f554"
