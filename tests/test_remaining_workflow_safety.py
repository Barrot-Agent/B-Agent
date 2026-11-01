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

def test_subscriber_processing_is_fully_disabled_pending_server_side_authorization():
    text = read("subscriber_sync.yml")
    assert "workflow_dispatch:" in text
    assert "permissions: {}" in text
    assert "if: false" in text
    assert "GUMROAD_ACCESS_TOKEN" not in text
    assert "secrets." not in text
    assert "api.gumroad.com" not in text
    assert "emails" not in text.lower()

def test_destructive_hugging_face_admin_is_disabled():
    text = read("barrot-hf-admin.yml")
    assert "permissions: {}" in text
    assert "HF_TOKEN" not in text
    assert "api/repos/delete" not in text
    assert "no external repository was changed" in text.lower()


def test_knowledge_signal_cycle_is_disabled_without_secrets_or_main_writes():
    text = read("knowledge-signal-cycle.yml")
    assert "permissions: {}" in text
    assert "if: ${{ false }}" in text
    assert "GROQ_API_KEY" not in text
    assert "contents: write" not in text
    assert "git push" not in text.lower()
    assert "KNOWLEDGE_CYCLE_NOT_PERFORMED" in text


def test_barrot_approval_workflow_cannot_self_attest_or_write_approval_labels():
    text = read("barrot-approve-pr.yml")
    assert "permissions: {}" in text
    assert "pull-requests: write" not in text
    assert "github.actor == github.repository_owner" not in text
    assert "gh api" not in text.lower()
    assert "gh pr" not in text.lower()
    assert "APPROVAL_NOT_PERFORMED" in text
