from pathlib import Path


def test_barrot_sync_distinguishes_local_oauth_note_from_provider_status() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "BARROT_SYNC.md").read_text(encoding="utf-8")

    assert "Authentication/data flow NOT VERIFIED" in content
    assert "presence/validity in GitHub Secrets is NOT VERIFIED" in content
    assert "provider-side OAuth revocation is NOT VERIFIED" in content
    # This is a local CLI credential-file warning, not a provider-wide revocation claim.
    assert "Do NOT re-commit .config/gh/hosts.yml - OAuth REVOKED" in content
    assert "httpx" in content
    assert "sync skipped" in content
    assert "no sync commit was produced" in content
    assert "No automatic external sync or push without explicit approval" in content
