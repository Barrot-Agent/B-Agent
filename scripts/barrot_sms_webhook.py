#!/usr/bin/env python3
"""Small, dependency-free Twilio webhook adapter for Barrot.

The adapter only accepts authenticated, allow-listed inbound messages and
delegates reasoning to the existing ping-pong chain. It does not persist phone
numbers or message bodies.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import html
import logging
import os
import time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable, Mapping
from urllib.parse import parse_qs, urlencode

LOGGER = logging.getLogger("barrot.sms")
MAX_REPLY_CHARS = 1400


def validate_twilio_signature(
    url: str, params: Mapping[str, str], signature: str, auth_token: str
) -> bool:
    """Validate Twilio's X-Twilio-Signature without logging request data."""
    if not url or not signature or not auth_token:
        return False
    payload = url + "".join(
        f"{key}{params[key]}" for key in sorted(params)
    )
    digest = hmac.new(
        auth_token.encode("utf-8"), payload.encode("utf-8"), hashlib.sha1
    ).digest()
    expected = base64.b64encode(digest).decode("ascii")
    return hmac.compare_digest(expected, signature)


class ReplayGuard:
    """Bounded replay and per-sender rate protection."""

    def __init__(self, max_messages: int = 2048, window_seconds: int = 60, limit: int = 5):
        self._seen: set[str] = set()
        self._order: deque[str] = deque()
        self._timestamps: defaultdict[str, deque[float]] = defaultdict(deque)
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self.limit = limit

    def accept(self, message_id: str, sender: str, now: float | None = None) -> bool:
        if not message_id or not sender or message_id in self._seen:
            return False
        current = time.time() if now is None else now
        timestamps = self._timestamps[sender]
        while timestamps and current - timestamps[0] >= self.window_seconds:
            timestamps.popleft()
        if len(timestamps) >= self.limit:
            return False
        timestamps.append(current)
        self._seen.add(message_id)
        self._order.append(message_id)
        while len(self._order) > self.max_messages:
            self._seen.discard(self._order.popleft())
        return True


def twiml_message(text: str) -> bytes:
    safe = html.escape((text or "").strip()[:MAX_REPLY_CHARS], quote=False)
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{safe}</Message></Response>'.encode(
        "utf-8"
    )


class BarrotSmsAdapter:
    """Authenticate and route Twilio form posts into the existing Barrot chain."""

    def __init__(
        self,
        chain: Callable[[str], str],
        *,
        auth_token: str,
        allowed_from: set[str],
        replay_guard: ReplayGuard | None = None,
    ):
        self.chain = chain
        self.auth_token = auth_token
        self.allowed_from = {value.strip() for value in allowed_from if value.strip()}
        self.replay_guard = replay_guard or ReplayGuard()

    def handle(self, *, url: str, params: Mapping[str, str], signature: str) -> tuple[int, bytes]:
        if not validate_twilio_signature(url, params, signature, self.auth_token):
            return 403, twiml_message("Unauthorized.")
        sender = params.get("From", "")
        message_id = params.get("MessageSid", "")
        if sender not in self.allowed_from or not self.replay_guard.accept(message_id, sender):
            return 403, twiml_message("Message not authorized.")
        body = params.get("Body", "").strip()
        if not body:
            return 400, twiml_message("Please send a text message.")
        try:
            reply = self.chain(body).strip()
        except Exception:
            LOGGER.exception("Barrot SMS chain failed")
            return 200, twiml_message("Barrot is temporarily unavailable. Please try again.")
        return 200, twiml_message(reply or "Barrot did not produce a response.")


def default_chain(task: str) -> str:
    from pingpong import run_chain

    final, _stages = run_chain(task, include_gpt=True, include_ibm_bob=False)
    return final


def build_adapter_from_environment(chain: Callable[[str], str] = default_chain) -> BarrotSmsAdapter:
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    allowed = {
        value.strip()
        for value in os.environ.get("BARROT_SMS_ALLOWED_FROM", "").split(",")
        if value.strip()
    }
    if not auth_token or not allowed:
        raise RuntimeError("TWILIO_AUTH_TOKEN and BARROT_SMS_ALLOWED_FROM are required")
    return BarrotSmsAdapter(chain, auth_token=auth_token, allowed_from=allowed)


class SmsRequestHandler(BaseHTTPRequestHandler):
    adapter: BarrotSmsAdapter

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        params = {
            key: values[0]
            for key, values in parse_qs(raw.decode("utf-8"), keep_blank_values=True).items()
        }
        url = os.environ.get("BARROT_SMS_PUBLIC_URL", "")
        status, response = self.adapter.handle(
            url=url,
            params=params,
            signature=self.headers.get("X-Twilio-Signature", ""),
        )
        self.send_response(status)
        self.send_header("Content-Type", "application/xml; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, _format: str, *_args: object) -> None:
        LOGGER.info("SMS webhook request received")


def main() -> None:
    adapter = build_adapter_from_environment()
    SmsRequestHandler.adapter = adapter
    server = HTTPServer(
        (os.environ.get("BARROT_SMS_BIND", "127.0.0.1"), int(os.environ.get("BARROT_SMS_PORT", "8080"))),
        SmsRequestHandler,
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
