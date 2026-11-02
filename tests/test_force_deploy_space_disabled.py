from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_force_deploy_space_is_inert_and_cannot_force_push():
    path = ROOT / ".github" / "workflows" / "force-deploy-space.yml"
    text = path.read_text(encoding="utf-8")
    assert "permissions: {}" in text
    assert "if: false" in text
    assert "workflow_dispatch" in text
    assert "HF_TOKEN" not in text
    assert "git push -f" not in text
    assert "huggingface.co/spaces" not in text
    assert "actions/checkout" not in text
