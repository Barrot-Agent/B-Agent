from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_score_parser_accepts_only_complete_valid_contract():
    module = load_script(REPO_ROOT / "scripts" / "emit_signal.py", "emit_signal_contract_valid")
    assert module._score_from_text('{"score":72,"confidence":0.8,"label":"bullish"}') == (72, 0.8, "bullish")
    assert module._score_from_text('{"score":45,"confidence":0,"label":"NEUTRAL"}') == (45, 0.0, "neutral")


def test_score_parser_rejects_malformed_missing_and_coerced_values():
    module = load_script(REPO_ROOT / "scripts" / "emit_signal.py", "emit_signal_contract_invalid")
    invalid = [
        "",
        "not json",
        '{"score":50,"confidence":0.5}',
        '{"score":"50","confidence":0.5,"label":"neutral"}',
        '{"score":true,"confidence":0.5,"label":"neutral"}',
        '{"score":101,"confidence":0.5,"label":"bullish"}',
        '{"score":50,"confidence":1.1,"label":"neutral"}',
        '{"score":50,"confidence":NaN,"label":"neutral"}',
        '{"score":50,"confidence":0.5,"label":"unknown"}',
        '[]',
    ]
    assert all(module._score_from_text(value) is None for value in invalid)


def test_provider_failures_return_unavailable_not_zero(monkeypatch):
    module = load_script(REPO_ROOT / "scripts" / "emit_signal.py", "emit_signal_provider_failure")

    def fail(_text):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(module, "_call_github_models", fail)
    monkeypatch.setattr(module, "_call_groq", fail)
    score, confidence, source = module.analyze_signal("test")
    assert score is None
    assert confidence is None
    assert "sentiment unavailable" in source


def test_news_gate_rejects_missing_naive_future_and_academic_timestamps(tmp_path: Path):
    module = load_script(REPO_ROOT / "scripts" / "emit_signal.py", "emit_signal_news_gate")
    now = datetime.now(timezone.utc)
    published = now.isoformat()
    entries = [
        {"distilled": True, "published": published, "distill": {"xrp_relevance": 1, "sentiment": "bullish"}, "title": "missing ingestion timestamp"},
        {"distilled": True, "ingested_at": now.replace(tzinfo=None).isoformat(), "published": published, "distill": {"xrp_relevance": 1, "sentiment": "bullish"}},
        {"distilled": True, "ingested_at": (now + timedelta(minutes=10)).isoformat(), "published": published, "distill": {"xrp_relevance": 1, "sentiment": "bullish"}},
        {"distilled": True, "ingested_at": now.isoformat(), "published": published, "source": "academic", "distill": {"xrp_relevance": 1, "sentiment": "bullish"}},
        {"distilled": True, "ingested_at": "not-a-time", "published": published, "distill": {"xrp_relevance": 1, "sentiment": "bullish"}},
        {"distilled": True, "ingested_at": now.isoformat(), "published": published, "distill": {"xrp_relevance": 1, "sentiment": "unverified"}},
    ]
    path = tmp_path / "news.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in entries) + "\n", encoding="utf-8")
    assert module._news_score(path=str(path)) == (None, 0, [])


def test_news_gate_accepts_recent_timestamped_entries(tmp_path: Path):
    module = load_script(REPO_ROOT / "scripts" / "emit_signal.py", "emit_signal_news_valid")
    now = datetime.now(timezone.utc).isoformat()
    entries = [
        {"distilled": True, "ingested_at": now, "published": now, "source": "wire-a", "title": "A", "distill": {"xrp_relevance": 0.8, "sentiment": "bullish"}},
        {"distilled": True, "ingested_at": now, "published": now, "source": "wire-b", "title": "B", "distill": {"xrp_relevance": 0.2, "sentiment": "bearish"}},
    ]
    path = tmp_path / "news.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in entries) + "\n", encoding="utf-8")
    score, count, headlines = module._news_score(path=str(path))
    assert score == 80
    assert count == 2
    assert len(headlines) == 1



def test_news_gate_uses_published_event_time_and_accepts_rss_dates(tmp_path: Path):
    module = load_script(REPO_ROOT / "scripts" / "emit_signal.py", "emit_signal_event_time_gate")
    now = datetime.now(timezone.utc)
    entries = [
        {
            "distilled": True,
            "ingested_at": now.isoformat(),
            "published": (now - timedelta(days=4)).isoformat(),
            "source": "wire-a",
            "title": "Old story re-ingested today",
            "distill": {"xrp_relevance": 1.0, "sentiment": "bullish"},
        },
        {
            "distilled": True,
            "ingested_at": now.isoformat(),
            "published": (now + timedelta(minutes=10)).isoformat(),
            "source": "wire-b",
            "title": "Future-dated story",
            "distill": {"xrp_relevance": 1.0, "sentiment": "bullish"},
        },
        {
            "distilled": True,
            "ingested_at": now.isoformat(),
            "published": now.strftime("%a, %d %b %Y %H:%M:%S +0000"),
            "source": "wire-c",
            "title": "Recent RSS story",
            "distill": {"xrp_relevance": 1.0, "sentiment": "bullish"},
        },
    ]
    path = tmp_path / "event_time_news.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in entries) + "\n", encoding="utf-8")
    score, count, headlines = module._news_score(path=str(path))
    assert score == 100
    assert count == 1
    assert headlines == ["[bullish] Recent RSS story"]


