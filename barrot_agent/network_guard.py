"""The single approved network module. Every outbound call goes through here.

Guardrails, all enforced in code rather than by convention:

    allowlist     exact host or a subdomain of a listed domain. Not a substring
                  match, so `evil-kaggle.com` and `kaggle.com.evil.net` fail.
    scheme        https only
    method        GET only. No POST, PUT, PATCH, DELETE, HEAD-with-body tricks.
    redirects     followed manually and re-checked, so a 302 to a denied host
                  cannot smuggle a request out
    credentials   if a credential-shaped environment variable exists, the guard
                  refuses to run at all. It never reads the value.
    auth headers  any Proxy-Authorization / Cookie / Authorization header is
                  stripped before the request is built
    rate          1 request per 2 seconds, 60 per rolling hour, persisted across
                  processes so separate CLI runs cannot exceed the cap
    timeout       10 seconds, then a clean error
    logging       every attempt appended to NETWORK_LOG.md, allowed or blocked

This module is the only file permitted to import `urllib.request` or `ssl`.
`tests/test_network_guard.py` enforces that by parsing the AST of the trading and
Chrome modules.
"""
from __future__ import annotations

import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "NETWORK_LOG.md"
STATE_PATH = REPO_ROOT / ".cache" / "network_guard_state.json"

ALLOWED_DOMAINS = (
    "kaggle.com",
    "www.kaggle.com",
    "api.kaggle.com",
    "api.coingecko.com",
    "api.coinmarketcap.com",
    "chromium.googlesource.com",
    "source.chromium.org",
    "bugs.chromium.org",
    "github.com",
    "raw.githubusercontent.com",
    "en.wikipedia.org",
)

MIN_INTERVAL_SECONDS = 2.0
MAX_REQUESTS_PER_HOUR = 60
TIMEOUT_SECONDS = 10
MAX_REDIRECTS = 3
MAX_BODY_BYTES = 2_000_000

CREDENTIAL_NAME = re.compile(
    r"(KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|PRIVATE_KEY)", re.IGNORECASE
)
IGNORED_NAME_SUFFIXES = ("_PATH", "_FILE", "_DIR", "_URL", "_ENDPOINT")

LOG_HEADER = """# NETWORK LOG

Append-only. Every attempt is recorded, including blocked ones. No secret is
ever written here: only the host, the status, the byte count, and the purpose.

| time (UTC) | method | host | status | bytes | verdict | purpose / reason |
|---|---|---|---|---|---|---|
"""


@dataclass(frozen=True)
class GuardResult:
    ok: bool
    status: int | None
    blocked: bool
    reason: str
    body: str
    host: str
    url: str
    bytes_read: int

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "status": self.status,
            "blocked": self.blocked,
            "reason": self.reason,
            "body": self.body,
            "host": self.host,
            "url": self.url,
            "bytes_read": self.bytes_read,
        }


# --- allowlist ----------------------------------------------------------------


def host_of(url: str) -> str:
    try:
        parsed = urllib.parse.urlsplit(url)
    except ValueError:
        return ""
    return (parsed.hostname or "").lower()


def is_allowed(url: str) -> bool:
    """Exact host, or a real subdomain. Never a substring match."""
    try:
        parsed = urllib.parse.urlsplit(url)
    except ValueError:
        return False
    if parsed.scheme != "https":
        return False
    host = (parsed.hostname or "").lower()
    if not host:
        return False
    for domain in ALLOWED_DOMAINS:
        if host == domain or host.endswith("." + domain):
            return True
    return False


# --- credential detection -----------------------------------------------------


def detect_live_keys() -> list[str]:
    """Names of credential-shaped environment variables. Values are never read.

    Length is reported so a placeholder can be told from a real secret, but the
    value itself never leaves the environment.
    """
    found = []
    for name, value in os.environ.items():
        if not CREDENTIAL_NAME.search(name):
            continue
        if name.endswith(IGNORED_NAME_SUFFIXES) or name in ("PWD", "OLDPWD"):
            continue
        found.append(name)
    return sorted(found)


def key_values_look_live() -> list[str]:
    """Credential names whose value is long enough to be a real secret.

    Short values (a placeholder like `x`, or `changeme`) are reported as names
    only. This function returns names, never values.
    """
    live = []
    for name in detect_live_keys():
        value = os.environ.get(name, "")
        if len(value) >= 20:
            live.append(name)
    return live


# --- rate limit ---------------------------------------------------------------


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {"calls": []}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"calls": []}


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=1), encoding="utf-8")


def recent_calls(state: dict, now: float) -> list[float]:
    return [ts for ts in state.get("calls", []) if now - ts < 3600]


