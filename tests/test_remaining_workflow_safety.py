from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows"

def read(name):
    return (WF / name).read_text(encoding="utf-8")

def test_signal_accuracy_is_read_only_and_artifact_only():
    text = read("check-signal-accuracy.yml")
    assert "contents: read" in text
    assert "contents: write" not in text
    assert "persist-credentials: false" in text
    assert "actions/upload-artifact@v4" in text
    assert "git commit" not in text
    assert "git push" not in text

def test_subscriber_processing_is_manual_explicit_and_nonpersistent():
    text = read("subscriber_sync.yml")
    assert "workflow_dispatch:" in text
    assert "schedule:" not in text
    assert "confirm_private_data_processing" in text
    assert 'default: "NO"' in text
    assert "inputs.confirm_private_data_processing == 'YES'" in text
    assert "contents: read" in text
    assert "git commit" not in text
    assert "git push" not in text
    assert "rm -f web/subscribers.json" in text

def test_destructive_hugging_face_admin_is_disabled():
    text = read("barrot-hf-admin.yml")
    assert "permissions: {}" in text
    assert "HF_TOKEN" not in text
    assert "api/repos/delete" not in text
    assert "no external repository was changed" in text.lower()
