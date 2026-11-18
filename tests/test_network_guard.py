"""Guard tests for the single approved network module.

Scope note, stated so the claim is not wider than the evidence: the AST check
below covers the trading package, the four trading CLI scripts, the live-ingest
script, and the Chrome sandbox. It does not cover the pre-existing repo surface
(the repo already had ~50 modules importing urllib before this guard existed),
so this is a scoped invariant, not a repo-wide one.

Nothing here touches the real log or the real rate-limit state: both paths are
redirected to tmp_path for every test.
"""
from __future__ import annotations

import ast
import json
import time
from pathlib import Path

import pytest

import barrot_agent.network_guard as ng

ROOT = Path(__file__).resolve().parents[1]

SCOPED_MODULES = [
    ROOT / "barrot_agent/trading/paper_sandbox.py",
    ROOT / "barrot_agent/trading/xrp_rotation.py",
    ROOT / "barrot_agent/trading/xrp_batch.py",
    ROOT / "barrot_agent/trading/xrp_cycle.py",
    ROOT / "scripts/paper_trade.py",
    ROOT / "scripts/xrp_loop.py",
    ROOT / "scripts/xrp_batch1.py",
    ROOT / "scripts/xrp_cycle.py",
    ROOT / "scripts/ingest_live.py",
]
FORBIDDEN_MODULES = {
    "socket", "ssl", "urllib", "http", "requests", "aiohttp", "httpx",
    "websocket", "websockets", "ccxt", "web3",
}


@pytest.fixture(autouse=True)
def isolated_paths(monkeypatch, tmp_path):
    """Never write the real NETWORK_LOG.md or the real rate-limit state."""
    monkeypatch.setattr(ng, "LOG_PATH", tmp_path / "NETWORK_LOG.md")
    monkeypatch.setattr(ng, "STATE_PATH", tmp_path / "state.json")
    return tmp_path


@pytest.fixture
def no_credentials(monkeypatch):
    """Remove credential-shaped variables so the key gate is not what blocks."""
    for name in ng.detect_live_keys():
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


# --- allowlist ----------------------------------------------------------------


@pytest.mark.parametrize("host", ng.ALLOWED_DOMAINS)
def test_every_listed_domain_is_allowed(host):
    assert ng.is_allowed(f"https://{host}/some/path") is True


@pytest.mark.parametrize(
    "url",
    [
        "https://chromium.googlesource.com/chromium/src/+log/main",
        "https://sub.api.coingecko.com/x",          # real subdomain
        "https://raw.githubusercontent.com/o/r/main/f",
        "https://en.wikipedia.org/wiki/XRP",
    ],
)
def test_subdomains_and_paths_allowed(url):
    assert ng.is_allowed(url) is True


@pytest.mark.parametrize(
    "url",
    [
        "https://api.binance.com/api/v3/ticker/price",
        "https://kraken.com",
        "https://api.coinbase.com/v2/prices/XRP-USD/spot",
        "https://discord.com/api",
        "https://kaggle.com.evil.example/model",     # suffix lookalike
        "https://evil-kaggle.com/model",             # prefix lookalike
        "https://notkaggle.com/model",               # substring lookalike
        "http://api.coingecko.com/api/v3/ping",      # plain http
        "ftp://api.coingecko.com/x",
        "https://api.coingecko.com@evil.example/x",  # userinfo smuggling
        "https:///nohost",
        "",
    ],
)
def test_non_allowlisted_is_denied(url):
    assert ng.is_allowed(url) is False


def test_host_of_returns_lowercase_hostname():
    assert ng.host_of("https://API.CoinGecko.com/x") == "api.coingecko.com"
    assert ng.host_of("not a url") == ""


# --- method -------------------------------------------------------------------


@pytest.mark.parametrize("method", ["POST", "PUT", "DELETE", "PATCH", "post"])
def test_write_methods_are_blocked(method):
    result = ng.guarded_get("https://api.coingecko.com/api/v3/ping",
                            purpose="method test", method=method)
    assert result["blocked"] is True
    assert result["status"] is None
    assert result["bytes_read"] == 0
    assert "read-only" in result["reason"]


def test_blocked_method_is_logged(isolated_paths):
    ng.guarded_get("https://api.coingecko.com/api/v3/ping", method="POST")
    log = (isolated_paths / "NETWORK_LOG.md").read_text(encoding="utf-8")
    assert "BLOCKED" in log
    assert "api.coingecko.com" in log


# --- credentials --------------------------------------------------------------


def test_key_detection_ignores_path_and_shell_variables(no_credentials):
    monkeypatch = no_credentials
    monkeypatch.setenv("MY_API_KEY", "a" * 32)
    monkeypatch.setenv("SOME_KEY_PATH", "/tmp/x")
    monkeypatch.setenv("PWD", "/root")
    found = ng.detect_live_keys()
    assert "MY_API_KEY" in found
    assert "SOME_KEY_PATH" not in found
    assert "PWD" not in found


def test_short_value_is_not_treated_as_live(no_credentials):
    no_credentials.setenv("PLACEHOLDER_TOKEN", "changeme")
    assert "PLACEHOLDER_TOKEN" not in ng.key_values_look_live()


