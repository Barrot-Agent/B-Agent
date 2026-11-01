import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_subscriber_page_fails_closed_without_server_side_entitlement():
    page = (ROOT / "web" / "signals.html").read_text(encoding="utf-8")
    lowered = page.lower()

    assert "subscriber delivery is temporarily unavailable" in lowered
    assert "server-side entitlement verification" in lowered
    assert "cannot securely verify paid subscriptions" in lowered
    assert "do not enter an email address" in lowered
    assert "<input" not in lowered
    assert "<script" not in lowered
    assert "fetch(" not in lowered
    assert "subscribers.json" not in lowered
    assert "latest_signal.json" not in lowered
    assert "crypto.subtle" not in lowered


def test_subscriber_sync_is_inert_and_has_no_private_data_access():
    workflow = (ROOT / ".github" / "workflows" / "subscriber_sync.yml").read_text(encoding="utf-8")
    lowered = workflow.lower()

    assert "workflow_dispatch:" in workflow
    assert "if: false" in workflow
    assert "permissions: {}" in workflow
    assert "schedule:" not in lowered
    assert "gumroad_access_token" not in lowered
    assert "api.gumroad.com" not in lowered
    assert "subscribers.json" not in lowered
    assert "git push" not in lowered
    assert "contents: write" not in lowered


def test_public_subscriber_identifier_file_remains_empty():
    data = json.loads((ROOT / "web" / "subscribers.json").read_text(encoding="utf-8"))
    assert data == {"emails": [], "count": 0}