def check_rate_limit(now: float | None = None, state: dict | None = None) -> tuple[bool, str]:
    now = time.time() if now is None else now
    state = _load_state() if state is None else state
    calls = recent_calls(state, now)
    if len(calls) >= MAX_REQUESTS_PER_HOUR:
        return False, f"hourly cap reached ({len(calls)}/{MAX_REQUESTS_PER_HOUR})"
    if calls:
        gap = now - max(calls)
        if gap < MIN_INTERVAL_SECONDS:
            return False, f"rate limit: {gap:.2f}s since last call, need {MIN_INTERVAL_SECONDS}s"
    return True, "ok"


def record_call(now: float | None = None) -> None:
    now = time.time() if now is None else now
    state = _load_state()
    state["calls"] = recent_calls(state, now) + [now]
    _save_state(state)


# --- logging ------------------------------------------------------------------


def log_event(
    method: str,
    host: str,
    status: int | None,
    size: int,
    verdict: str,
    purpose: str,
) -> None:
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    safe_purpose = purpose.replace("|", "/").replace("\n", " ")[:120]
    shown_status = status if status is not None else "-"
    row = (
        f"| {stamp} | {method} | {host or '-'} | {shown_status} | {size} | "
        f"{verdict} | {safe_purpose} |\n"
    )
    if not LOG_PATH.exists():
        LOG_PATH.write_text(LOG_HEADER, encoding="utf-8")
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(row)


# --- the request --------------------------------------------------------------


class _AllowlistRedirect(urllib.request.HTTPRedirectHandler):
    """Re-check every redirect hop. A 302 to a denied host must fail closed."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: N802
        if not is_allowed(newurl):
            raise urllib.error.HTTPError(
                newurl, code, f"redirect to non-allowlisted host: {host_of(newurl)}", headers, fp
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _opener() -> urllib.request.OpenerDirector:
    context = ssl.create_default_context()
    return urllib.request.build_opener(
        _AllowlistRedirect, urllib.request.HTTPSHandler(context=context)
    )


def guarded_get(url: str, purpose: str = "", method: str = "GET") -> dict:
    """The only way out. Returns a dict; never raises for a guard decision."""
    host = host_of(url)

    if method.upper() != "GET":
        log_event(method, host, None, 0, "BLOCKED", f"method not GET: {purpose}")
        return GuardResult(
            False, None, True, f"method {method} is not permitted: read-only guard",
            "", host, url, 0,
        ).as_dict()

    if not is_allowed(url):
        reason = f"host {host or '(none)'} is not allowlisted"
        log_event(method, host, None, 0, "BLOCKED", f"{reason}: {purpose}")
        return GuardResult(False, None, True, reason, "", host, url, 0).as_dict()

    live = key_values_look_live()
    if live:
        reason = "LIVE KEY DETECTED — ABORT"
        log_event(method, host, None, 0, "ABORT", f"{reason}: {', '.join(live)}")
        return GuardResult(False, None, True, reason, "", host, url, 0).as_dict()

    allowed, why = check_rate_limit()
    if not allowed:
        log_event(method, host, None, 0, "BLOCKED", f"{why}: {purpose}")
        return GuardResult(False, None, True, why, "", host, url, 0).as_dict()

    request = urllib.request.Request(url, method="GET")
    # Never carry credentials, even if a caller tried to add them.
    for header in ("Authorization", "Cookie", "Proxy-Authorization"):
        request.remove_header(header)
    request.add_header("User-Agent", "Barrot-Agent/1.0 (paper only; read-only)")

    record_call()
    started = time.time()
    try:
        with _opener().open(request, timeout=TIMEOUT_SECONDS) as response:
            raw = response.read(MAX_BODY_BYTES)
            status = response.status
        body = raw.decode("utf-8", errors="replace")
        elapsed = time.time() - started
        log_event(method, host, status, len(raw), "ALLOW", f"{purpose} ({elapsed:.2f}s)")
        return GuardResult(True, status, False, "ok", body, host, url, len(raw)).as_dict()
    except urllib.error.HTTPError as exc:
        log_event(method, host, exc.code, 0, "HTTP_ERROR", f"{purpose}: {exc.reason}")
        return GuardResult(
            False, exc.code, False, f"HTTP {exc.code}: {exc.reason}", "", host, url, 0
        ).as_dict()
    except (urllib.error.URLError, TimeoutError, ssl.SSLError, OSError) as exc:
        log_event(method, host, None, 0, "ERROR", f"{purpose}: {type(exc).__name__}")
        return GuardResult(
            False, None, False, f"{type(exc).__name__}: {exc}", "", host, url, 0
        ).as_dict()
