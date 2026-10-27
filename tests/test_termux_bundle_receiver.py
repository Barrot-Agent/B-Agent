from __future__ import annotations

import base64
import hashlib
import json

import pytest
from scripts import termux_bundle_receiver as receiver

COMMIT = "a" * 40
BUNDLE_ID = "probe-20261027"
URL = f"https://raw.githubusercontent.com/Barrot-Agent/B-Agent/{COMMIT}/data/termux_bundles/{BUNDLE_ID}.json"
PAYLOAD = b'{"kind":"barrot-termux-self-drop-probe","execute":false}\n'


class FakeResponse:
    def __init__(self, body: bytes, url: str = URL):
        self.body, self.url = body, url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size=-1):
        return self.body[:size] if size >= 0 else self.body

    def geturl(self):
        return self.url


def make_manifest(**overrides):
    value = {
        "schema_version": 1,
        "bundle_id": BUNDLE_ID,
        "filename": "barrot-self-drop-probe.json",
        "content_base64": base64.b64encode(PAYLOAD).decode("ascii"),
        "sha256": hashlib.sha256(PAYLOAD).hexdigest(),
        "created_at": "2026-10-27T00:00:00Z",
    }
    value.update(overrides)
    return json.dumps(value).encode("utf-8")


def patch_fetch(monkeypatch, body: bytes, final_url: str = URL):
    def fake_urlopen(request, timeout=20):
        assert timeout == 20
        return FakeResponse(body, final_url)
    monkeypatch.setattr(receiver, "urlopen", fake_urlopen)


def receive(tmp_path):
    home = tmp_path / "home"
    return receiver.receive_bundle(
        manifest_url=URL,
        expected_sha256=hashlib.sha256(PAYLOAD).hexdigest(),
        destination=home / "barrot" / "inbox",
        home_dir=home,
    )


def test_receives_hash_verified_data_only_bundle(monkeypatch, tmp_path):
    patch_fetch(monkeypatch, make_manifest())
    result = receive(tmp_path)
    target = tmp_path / "home/barrot/inbox/barrot-self-drop-probe.json"
    assert target.read_bytes() == PAYLOAD
    assert result["verified"] is True
    assert result["executed"] is False
    assert result["git_modified"] is False
    assert result["sha256"] == hashlib.sha256(PAYLOAD).hexdigest()


def test_rejects_non_allowlisted_url_before_network(monkeypatch, tmp_path):
    called = False

    def forbidden(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("network should not be used")

    monkeypatch.setattr(receiver, "urlopen", forbidden)
    with pytest.raises(receiver.BundleReceiveError):
        receiver.receive_bundle(
            manifest_url="https://example.com/manifest.json",
            expected_sha256=hashlib.sha256(PAYLOAD).hexdigest(),
            destination=tmp_path / "home/inbox",
            home_dir=tmp_path / "home",
        )
    assert not called


def test_rejects_redirect_to_untrusted_host(monkeypatch, tmp_path):
    patch_fetch(monkeypatch, make_manifest(), "https://evil.example/manifest.json")
    with pytest.raises(receiver.BundleReceiveError, match="raw.githubusercontent.com"):
        receive(tmp_path)


def test_rejects_manifest_hash_mismatch(monkeypatch, tmp_path):
    patch_fetch(monkeypatch, make_manifest(sha256="0" * 64))
    with pytest.raises(receiver.BundleReceiveError, match="does not match the manifest"):
        receive(tmp_path)


def test_requires_independent_expected_hash(monkeypatch, tmp_path):
    patch_fetch(monkeypatch, make_manifest())
    with pytest.raises(receiver.BundleReceiveError, match="expected hash"):
        receiver.receive_bundle(
            manifest_url=URL,
            expected_sha256="0" * 64,
            destination=tmp_path / "home/inbox",
            home_dir=tmp_path / "home",
        )


def test_rejects_path_traversal_filename(monkeypatch, tmp_path):
    patch_fetch(monkeypatch, make_manifest(filename="../outside.txt"))
    with pytest.raises(receiver.BundleReceiveError, match="simple basename"):
        receive(tmp_path)


def test_refuses_to_overwrite_existing_bundle(monkeypatch, tmp_path):
    patch_fetch(monkeypatch, make_manifest())
    receive(tmp_path)
    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        receive(tmp_path)


def test_rejects_destination_outside_home(monkeypatch, tmp_path):
    patch_fetch(monkeypatch, make_manifest())
    with pytest.raises(receiver.BundleReceiveError, match="subdirectory"):
        receiver.receive_bundle(
            manifest_url=URL,
            expected_sha256=hashlib.sha256(PAYLOAD).hexdigest(),
            destination=tmp_path / "outside",
            home_dir=tmp_path / "home",
        )


def test_rejects_invalid_base64(monkeypatch, tmp_path):
    patch_fetch(monkeypatch, make_manifest(content_base64="not base64!"))
    with pytest.raises(receiver.BundleReceiveError, match="base64 is invalid"):
        receive(tmp_path)
