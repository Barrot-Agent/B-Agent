import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_paper_trading_state.py"
SPEC = importlib.util.spec_from_file_location("paper_state_audit", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def record(timestamp, product, price, action, amount, portfolio_value):
    return json.dumps({
        "timestamp": timestamp,
        "product": product,
        "price": price,
        "decision": {"action": action, "amount_usd": amount, "reasoning": "fixture"},
        "result": "fixture",
        "portfolio_value_usd": portfolio_value,
    })


def fixture_log():
    return "\n".join([
        record("2026-01-01T00:00:00+00:00", "BTC-USD", 100, "hold", 0, 1000),
        record("2026-01-01T00:01:00+00:00", "BTC-USD", 100, "buy", 100, 1000),
        record("2026-01-01T00:02:00+00:00", "BTC-USD", 110, "sell", 50, 1010),
    ])


def reconciled_state():
    return {
        "cash_usd": 950.0,
        "position_size": 1.0 - (50.0 / 110.0),
        "position_product": None,
        "avg_entry_price": 100.0,
        "trade_count": 2,
    }


def test_exact_replay_reports_candidate_without_mutating_state():
    state = reconciled_state()
    before = state.copy()
    report = AUDIT.audit_state(state, fixture_log())
    assert report["status"] == "RECONCILED_IDENTITY_CANDIDATE"
    assert report["rows_parsed"] == 3
    assert report["product_ids"] == ["BTC-USD"]
    assert report["replayed_state"]["position_product_candidate"] == "BTC-USD"
    assert report["portfolio_value_mismatch_count"] == 0
    assert report["state_mutated"] is False
    assert state == before


def test_multiple_products_block_identity_reconciliation():
    log = fixture_log().replace('"product": "BTC-USD", "price": 110', '"product": "XRP-USD", "price": 110')
    report = AUDIT.audit_state(reconciled_state(), log)
    assert report["status"] == "BLOCKED"
    assert any("identity is ambiguous" in error for error in report["errors"])


def test_corrupt_json_line_blocks_replay():
    report = AUDIT.audit_state(reconciled_state(), fixture_log() + "\nnot-json")
    assert report["status"] == "BLOCKED"
    assert any("invalid JSON" in error for error in report["errors"])


def test_persisted_cash_mismatch_blocks_reconciliation():
    state = reconciled_state()
    state["cash_usd"] += 1
    report = AUDIT.audit_state(state, fixture_log())
    assert report["status"] == "BLOCKED"
    assert any("cash mismatch" in error for error in report["errors"])


def test_portfolio_value_mismatch_blocks_reconciliation():
    log = fixture_log().replace('"portfolio_value_usd": 1010', '"portfolio_value_usd": 900')
    report = AUDIT.audit_state(reconciled_state(), log)
    assert report["status"] == "BLOCKED"
    assert report["portfolio_value_mismatch_count"] == 1


def test_stale_identity_on_flat_position_blocks_reconciliation():
    state = {
        "cash_usd": 1000.0,
        "position_size": 0.0,
        "position_product": "BTC-USD",
        "avg_entry_price": None,
        "trade_count": 0,
    }
    log = record("2026-01-01T00:00:00+00:00", "BTC-USD", 100, "hold", 0, 1000)
    report = AUDIT.audit_state(state, log)
    assert report["status"] == "BLOCKED"
    assert any("stale position_product" in error for error in report["errors"])


def test_out_of_order_timestamps_block_replay():
    log = "\n".join([
        record("2026-01-01T00:01:00+00:00", "BTC-USD", 100, "hold", 0, 1000),
        record("2026-01-01T00:00:00+00:00", "BTC-USD", 100, "hold", 0, 1000),
    ])
    state = {
        "cash_usd": 1000.0,
        "position_size": 0.0,
        "position_product": None,
        "avg_entry_price": None,
        "trade_count": 0,
    }
    report = AUDIT.audit_state(state, log)
    assert report["status"] == "BLOCKED"
    assert any("not chronological" in error for error in report["errors"])


def test_current_repository_state_and_log_reconcile_read_only():
    state_path = REPO_ROOT / "web" / "paper_trading_state.json"
    log_path = REPO_ROOT / "web" / "paper_trading_log.jsonl"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    original_state = state.copy()
    log_text = log_path.read_text(encoding="utf-8")

    report = AUDIT.audit_state(state, log_text)

    assert report["status"] == "RECONCILED_IDENTITY_CANDIDATE"
    assert report["rows_parsed"] == 2345
    assert report["product_ids"] == ["BTC-USD"]
    assert report["portfolio_value_mismatch_count"] == 0
    assert report["replayed_state"]["position_product_candidate"] == "BTC-USD"
    assert report["state_mutated"] is False
    assert state == original_state
