from pathlib import Path


def test_barrot_sync_does_not_claim_unverified_credentials_or_oauth_revocation() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "BARROT_SYNC.md").read_text(encoding="utf-8")

    assert "Authentication/data flow NOT VERIFIED" in content
    assert "presence/validity in GitHub Secrets is NOT VERIFIED" in content
    assert "provider-side OAuth revocation is NOT VERIFIED" in content
    assert "OAuth REVOKED" not in content
    assert "httpx" in content
    assert "sync skipped" in content
    assert "no sync commit was produced" in content
    assert "No automatic external sync or push without explicit approval" in content
