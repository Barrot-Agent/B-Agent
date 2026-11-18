#!/usr/bin/env python3
"""Guardrail proof and first live pulls.

    python3 NETWORK_TEST.py --tests     five guard tests, no request leaves
    python3 NETWORK_TEST.py --pulls     three live pulls through the guard
    python3 NETWORK_TEST.py --all

The credential test is expected to ABORT in this environment: a
credential-shaped variable is present. That is the guard working. Live pulls
must therefore run in a child process with that variable unset:

    env -u LUNAROUTE_API_KEY python3 NETWORK_TEST.py --pulls
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from barrot_agent.network_guard import (  # noqa: E402
    ALLOWED_DOMAINS,
    guarded_get,
    is_allowed,
    key_values_look_live,
)

RESULTS: list[tuple[str, str, str]] = []


def record(name: str, verdict: str, detail: str) -> None:
    RESULTS.append((name, verdict, detail))
    print(f"  [{verdict}] {name}: {detail}")


# --- guard tests --------------------------------------------------------------


def test_allowed_kaggle() -> None:
    url = "https://www.kaggle.com/models"
    record("allowed / kaggle", "PASS" if is_allowed(url) else "FAIL", url)


def test_allowed_coingecko() -> None:
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ripple&vs_currencies=usd"
    record("allowed / coingecko", "PASS" if is_allowed(url) else "FAIL", url)


def test_blocked_exchange() -> None:
    for url in (
        "https://api.binance.com/api/v3/ticker/price?symbol=XRPUSDT",
        "https://kraken.com",
        "https://kaggle.com.evil.example/x",
        "http://api.coingecko.com/api/v3/ping",
    ):
        if is_allowed(url):
            record("blocked / non-allowlisted", "FAIL", f"{url} was allowed")
            return
    record("blocked / non-allowlisted", "PASS",
           "binance, kraken, lookalike host, plain http all denied")


def test_blocked_post() -> None:
    result = guarded_get(
        "https://api.coingecko.com/api/v3/ping", purpose="post test", method="POST"
    )
    ok = result["blocked"] and "read-only" in result["reason"]
    record("blocked / POST", "PASS" if ok else "FAIL", result["reason"])


def test_live_key_abort() -> None:
    live = key_values_look_live()
    result = guarded_get("https://api.coingecko.com/api/v3/ping", purpose="key test")
    if live:
        ok = result["blocked"] and result["reason"] == "LIVE KEY DETECTED — ABORT"
        detail = f"detected {', '.join(live)} (names only); guard refused"
        record("abort / live key", "PASS" if ok else "FAIL", detail)
    else:
        record("abort / live key", "SKIP", "no credential-shaped variable present; cannot prove")


# --- live pulls ---------------------------------------------------------------


def pull_kaggle_models() -> None:
    # api.kaggle.com needs authentication for most endpoints. Try the public
    # listing first and report the real status rather than assuming.
    for url in (
        "https://www.kaggle.com/api/v1/models/list?pageSize=5",
        "https://www.kaggle.com/models",
    ):
        result = guarded_get(url, purpose="kaggle models list")
        if result["blocked"]:
            record("pull / kaggle", "BLOCKED", result["reason"])
            return
        if result["ok"]:
            body = result["body"]
            names = []
            try:
                payload = json.loads(body)
                for item in payload.get("models", [])[:5]:
                    names.append(str(item.get("title") or item.get("ref") or "?"))
            except json.JSONDecodeError:
                for token in ("Qwen3", "Gemma", "TabPFN", "Llama", "Mistral", "DeepSeek"):
                    if token.lower() in body.lower():
                        names.append(token)
            detail = f"{result['status']} {result['bytes_read']}B"
            if names:
                detail += " | " + ", ".join(dict.fromkeys(names))
            record("pull / kaggle", "PASS", detail)
            return
        record("pull / kaggle", "FAIL", f"{result['status']} {result['reason']} ({url})")
        time.sleep(2.1)


def pull_coingecko_prices() -> None:
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        "?ids=ripple,bitcoin,ethereum,solana,stellar,tether"
        "&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true"
    )
    result = guarded_get(url, purpose="coingecko spot prices")
    if not result["ok"]:
        record("pull / coingecko", "BLOCKED" if result["blocked"] else "FAIL",
               result["reason"] or f"HTTP {result['status']}")
        return
    try:
        payload = json.loads(result["body"])
    except json.JSONDecodeError:
        record("pull / coingecko", "FAIL", "response was not JSON")
        return
    out = []
    for key, quote in payload.items():
        price = quote.get("usd")
        change = quote.get("usd_24h_change")
        out.append(f"{key}={price} ({change:+.2f}%)" if change is not None else f"{key}={price}")
    record("pull / coingecko", "PASS", "; ".join(out))
    out_path = ROOT / "market" / "live-coingecko.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def pull_chromium_commits() -> None:
    url = "https://chromium.googlesource.com/chromium/src/+log/main?format=JSON&n=5"
    result = guarded_get(url, purpose="chromium src log")
    if not result["ok"]:
        record("pull / chromium", "BLOCKED" if result["blocked"] else "FAIL",
               result["reason"] or f"HTTP {result['status']}")
        return
    body = result["body"]
    if body.startswith(")]}'"):
        body = body.split("\n", 1)[1] if "\n" in body else body[4:]
    try:
        payload = json.loads(body)
        commits = payload.get("log", [])
        lines = [f"{c['commit'][:12]} {c['message'].splitlines()[0][:60]}" for c in commits]
        record("pull / chromium", "PASS", f"{len(commits)} commits | " + " || ".join(lines[:3]))
        out_path = ROOT / "market" / "live-chromium-log.json"
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except (json.JSONDecodeError, KeyError) as exc:
        record("pull / chromium", "FAIL", f"unexpected payload: {type(exc).__name__}")


def main(argv: list[str]) -> int:
    do_tests = "--tests" in argv or "--all" in argv or len(argv) == 0
    do_pulls = "--pulls" in argv or "--all" in argv

    print(f"allowlist: {', '.join(ALLOWED_DOMAINS)}")
    print("mode: read-only, GET only, 1 req / 2s, 60 / hour, 10s timeout")
    print()

    if do_tests:
        print("guard tests")
        test_allowed_kaggle()
        test_allowed_coingecko()
        test_blocked_exchange()
        test_blocked_post()
        test_live_key_abort()
        print()

    if do_pulls:
        live = key_values_look_live()
        if live:
            print("LIVE KEY DETECTED — ABORT")
            print(f"  {', '.join(live)} present in this process.")
            print("  Re-run with: env -u " + " -u ".join(live) + " python3 NETWORK_TEST.py --pulls")
            return 2
        print("live pulls")
        pull_kaggle_models()
        time.sleep(2.1)
        pull_coingecko_prices()
        time.sleep(2.1)
        pull_chromium_commits()
        print()

    failed = [row for row in RESULTS if row[1] == "FAIL"]
    aborted = [row for row in RESULTS if row[1] in ("ABORT", "BLOCKED")]
    print(f"{len(RESULTS)} checks, {len(failed)} failed, {len(aborted)} blocked/aborted")
    print("log: NETWORK_LOG.md")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
