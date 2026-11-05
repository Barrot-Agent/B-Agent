import json
from pathlib import Path

from scripts import check_signal_accuracy, daily_digest


def test_retired_scorer_is_read_only_and_does_not_rewrite_legacy_files(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    web = tmp_path / "web"
    web.mkdir()
    history = web / "signal_history.jsonl"
    summary = web / "signal_accuracy.json"
    history.write_text('{"score": 80, "generated_at_unix": 1}\n', encoding="utf-8")
    summary.write_text('{"checked_count": 1697, "correct_count": 772, "accuracy_pct": 45.5}\n', encoding="utf-8")
    before = (history.read_bytes(), summary.read_bytes())

    assert check_signal_accuracy.main() == 0
    result = json.loads(capsys.readouterr().out)

    assert result["status"] == "NOT_EVALUATED"
    assert result["forecast_issued"] is False
    assert result["reason_code"] == "LEGACY_VARIABLE_HORIZON_SCORER_RETIRED"
    assert (history.read_bytes(), summary.read_bytes()) == before


def test_daily_digest_never_publishes_legacy_signal_or_accuracy(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    web = tmp_path / "web"
    web.mkdir()
    (web / "latest_signal.json").write_text(
        json.dumps({"score": 44, "confidence": 0.0, "source": "legacy"}),
        encoding="utf-8",
    )
    (web / "signal_accuracy.json").write_text(
        json.dumps({"checked_count": 1697, "correct_count": 772, "accuracy_pct": 45.5}),
        encoding="utf-8",
    )
    monkeypatch.setattr(daily_digest, "_count_recent_kb", lambda: 0)
    monkeypatch.setattr(daily_digest, "_count_recent_content", lambda: 0)

    daily_digest.main()
    body = (tmp_path / "digest_body.md").read_text(encoding="utf-8")

    assert "NOT_ISSUED" in body
    assert "NOT_EVALUATED" in body
    assert "45.5" not in body
    assert "score 44" not in body.lower()
    assert "confidence 0.0" not in body.lower()


def test_public_json_artifacts_do_not_expose_a_directional_forecast():
    latest = json.loads(Path("web/latest_signal.json").read_text(encoding="utf-8"))
    accuracy = json.loads(Path("web/signal_accuracy.json").read_text(encoding="utf-8"))
    summary = json.loads(Path("web/latest_signal_summary.json").read_text(encoding="utf-8"))

    assert latest["status"] == "NOT_ISSUED"
    assert latest["forecast_issued"] is False
    assert latest["probabilities"] is None
    assert "score" not in latest
    assert latest["legacy_sentiment_observation"]["forecast_eligible"] is False

    assert accuracy["status"] == "NOT_EVALUATED"
    assert accuracy["accuracy_pct"] is None
    assert accuracy["forecast_eligible"] is False
    assert accuracy["legacy_observation"]["reported_percentage"] == 45.5
    assert accuracy["legacy_observation"]["valid_predictive_accuracy"] is False

    assert summary["forecast_status"] == "NOT_ISSUED"
    assert summary["audio"] is None
    assert summary["source_signal"] is None


def test_public_pages_and_webmcp_do_not_sell_or_render_legacy_directional_signals():
    landing = Path("web/landing.html").read_text(encoding="utf-8")
    subscriber = Path("web/signals.html").read_text(encoding="utf-8")
    monetization = Path("web/webmcp_monetization.js").read_text(encoding="utf-8")

    for forbidden in (
        "prostarelite.gumroad.com",
        "GET SIGNALS",
        "SUBSCRIBE NOW",
        "AUTONOMOUS XRP SIGNAL SERVICE",
        "Every hour, XRP resolves",
        "1.58-BIT TERNARY LOGIC",
    ):
        assert forbidden.lower() not in landing.lower()
    assert "NOT_ISSUED" in landing
    assert "PAUSED_PENDING_VALIDATION" in landing

    assert "NOT_ISSUED" in subscriber
    assert "BUY" not in subscriber
    assert "SELL" not in subscriber
    assert "latest_signal.json?" not in subscriber
    assert "prostarelite.gumroad.com" not in subscriber

    assert "PAUSED_PENDING_VALIDATION" in monetization
    assert "purchase_url: null" in monetization


def test_legacy_accuracy_and_digest_workflows_remain_disabled():
    accuracy_workflow = Path(".github/workflows/check-signal-accuracy.yml").read_text(encoding="utf-8")
    digest_workflow = Path(".github/workflows/daily-digest.yml").read_text(encoding="utf-8")

    for workflow in (accuracy_workflow, digest_workflow):
        lowered = workflow.lower()
        assert "workflow_dispatch: {}" in workflow
        assert "permissions: {}" in workflow
        assert "if: false" in workflow
        assert "schedule:" not in lowered
        assert "contents: write" not in lowered
