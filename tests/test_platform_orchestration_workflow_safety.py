from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_pingpong_workflow_does_not_fake_external_collaboration_or_write_to_main():
    workflow = (
        REPO_ROOT / ".github" / "workflows" / "Barrot.Cognitive.PingPong.Engine.yml"
    ).read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "schedule:" not in workflow
    assert "push:" not in workflow
    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "issues: write" not in workflow
    assert "pull-requests: write" not in workflow
    assert "git push" not in workflow
    assert "git commit" not in workflow
    assert "Response quality: Optimal" not in workflow
    assert "Learning rate: Adaptive" not in workflow
    assert '"live_collaboration_verified": False' in workflow
    assert '"external_api_calls_made": False' in workflow
    assert "designed_only_not_live_verified_by_this_workflow" in workflow
