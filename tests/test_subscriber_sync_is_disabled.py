from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_subscriber_sync_is_inert_and_has_no_private_data_or_secrets():
    path = ROOT / ".github" / "workflows" / "subscriber_sync.yml"
    text = path.read_text(encoding="utf-8")
    workflow = yaml.safe_load(text)
    assert workflow["permissions"] == {}
    assert workflow["jobs"]["disabled"]["if"] is False
    assert "GUMROAD_ACCESS_TOKEN" not in text
    assert "secrets." not in text
    assert "api.gumroad.com" not in text
    assert "emails" not in text.lower()
