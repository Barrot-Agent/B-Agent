from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_current.json"


def _load_map() -> dict:
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def test_run175_current_main_successor_snapshot_is_explicit() -> None:
    data = _load_map()
    run = data["run175_snapshot"]
    assert data["latest_run_id"] == "Run175"
    assert data["current_repository_state"]["main_sha"] == "5b2a9c46eb878250dfec99190e294909cd5835bf"
    assert run["main_sha"] == "5b2a9c46eb878250dfec99190e294909cd5835bf"
    assert run["successor_head_before_run175_commit"] == "692caffaba27e9653fddfde3823785efad096e17"
    assert run["ci"]["tests_collected"] == 3808
    assert run["ci"]["tests_passed"] == 3807
    assert run["ci"]["tests_failed"] == 0
    assert run["ci"]["tests_skipped"] == 1
    assert run["ci"]["subtests_passed"] == 19
    assert run["ci"]["inclusive_coverage_pct"] == 64.02
    assert run["prediction"]["forecast_status"] == "NOT_ISSUED"
    assert run["prediction"]["accuracy_status"] == "NOT_EVALUATED"
    assert run["pr_1662"]["state"] == "closed"
    assert run["pr_1662"]["merged"] is False
    assert run["open_prs"]["count"] == 8
    assert run["tree_reconciliation"]["main_paths_missing_after_restore"] == 0


def test_run175_restores_current_main_barrot_state_blobs_byte_for_byte() -> None:
    data = _load_map()
    expected = data["run175_snapshot"]["preservation"]["restored_main_blob_sha1"]
    assert len(expected) == 10
    for relative_path, expected_sha in expected.items():
        payload = (ROOT / relative_path).read_bytes()
        header = b"blob " + str(len(payload)).encode("ascii") + b"\0"
        actual_sha = hashlib.sha1(header + payload).hexdigest()
        assert actual_sha == expected_sha, relative_path


def test_run175_platform_map_does_not_claim_unverified_external_connections() -> None:
    data = _load_map()
    platforms = data["run175_snapshot"]["platforms"]
    assert platforms["ChatGPT"]["authentication_status"] == "VERIFIED_CURRENT_SESSION"
    assert platforms["Claude"]["authentication_status"] == "UNVERIFIED_NO_AUTH_TEST"
    assert platforms["Grok"]["authentication_status"] == "UNVERIFIED_NO_AUTH_TEST"
    assert platforms["Gemini"]["authentication_status"] == "UNVERIFIED_NO_AUTH_TEST"
    assert platforms["Codex"]["authentication_status"] == "UNVERIFIED_NO_AUTH_TEST"
    assert platforms["Groq"]["dispatch"] is False
    assert platforms["ChatGPT"]["external_model_transfer"] is False


def test_run175_self_benchmark_is_quarantined_until_isolated() -> None:
    workflow = (ROOT / ".github/workflows/self-benchmark.yml").read_text(encoding="utf-8")
    assert "permissions: {}" in workflow
    assert "if: ${{ false }}" in workflow
    assert "GROQ_API_KEY" not in workflow
    assert "network-disabled" in workflow


def test_run175_credential_file_stays_absent_and_ignored() -> None:
    assert not (ROOT / ".config/gh/hosts.yml").exists()
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".config/gh/hosts.yml" in ignore
    audit = _load_map()["run175_snapshot"]["credential_path_audit"]
    assert audit["open_pr_branch_tips_with_path"] == 8
    assert audit["content_read"] is False
    assert audit["credential_rotation_performed"] is False


def test_run175_preserves_verified_opencode_default_and_disables_unverified_lunaroute() -> None:
    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    assert config["default_agent"] == "barrot"
    assert config["model"] == "opencode/deepseek-v4.1-flash-free"
    assert config["agent"]["barrot"]["model"] == "opencode/deepseek-v4.1-flash-free"
    assert config["mcp"]["servers"]["lunaroute"]["disabled"] is True
    assert "authentication" in config["agent"]["barrot"]["prompt"].lower()
    assert config["permission"]["edit"] == "ask"
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "authentication and model data-flow have not been verified" in agents
    assert agents.count("## Permanent memory") == 1
    prompt = (ROOT / ".opencode/agent/barrot.md").read_text(encoding="utf-8")
    assert "offline phone deployment in Termux" in prompt
    assert "Highest priority: XRP intelligence" in prompt
    assert "transmute.py" in prompt and "QUARANTINED" in prompt
    assert "git add -A" in prompt


def test_run175_historical_gitignore_digest_is_retained_and_current_rules_remain() -> None:
    data = _load_map()
    # Run175's digest is historical evidence. Main has since advanced; do not
    # compare the current .gitignore against an obsolete snapshot.
    assert data["run175_snapshot"]["preservation"]["main_gitignore_blob_sha1"] == (
        "f63d4ea6c01a6dbeb72cd80d8f5fcdac93ea66d4"
    )
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for required in (
        ".config/gh/hosts.yml",
        ".config/gh/",
        "data/xrp_intelligence/forecast_ledger.sqlite3",
        "data/xrp_intelligence/feature_store.sqlite3",
    ):
        assert required in ignore
