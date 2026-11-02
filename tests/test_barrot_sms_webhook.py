import base64
import hashlib
import hmac
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "barrot_sms_webhook", ROOT / "scripts" / "barrot_sms_webhook.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def signed(url, params, token):
    payload = url + "".join(f"{key}{params[key]}" for key in sorted(params))
    digest = hmac.new(token.encode(), payload.encode(), hashlib.sha1).digest()
    return base64.b64encode(digest).decode()


def test_routes_authorized_sms_to_existing_chain():
    calls = []
    adapter = MODULE.BarrotSmsAdapter(
        lambda text: calls.append(text) or "Hello <there>",
        auth_token="secret",
        allowed_from={"+15550001111"},
    )
    params = {"From": "+15550001111", "MessageSid": "SM1", "Body": "Hi Barrot"}
    status, body = adapter.handle(
        url="https://example.test/sms", params=params, signature=signed("https://example.test/sms", params, "secret")
    )
    assert status == 200
    assert calls == ["Hi Barrot"]
    assert b"Hello &lt;there&gt;" in body


def test_rejects_bad_signature_and_sender():
    adapter = MODULE.BarrotSmsAdapter(lambda _: "never", auth_token="secret", allowed_from={"+15550001111"})
    params = {"From": "+15550009999", "MessageSid": "SM2", "Body": "Hi"}
    status, body = adapter.handle(url="https://example.test/sms", params=params, signature="bad")
    assert status == 403
    assert b"Unauthorized" in body


def test_replay_and_rate_limit_are_blocked():
    guard = MODULE.ReplayGuard(window_seconds=60, limit=1)
    assert guard.accept("SM1", "+15550001111", now=100)
    assert not guard.accept("SM1", "+15550001111", now=100)
    assert not guard.accept("SM2", "+15550001111", now=101)
    assert guard.accept("SM2", "+15550001111", now=161)


def test_chain_failure_returns_safe_reply():
    def fail(_):
        raise RuntimeError("provider secret or response leaked")

    adapter = MODULE.BarrotSmsAdapter(fail, auth_token="secret", allowed_from={"+15550001111"})
    params = {"From": "+15550001111", "MessageSid": "SM3", "Body": "Hi"}
    status, body = adapter.handle(
        url="https://example.test/sms", params=params, signature=signed("https://example.test/sms", params, "secret")
    )
    assert status == 200
    assert b"temporarily unavailable" in body
    assert b"provider secret" not in body


def test_environment_requires_credentials(monkeypatch):
    monkeypatch.delenv("TWILIO_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("BARROT_SMS_ALLOWED_FROM", raising=False)
    with pytest.raises(RuntimeError):
        MODULE.build_adapter_from_environment(lambda _: "ok")
