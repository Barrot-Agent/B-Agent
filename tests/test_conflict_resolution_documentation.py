from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_conflict_guides_do_not_recommend_automatic_resolution():
    paths = (
        "MERGE_CONFLICT_RESOLUTION_GUIDE.md",
        "docs/MERGE_CONFLICT_RESOLUTION_GUIDE.md",
        "docs/system.md",
    )
    for relative in paths:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "**Auto-Resolvable**: Yes" not in text
        assert '"auto_resolve_safe_conflicts": True' not in text
        assert "Accept both imports" not in text
        assert "human authorization" in text.lower()


def test_conflict_guides_do_not_publish_unverified_accept_both_rate():
    paths = (
        "MERGE_CONFLICT_RESOLUTION_GUIDE.md",
        "docs/MERGE_CONFLICT_RESOLUTION_GUIDE.md",
        "docs/system.md",
        "merge_conflict_knowledge_report.md",
        "memory-bundles/merge-conflict-resolutions.md",
    )
    for relative in paths:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "85% (depends on reviewer)" not in text
        assert "85% (expected)" not in text


def test_policy_document_preserves_advisory_only_execution_boundary():
    text = (ROOT / "docs/AUTONOMOUS_CONFLICT_RESOLUTION_POLICY.md").read_text(
        encoding="utf-8"
    ).lower()
    assert "auto_apply" in text and "always false" in text
    assert "resolver workflow remains quarantined" in text
    assert "explicit human authorization" in text