def test_live_key_aborts_without_reading_the_value(no_credentials, isolated_paths):
    secret = "sk-" + "z" * 40
    no_credentials.setenv("LEAKY_API_KEY", secret)
    result = ng.guarded_get("https://api.coingecko.com/api/v3/ping", purpose="key test")
    assert result["blocked"] is True
    assert result["reason"] == "LIVE KEY DETECTED — ABORT"
    log = (isolated_paths / "NETWORK_LOG.md").read_text(encoding="utf-8")
    assert "LEAKY_API_KEY" in log      # the name is recorded
    assert secret not in log           # the value never is
    assert "LIVE KEY DETECTED" in log


def test_clearing_credentials_gets_past_the_key_gate(no_credentials, isolated_paths):
    """With no keys and a full rate-limit window the block must be the rate limit."""
    assert ng.key_values_look_live() == []
    isolated_paths.joinpath("state.json").write_text(
        json.dumps({"calls": [time.time()]}), encoding="utf-8"
    )
    result = ng.guarded_get("https://api.coingecko.com/api/v3/ping", purpose="gate order")
    assert "rate limit" in result["reason"]
    assert result["reason"] != "LIVE KEY DETECTED — ABORT"


# --- rate limit ---------------------------------------------------------------


def test_rate_limit_allows_a_cold_state():
    allowed, why = ng.check_rate_limit(now=1000.0, state={"calls": []})
    assert allowed is True and why == "ok"


def test_rate_limit_blocks_two_calls_inside_two_seconds():
    allowed, why = ng.check_rate_limit(now=1000.0, state={"calls": [999.0]})
    assert allowed is False
    assert "rate limit" in why


def test_rate_limit_allows_after_the_interval():
    allowed, _ = ng.check_rate_limit(now=1002.1, state={"calls": [1000.0]})
    assert allowed is True


def test_hourly_cap_blocks():
    now = 10_000.0
    # Start just inside the window: exactly 3600s old is already pruned.
    state = {"calls": [now - 3599 + i * 50 for i in range(ng.MAX_REQUESTS_PER_HOUR)]}
    allowed, why = ng.check_rate_limit(now=now, state=state)
    assert allowed is False
    assert "hourly cap" in why


def test_calls_older_than_an_hour_are_forgotten():
    now = 10_000.0
    state = {"calls": [now - 7200.0, now - 4000.0]}
    assert ng.recent_calls(state, now) == []


def test_record_call_persists_and_prunes(isolated_paths):
    ng.record_call(now=5000.0)
    ng.record_call(now=7000.0)
    state = json.loads((isolated_paths / "state.json").read_text(encoding="utf-8"))
    assert state["calls"] == [5000.0, 7000.0]

    # 10_000 is 5000s after the first call, so the first one falls out of the window
    ng.record_call(now=10_000.0)
    state = json.loads((isolated_paths / "state.json").read_text(encoding="utf-8"))
    assert 5000.0 not in state["calls"]
    assert 7000.0 in state["calls"] and 10_000.0 in state["calls"]


def test_corrupt_state_fails_closed_to_empty(isolated_paths):
    (isolated_paths / "state.json").write_text("{not json", encoding="utf-8")
    assert ng._load_state() == {"calls": []}


# --- logging ------------------------------------------------------------------


def test_log_row_sanitises_pipes_and_newlines(isolated_paths):
    ng.log_event("GET", "api.coingecko.com", 200, 10, "ALLOW", "a|b\nc")
    log = (isolated_paths / "NETWORK_LOG.md").read_text(encoding="utf-8")
    row = [line for line in log.splitlines() if line.startswith("| 20")][0]
    assert row.count("|") == 8          # 7 columns, 8 separators
    assert "a/b c" in row


def test_log_header_written_once(isolated_paths):
    ng.log_event("GET", "x", 200, 1, "ALLOW", "one")
    ng.log_event("GET", "x", 200, 1, "ALLOW", "two")
    log = (isolated_paths / "NETWORK_LOG.md").read_text(encoding="utf-8")
    assert log.count("# NETWORK LOG") == 1
    assert log.count("ALLOW") == 2


# --- AST invariant ------------------------------------------------------------


def _imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            roots.add(node.module.split(".")[0])
    return roots


@pytest.mark.parametrize("path", SCOPED_MODULES, ids=lambda p: p.name)
def test_only_network_guard_may_import_network_modules(path):
    if not path.exists():
        pytest.skip(f"{path.name} not present")
    hits = _imported_roots(path) & FORBIDDEN_MODULES
    assert hits == set(), f"{path.name} imports {sorted(hits)}; route it through network_guard"


def test_network_guard_is_the_approved_exception():
    roots = _imported_roots(ROOT / "barrot_agent/network_guard.py")
    assert "urllib" in roots and "ssl" in roots


def test_trading_package_does_not_import_the_guard_backwards():
    """The engine must be callable without network access at all."""
    for path in (ROOT / "barrot_agent/trading").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert "network_guard" not in node.module, f"{path.name} couples to the network"
