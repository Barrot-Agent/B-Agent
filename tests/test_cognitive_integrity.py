from pathlib import Path

from barrot_agent.evolution.cognitive_integrity import CognitiveIntegrityLoop


def test_integrity_loop_records_outcome(tmp_path, monkeypatch):
    import barrot_agent.evolution.cognitive_integrity as module

    monkeypatch.setattr(module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(module, "LEDGER_FILE", tmp_path / "outcomes.json")

    loop = CognitiveIntegrityLoop()
    record = loop.record_outcome(
        "test",
        {"result": "verified"},
        sources=["internal_test"],
        confidence=0.9,
    )

    assert record["operation"] == "test"
    assert loop.evaluate_integrity()["records"] == 1


def test_merge_queue_workflow_is_read_only_inventory():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github" / "workflows" / "merge-queue.yml").read_text(encoding="utf-8")
    lowered = workflow.lower()

    assert "workflow_dispatch:" in workflow
    assert "contents: read" in workflow
    assert "pull-requests: read" in workflow
    assert "checks: read" in workflow
    assert "statuses: read" in workflow

    forbidden = (
        "contents: write",
        "pull-requests: write",
        "gh pr merge",
        "gh pr comment",
        "update-branch",
        "--delete-branch",
        "--method put",
        "--method post",
        "--method delete",
        "git push",
        "git commit",
        "secrets.gh_pat",
        "dry_run",
        "mode=all",
    )
    for token in forbidden:
        assert token not in lowered

    assert "gh api --paginate" in workflow
    assert "pulls?state=open" in workflow
    assert "no branch updates" in lowered
