from barrot_agent.orchestration.action_executor import BarrotActionExecutor
from barrot_agent.orchestration.autonomous_actions import deliver_autonomous_bundle
from barrot_agent.orchestration.bundle_evidence import (
    content_sha256,
    file_sha256,
    verify_bundle_delivery,
)


def test_bundle_delivery_produces_matching_hash_evidence(tmp_path):
    executor = BarrotActionExecutor(workspace=tmp_path)

    target = tmp_path / "evidence_bundle.py"
    content = 'def probe():\n    return "EVIDENCE_OK"\n'

    result = deliver_autonomous_bundle(
        executor,
        path=str(target),
        content=content,
    )

    assert result.success is True

    evidence = verify_bundle_delivery(
        path=str(target),
        content=content,
    )

    assert evidence.verified is True
    assert evidence.content_hash.startswith("sha256:")
    assert evidence.content_hash == evidence.delivered_hash
    assert content_sha256(content) == file_sha256(target)


def test_bundle_delivery_evidence_detects_modified_file(tmp_path):
    target = tmp_path / "modified_bundle.py"
    content = 'def probe():\n    return "ORIGINAL"\n'

    target.write_text(
        'def probe():\n    return "MODIFIED"\n',
        encoding="utf-8",
    )

    evidence = verify_bundle_delivery(
        path=str(target),
        content=content,
    )

    assert evidence.verified is False
    assert evidence.content_hash != evidence.delivered_hash
    assert "hash" in evidence.reason.lower()


def test_bundle_delivery_evidence_detects_missing_file(tmp_path):
    target = tmp_path / "missing_bundle.py"
    content = "x = 1\n"

    evidence = verify_bundle_delivery(
        path=str(target),
        content=content,
    )

    assert evidence.verified is False
    assert evidence.delivered_hash == ""
    assert "does not exist" in evidence.reason.lower()