def test_news_gate_rejects_observed_research_titles_and_academic_urls(tmp_path: Path):
    module = load_script(REPO_ROOT / "scripts" / "emit_signal.py", "emit_signal_academic_source_gate")
    now = datetime.now(timezone.utc).isoformat()
    titles = [
        "Analysis of the XRP Ledger Consensus Protocol",
        "To Squelch or not to Squelch: Message Dissemination on the XRP Ledger",
        "Probabilistic Edge Multicast Routing for the XRP Network",
        "Pub/Sub Dissemination on the XRP Ledger",
        "Consensus Crash Testing: Ripple Decentralization Degree in Adversarial Environment",
        "Causal AI for XRPL/GossipSub network configuration",
        "A general market update hosted on an arXiv paper page",
    ]
    entries = []
    for index, title in enumerate(titles):
        entries.append({
            "distilled": True,
            "ingested_at": now,
            "published": now,
            "source": "online_articles",
            "feed": "https://news.google.com/rss/search?q=xrp",
            "url": "https://arxiv.org/abs/2026.0000" if index == len(titles) - 1 else "https://news.google.com/rss/articles/example",
            "title": title,
            "distill": {"xrp_relevance": 1.0, "sentiment": "bullish"},
        })
    path = tmp_path / "academic_news.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in entries) + "\n", encoding="utf-8")
    assert module._news_score(path=str(path)) == (None, 0, [])


def test_main_keeps_news_score_separate_when_model_is_unavailable(tmp_path: Path, monkeypatch):
    module = load_script(REPO_ROOT / "scripts" / "emit_signal.py", "emit_signal_main_unavailable")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(module, "_news_score", lambda: (88, 11, ["[bullish] headline"]))
    monkeypatch.setattr(module, "analyze_signal", lambda _text: (None, None, "sentiment unavailable"))
    module.main()
    output = json.loads((tmp_path / "web" / "latest_signal.json").read_text(encoding="utf-8"))
    assert output["score"] is None
    assert output["model_score"] is None
    assert output["confidence"] is None
    assert output["news_score"] == 88
    assert output["signal_status"] == "news_only"
    assert output["forecast_status"] == "NOT_ISSUED"
    assert not (tmp_path / "web" / "signal_history.jsonl").exists()


def test_accuracy_evaluator_does_not_mutate_legacy_history(tmp_path: Path, monkeypatch):
    module = load_script(REPO_ROOT / "scripts" / "check_signal_accuracy.py", "legacy_accuracy_read_only")
    history = tmp_path / "signal_history.jsonl"
    original = '{"score":44,"price_at_emission":1.2}\n{"score":null}\n'
    history.write_text(original, encoding="utf-8")
    monkeypatch.setattr(module, "HISTORY_PATH", history)
    monkeypatch.setattr(module, "SUMMARY_PATH", tmp_path / "signal_accuracy.json")
    summary = module.main()
    assert history.read_text(encoding="utf-8") == original
    assert summary["status"] == "NOT_EVALUATED"
    assert summary["accuracy_pct"] is None
    assert summary["legacy_history_rows"] == 2


def test_hrm_sandbox_skips_unavailable_score(tmp_path: Path, monkeypatch):
    module = load_script(REPO_ROOT / "scripts" / "emit_signal_with_hrm.py", "hrm_sandbox_unavailable")
    live = tmp_path / "latest_signal.json"
    output = tmp_path / "hrm_sandbox_signal.json"
    live.write_text('{"score":null,"forecast_status":"NOT_ISSUED"}', encoding="utf-8")
    monkeypatch.setattr(module, "LIVE_PATH", live)
    monkeypatch.setattr(module, "OUT_PATH", output)
    module.main()
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["status"] == "NOT_ISSUED"
    assert result["forecast_status"] == "NOT_ISSUED"
    assert "hrm_state" not in result




def test_accuracy_summary_preserves_legacy_metric_as_not_comparable(tmp_path: Path, monkeypatch):
    module = load_script(REPO_ROOT / "scripts" / "check_signal_accuracy.py", "legacy_accuracy_preserve_metric")
    history = tmp_path / "signal_history.jsonl"
    history.write_text("", encoding="utf-8")
    summary_path = tmp_path / "signal_accuracy.json"
    summary_path.write_text(json.dumps({
        "checked_count": 1612,
        "correct_count": 749,
        "accuracy_pct": 46.5,
    }), encoding="utf-8")
    monkeypatch.setattr(module, "HISTORY_PATH", history)
    monkeypatch.setattr(module, "SUMMARY_PATH", summary_path)

    summary = module.main()
    assert summary["status"] == "NOT_EVALUATED"
    assert summary["accuracy_pct"] is None
    assert summary["legacy_metric"]["checked_count"] == 1612
    assert summary["legacy_metric"]["correct_count"] == 749
    assert summary["legacy_metric"]["accuracy_pct"] == 46.5
    assert summary["legacy_metric"]["validity"] == "NOT_COMPARABLE"


def test_accuracy_workflow_is_read_only_and_artifact_only():
    workflow = (REPO_ROOT / ".github" / "workflows" / "check-signal-accuracy.yml").read_text(encoding="utf-8")
    assert "contents: read" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "git push" not in workflow
    assert "git commit" not in workflow


def test_ci_runs_xrp_signal_integrity_suite():
    workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "tests/test_xrp_signal_integrity.py" in workflow
