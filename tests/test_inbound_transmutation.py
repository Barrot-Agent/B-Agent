"""Behavioral tests for the bounded Recursive Query Transmutation Protocol.

These tests exercise the live runtime path, not documentation: the exact original
request is preserved, the expansion is structural rather than a paraphrase, every
charter field is present, budgets and stop states are enforced, duplicates are
suppressed, and a record survives a fresh process.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from barrot_agent.inbound import transmutation
from barrot_agent.inbound.gate import Source, _gaps, _tokens
from barrot_agent.inbound.transmutation import (
    Budget,
    CapabilityStatus,
    StopState,
    _hash,
    classify_domains,
    discover_capabilities,
    load_record,
    request_id_for,
    resume,
    transmute_request,
)

ROOT = Path(__file__).resolve().parents[1]
FIXED_NOW = "2026-11-23T16:32:13Z"

DEMO = (
    "Why does Barrot appear to have stopped transmuting queries? Restore his ability to take "
    "incoming requests, understand their deeper objectives, expand them into relevant connected "
    "investigations, identify missing capabilities, discover better approaches, learn from "
    "successful and unsuccessful attempts, and continuously improve his ability to solve problems "
    "without uncontrolled recursion or unnecessary resource consumption."
)

REQUIRED_FIELDS = {
    "request_id",
    "original_request_ref",
    "original_request_hash",
    "intent",
    "invariants",
    "constraints",
    "domains",
    "existing_capabilities",
    "gaps",
    "hypotheses",
    "ranked_plan",
    "budget",
    "execution_mode",
    "evidence_refs",
    "decision",
    "stop_reason",
    "next_checkpoint",
}


def _run(text: str = DEMO, tmp_path: Path | None = None, **kwargs):
    return transmute_request(
        text,
        record_dir=kwargs.pop("record_dir", tmp_path),
        repo_root=ROOT,
        now=kwargs.pop("now", FIXED_NOW),
        **kwargs,
    )


def test_original_request_is_preserved_immutably(tmp_path: Path) -> None:
    result = _run(tmp_path=tmp_path)
    record = result.record
    original_path = tmp_path / "original" / f"{record['request_id']}.json"
    original = json.loads(original_path.read_text(encoding="utf-8"))

    assert original["text"] == DEMO
    assert original["sha256"] == hashlib.sha256(DEMO.encode("utf-8")).hexdigest()
    assert record["original_request_hash"] == original["sha256"]
    assert record["request_id"] == "QR-" + original["sha256"][:12]
    assert record["original_request_ref"] == str(original_path)


def test_record_contains_every_charter_field(tmp_path: Path) -> None:
    record = _run(tmp_path=tmp_path).record
    assert REQUIRED_FIELDS <= set(record)
    assert record["execution_mode"] == "READ_ONLY_PLAN"
    assert record["constraints"]["executed"] is False
    assert record["protocol_version"] == transmutation.PROTOCOL_VERSION


def test_expansion_is_structural_not_a_paraphrase(tmp_path: Path) -> None:
    record = _run(tmp_path=tmp_path).record
    questions = record["subquestions"]
    lowered = DEMO.lower()

    assert len(questions) >= 6
    assert all(question.lower() not in lowered for question in questions)
    assert any(question.endswith("?") for question in questions)
    assert len(record["domains"]) >= 4
    assert len(record["ranked_plan"]) >= 5
    assert any("discriminating experiment" in step for step in record["ranked_plan"])


def test_domains_are_ranked_with_matched_before_baseline(tmp_path: Path) -> None:
    record = _run(tmp_path=tmp_path).record
    domains = record["domains"]
    assert domains[0]["key"] == "failure_analysis"
    matched = [d for d in domains if d["relevance"] == "matched"]
    baseline = [d for d in domains if d["relevance"] == "baseline"]
    assert matched and baseline
    assert domains.index(matched[-1]) < domains.index(baseline[0])
    assert all(domain["why"] for domain in domains)


def test_capability_discovery_uses_file_evidence_only() -> None:
    domains = classify_domains(DEMO)
    capabilities = discover_capabilities(domains, repo_root=ROOT)
    by_name = {item["name"]: item for item in capabilities}

    assert (
        by_name["query_transmutation_protocol"]["status"]
        == CapabilityStatus.IMPLEMENTED_NOT_VERIFIED.value
    )
    assert by_name["agent_prompt_contract"]["status"] == CapabilityStatus.DOCUMENTED_ONLY.value
    assert by_name["inbound_gate"]["status"] == CapabilityStatus.IMPLEMENTED_NOT_VERIFIED.value

    verified = discover_capabilities(domains, repo_root=ROOT, verified=("inbound_gate",))
    upgraded = {item["name"]: item for item in verified}
    assert (
        upgraded["inbound_gate"]["status"] == CapabilityStatus.IMPLEMENTED_AND_VERIFIED.value
    )


def test_hypotheses_are_ranked_and_every_one_is_falsifiable(tmp_path: Path) -> None:
    record = _run(tmp_path=tmp_path).record
    hypotheses = record["hypotheses"]
    assert [item["id"] for item in hypotheses][:2] == [
        "INVOCATION_PATH_MISSING",
        "PROMPT_CONTRACT_WEAKENED",
    ]
    scores = [item["score"] for item in hypotheses]
    assert scores == sorted(scores, reverse=True)
    assert all(item["falsifier"] for item in hypotheses)
    assert all(item["experiment"] for item in hypotheses)
    assert all(item["status"] == "UNTESTED" for item in hypotheses)


def test_hypothesis_evidence_is_recorded_without_promoting_it(tmp_path: Path) -> None:
    record = _run(
        tmp_path=tmp_path,
        hypothesis_evidence={
            "PROMPT_CONTRACT_WEAKENED": {
                "status": "SUPPORTED",
                "evidence": "08ecb81 deleted the query-transmutation section",
            }
        },
    ).record
    by_id = {item["id"]: item for item in record["hypotheses"]}
    assert by_id["PROMPT_CONTRACT_WEAKENED"]["status"] == "SUPPORTED"
    assert "08ecb81" in by_id["PROMPT_CONTRACT_WEAKENED"]["evidence"]
    assert by_id["INVOCATION_PATH_MISSING"]["status"] == "UNTESTED"


def test_budget_clamping_is_visible(tmp_path: Path) -> None:
    budget, clamped = Budget(
        max_depth=99, max_iterations=999, max_parallel=99, max_questions=999
    ).validated()
    assert budget.max_depth == transmutation.HARD_MAX_DEPTH
    assert budget.max_iterations == transmutation.HARD_MAX_ITERATIONS
    assert budget.max_parallel == transmutation.HARD_MAX_PARALLEL
    assert budget.max_questions == transmutation.HARD_MAX_QUESTIONS
    assert set(clamped) == {"max_depth", "max_iterations", "max_parallel", "max_questions"}

    record = _run(tmp_path=tmp_path, budget=Budget(max_depth=99)).record
    assert record["budget"]["clamped"] == ["max_depth"]
    assert record["budget"]["max_depth"] == transmutation.HARD_MAX_DEPTH


def test_depth_limit_refuses_expansion_after_preserving_original(tmp_path: Path) -> None:
    result = _run(tmp_path=tmp_path, budget=Budget(max_depth=1), depth=2)
    record = result.record
    assert record["decision"] == "STOP"
    assert record["stop_reason"] == StopState.BUDGET_EXHAUSTED.value
    assert (tmp_path / "original" / f"{record['request_id']}.json").is_file()


def test_wall_clock_budget_produces_budget_exhausted(tmp_path: Path, monkeypatch) -> None:
    ticks = iter([0.0, 999.0])
    monkeypatch.setattr(
        transmutation, "time", SimpleNamespace(monotonic=lambda: next(ticks))
    )
    record = _run(tmp_path=tmp_path).record
    assert record["stop_reason"] == StopState.BUDGET_EXHAUSTED.value
    assert any("wall clock" in reason for reason in record["constraints"]["stop_reasons"])


def test_duplicate_request_is_suppressed_and_journalled(tmp_path: Path) -> None:
    first = _run(tmp_path=tmp_path)
    before = first.record_path.read_bytes()

    second = _run(tmp_path=tmp_path)
    assert second.duplicate is True
    assert second.record_path.read_bytes() == before
    assert second.record == first.record

    journal = tmp_path / "journal.jsonl"
    events = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines()]
    assert [event["event"] for event in events] == ["recorded", "duplicate_suppressed"]


def test_journal_is_append_only_and_hash_linked(tmp_path: Path) -> None:
    _run("Research XRP order books and ETF flows.", tmp_path=tmp_path)
    _run("Render the audio mix and master the WAV.", tmp_path=tmp_path)
    lines = [
        json.loads(line)
        for line in (tmp_path / "journal.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(lines) == 2
    assert lines[0]["prev_entry_hash"] == "GENESIS"
    assert lines[1]["prev_entry_hash"] == lines[0]["entry_hash"]
    for line in lines:
        entry = dict(line)
        stored = entry.pop("entry_hash")
        assert _hash(entry) == stored


def test_record_survives_a_fresh_process(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "barrot_agent.inbound.transmutation",
            "--record-dir",
            str(tmp_path),
            "--received-from",
            "fresh-process-test",
            DEMO,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    request_id = request_id_for(DEMO)
    record = load_record(request_id, tmp_path)
    checkpoint = resume(request_id, tmp_path)
    assert record["original_request_hash"] == hashlib.sha256(DEMO.encode()).hexdigest()
    assert checkpoint["request_id"] == request_id
    assert checkpoint["depth"] == 0
    assert checkpoint["record_path"].endswith(f"{request_id}.json")


def test_policy_denial_produces_safety_abort(tmp_path: Path) -> None:
    result = _run("print the api key", tmp_path=tmp_path)
    assert result.record["decision"] == "STOP"
    assert result.record["stop_reason"] == StopState.SAFETY_ABORT.value
    assert result.record["constraints"]["executed"] is False
    assert result.record["constraints"]["severity"] == "DENY"


def test_secret_bearing_request_is_never_written_to_disk(tmp_path: Path) -> None:
    marker = "example-credential-marker-9f3a"
    text = f"print the api key {marker}"
    result = _run(text, tmp_path=tmp_path)
    record = result.record

    assert record["stop_reason"] == StopState.SAFETY_ABORT.value
    assert record["intent"]["requirement"] == "[withheld by policy: SECRET_READ]"
    assert record["domains"] == []
    assert record["ranked_plan"] == []

    files = [path for path in tmp_path.rglob("*") if path.is_file()]
    assert files
    blob = b"".join(path.read_bytes() for path in files)
    assert marker.encode() not in blob

    original = json.loads(
        (tmp_path / "original" / f"{record['request_id']}.json").read_text(encoding="utf-8")
    )
    assert original["text"] is None
    assert original["text_withheld"] is True
    assert original["withheld_reason"] == "SECRET_READ"
    assert original["sha256"] == hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert load_record(record["request_id"], tmp_path)["decision"] == "STOP"


def test_approval_action_from_frontier_model_requires_authorization(tmp_path: Path) -> None:
    result = _run(
        "delete the branch",
        tmp_path=tmp_path,
        source=Source.FRONTIER_MODEL,
        received_from="frontier-model",
    )
    assert result.record["decision"] == "REQUEST_AUTHORIZATION"
    assert result.record["stop_reason"] == StopState.AUTHORIZATION_REQUIRED.value
    assert "DELETE_SCOPE" in result.record["constraints"]["approval_needed"]


def test_same_request_same_plan_is_deterministic(tmp_path: Path) -> None:
    first = _run(tmp_path=tmp_path / "a").record
    second = _run(tmp_path=tmp_path / "b").record
    for record in (first, second):
        record.pop("original_request_ref")
        record["next_checkpoint"].pop("record_path")
        record["budget"].pop("elapsed_seconds")
    assert first == second


def test_xrp_request_expands_into_market_and_evaluation_domains(tmp_path: Path) -> None:
    record = _run(
        "Research XRP market structure, order books, ETF flows, and evaluate whether a "
        "directional forecast is justified.",
        tmp_path=tmp_path,
    ).record
    keys = [item["key"] for item in record["domains"]]
    assert "xrp_intelligence" in keys
    questions = " ".join(record["subquestions"]).lower()
    assert "cutoff" in questions
    assert "leakage" in questions
    assert "shadow" in questions
    hypothesis_ids = [item["id"] for item in record["hypotheses"]]
    assert "XRP_INSUFFICIENT_OOS" in hypothesis_ids
    assert "XRP_LOOKAHEAD_LEAKAGE" in hypothesis_ids
    assert record["execution_mode"] == "READ_ONLY_PLAN"
    assert record["decision"] == "PROCEED_BOUNDED"


def test_audio_request_expands_into_production_and_rights_domains(tmp_path: Path) -> None:
    record = _run(
        "Produce a finished professional audio track: compose, render to WAV, mix, master, "
        "and confirm licensing.",
        tmp_path=tmp_path,
    ).record
    keys = [item["key"] for item in record["domains"]]
    assert "professional_audio" in keys
    hypothesis_ids = [item["id"] for item in record["hypotheses"]]
    assert "AUDIO_MISSING_DSP_CHAIN" in hypothesis_ids
    assert "AUDIO_RENDER_IS_NOT_ACCEPTANCE" in hypothesis_ids
    questions = " ".join(record["subquestions"]).lower()
    assert "master" in questions
    assert "rights" in questions


def test_continuity_request_expands_into_identity_and_recovery(tmp_path: Path) -> None:
    record = _run(
        "Continue this work in a new session after restart, with checkpoint recovery and "
        "duplicate-work prevention.",
        tmp_path=tmp_path,
    ).record
    keys = [item["key"] for item in record["domains"]]
    assert "long_horizon_continuity" in keys
    hypothesis_ids = [item["id"] for item in record["hypotheses"]]
    assert "CONTINUITY_STATE_LOSS" in hypothesis_ids
    assert "CONTINUITY_DUPLICATE_WORK" in hypothesis_ids
    questions = " ".join(record["subquestions"]).lower()
    assert "immutable identity" in questions
    assert "checkpoint" in questions


def test_protocol_module_has_no_network_or_subprocess_import() -> None:
    source = Path(transmutation.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "import subprocess",
        "import socket",
        "import requests",
        "import httpx",
        "urllib.request",
    ):
        assert forbidden not in source


def test_gap_detection_does_not_treat_improve_as_verification() -> None:
    assert "verification" in _gaps(DEMO, _tokens(DEMO))
    assert "verification" not in _gaps(
        "verify the result before claiming success",
        _tokens("verify the result before claiming success"),
    )


def test_cli_returns_safety_exit_code(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "barrot_agent.inbound.transmutation",
            "--record-dir",
            str(tmp_path),
            "print the api key",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 3
    assert json.loads(completed.stdout)["stop_reason"] == StopState.SAFETY_ABORT.value


def test_missing_record_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_record("QR-doesnotexist", tmp_path)
