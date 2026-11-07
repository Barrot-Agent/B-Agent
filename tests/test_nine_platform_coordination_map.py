from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "data/xrp_intelligence/architecture_decisions/20261101T230851Z-nine-platform-coordination-map.json"
EXPECTED = {"ChatGPT", "Claude", "Grok", "Gemini", "Copilot", "Codex", "HuggingFace", "Kaggle", "Databricks"}


def load():
    return json.loads(MAP.read_text(encoding="utf-8"))


def test_all_nine_target_platforms_are_mapped_without_false_connection_claims():
    d = load()
    assert set(d["platforms"]) == EXPECTED
    assert d["status"] == "DESIGNED_NOT_CONNECTED"
    assert d["platforms"]["ChatGPT"]["status"] == "VERIFIED_ACTIVE_CURRENT_SESSION"
    for name in EXPECTED - {"ChatGPT"}:
        assert d["platforms"][name]["status"] == "NOT_CONNECTED_OR_NOT_TESTED"
    assert d["connection_claim_policy"].startswith("Only ChatGPT current session and GitHub")


def test_platform_map_defines_least_privilege_and_no_unapproved_mutations():
    d = load()
    safety = d["authentication_and_safety"]
    assert "Least privilege" in safety["default"]
    assert "No main-branch writes" in safety["write_controls"]
    assert "never fabricate" in safety["rate_limits"]


def test_evidence_packets_preserve_dissent_and_require_provenance():
    d = load()
    schema = d["evidence_packet_schema"]
    assert "data_cutoff_utc" in schema["required_fields"]
    assert "counter_evidence" in schema["required_fields"]
    assert "minority_objection" in schema["required_fields"]
    assert d["disagreement_resolution"]["no_forced_unanimity"] is True
    assert d["disagreement_resolution"]["preserve_minority_objections"] is True
