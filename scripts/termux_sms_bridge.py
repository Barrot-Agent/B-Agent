#!/usr/bin/env python3
"""Forward Android SMS messages to Barrot and send replies through Termux:API.

Run this on the Android phone in Termux. Secrets are supplied only through the
environment and never written to the repository.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import subprocess
import time
import urllib.request


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def sign(message_id: str, sender: str, body: str, secret: str) -> str:
    payload = f"{message_id}:{sender}:{body}"
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def list_messages() -> list[dict]:
    output = subprocess.check_output(["termux-sms-list", "-l", "20"], text=True)
    messages = json.loads(output)
    return messages if isinstance(messages, list) else []


def send_sms(number: str, body: str) -> None:
    subprocess.run(["termux-sms-send", "-n", number, "-b", body], check=True)


def forward(message: dict, endpoint: str, secret: str) -> str:
    message_id = str(message.get("_id") or message.get("id") or "")
    sender = str(message.get("sender") or message.get("number") or "")
    body = str(message.get("body") or "")
    if not message_id or not sender or not body:
        raise ValueError("SMS record is missing id, sender, or body")
    payload = json.dumps({"id": message_id, "from": sender, "body": body}).encode()
    request = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Barrot-Signature": sign(message_id, sender, body, secret),
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def run_once() -> None:
    endpoint = _required("BARROT_SMS_ENDPOINT")
    secret = _required("BARROT_SMS_SHARED_SECRET")
    destination = _required("BARROT_SMS_REPLY_TO")
    state_path = os.environ.get("BARROT_SMS_STATE", os.path.expanduser("~/.barrot_sms_state"))
    last_id = ""
    if os.path.exists(state_path):
        last_id = open(state_path, encoding="utf-8").read().strip()
    for message in reversed(list_messages()):
        message_id = str(message.get("_id") or message.get("id") or "")
        if not message_id or message_id == last_id:
            continue
        reply = forward(message, endpoint, secret).strip()
        if reply:
            send_sms(destination, reply)
        with open(state_path, "w", encoding="utf-8") as state:
            state.write(message_id)


def main() -> None:
    interval = int(os.environ.get("BARROT_SMS_POLL_SECONDS", "15"))
    while True:
        try:
            run_once()
        except Exception as exc:
            print(f"SMS bridge unavailable: {type(exc).__name__}", flush=True)
        time.sleep(interval)


if __name__ == "__main__":
    main()
