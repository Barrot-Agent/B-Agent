from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows"


ARTIFACT_ONLY = {
    "check-signal-accuracy.yml": ["web/signal_history.jsonl", "web/signal_accuracy.json"],
    "financial-data-refresh.yml": ["financial_data.json"],
    "knowledge-signal-cycle.yml": ["log.jsonl", "latest_signal.json"],
    "knowledge-signal-cycle-btc.yml": ["log_btc.jsonl", "latest_signal_btc.json"],
    "data-value-triage.yml": ["triage_results_*.json"],
    "entity-relations.yml": ["entity_relations.json"],
    "research-topics.yml": ["topics_log.jsonl"],
    "coinbase-paper-trader.yml": ["paper_trading_state.json", "paper_trading_log.jsonl"],
    "self-benchmark.yml": ["benchmark_log.jsonl"],
    "subagent-spawn.yml": ["subagent_run_*.json"],
    "webmcp-trend-digest.yml": ["webmcp_trend_summary.json"],
    "webmcp-monetization-enrich.yml": ["webmcp_monetization_signals.json"],
    "content-pipeline.yml": ["content/"],
    "frontier-digest.yml": ["frontier_log.jsonl", "upgrade_recommendations.jsonl"],
    "riemann-harvest.yml": ["riemann_hypothesis_harvest.json", "riemann_research_corpus.js"],
    "free-image-gen.yml": ["generated_images/"],
    "hover_bike_updates.yml": ["hover_bike_spec.json", "component_geometry.json"],
    "pingpong.yml": ["log.jsonl"],
    "make-track.yml": ["music/"],
    "gumroad-metrics.yml": ["gumroad_metrics.json"],
}


def test_selected_main_writers_are_read_only_and_artifact_only():
    for name, expected_paths in ARTIFACT_ONLY.items():
        text = (WF / name).read_text(encoding="utf-8")
        assert "contents: read" in text, name
        assert "actions/upload-artifact@" in text, name
        assert "git push" not in text, name
        assert "git commit" not in text, name
        assert "gh pr merge" not in text, name
        for expected in expected_paths:
            assert expected in text, (name, expected)


def test_private_subscriber_sync_is_manual_explicit_and_non_persistent():
    text = (WF / "subscriber_sync.yml").read_text(encoding="utf-8")
    assert "schedule:" not in text
    assert "confirm_private_data_processing" in text
    assert 'default: "NO"' in text
    assert "inputs.confirm_private_data_processing == 'YES'" in text
    assert "contents: read" in text
    assert "git push" not in text
    assert "actions/upload-artifact@" not in text
    assert "rm -f web/subscribers.json" in text


def test_brain_corpus_export_requires_explicit_approval_and_short_retention():
    text = (WF / "dump-brain-corpus.yml").read_text(encoding="utf-8")
    assert "confirm_private_data_processing" in text
    assert 'default: "NO"' in text
    assert "inputs.confirm_private_data_processing == 'YES'" in text
    assert "contents: read" in text
    assert "retention-days: 1" in text
    assert "git push" not in text


def test_force_push_and_destructive_hf_admin_workflows_are_disabled():
    admin = (WF / "barrot-hf-admin.yml").read_text(encoding="utf-8")
    force = (WF / "force-deploy-space.yml").read_text(encoding="utf-8")
    for text in (admin, force):
        assert "permissions: {}" in text
        assert "HF_TOKEN" not in text
    assert "curl -X DELETE" not in admin
    assert "git push -f" not in force


def test_huggingface_model_uploads_require_explicit_confirmation_and_safe_name():
    for name in ("barrot-merge.yml", "barrot-merge-manual.yml"):
        text = (WF / name).read_text(encoding="utf-8")
        assert "confirm_external_change" in text
        assert 'default: "NO"' in text
        assert "inputs.confirm_external_change == 'YES'" in text
        assert "MODEL_NAME" in text
        assert "A-Za-z0-9._-" in text
        assert "blocked:" in text
