"""Tests for the witness loop (V2). Every state must be reachable and every
refusal must actually refuse."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import witness_loop as wl  # noqa: E402


def claim(rule_id="R1", task="smallest task"):
    return wl.Claim(rule_id=rule_id, source_domain="music", target_domain="rendering", task=task)


def test_claim_requires_witness(tmp_path):
    with pytest.raises(wl.EvidenceRequired):
        wl.record(claim(), None, tmp_path / "ledger.jsonl")


def test_flipped_witness_is_supported(tmp_path):
    c = claim()
    w = wl.ablate(c, lambda has_rule: has_rule)
    assert w.with_rule is True and w.without_rule is False and w.flipped is True

    recorded = wl.record(c, w, tmp_path / "ledger.jsonl")
    assert recorded["state"] == wl.SUPPORTED
    assert wl.verify_ledger(tmp_path / "ledger.jsonl")


def test_unflipped_witness_is_refuted_but_recorded(tmp_path):
    c = claim()
    w = wl.ablate(c, lambda has_rule: True)  # succeeds either way
    recorded = wl.record(c, w, tmp_path / "ledger.jsonl")

    assert recorded["state"] == wl.REFUTED
    assert len(wl.read_ledger(tmp_path / "ledger.jsonl")) == 1


def test_rule_that_hurts_is_contradicted(tmp_path):
    c = claim()
    w = wl.ablate(c, lambda has_rule: not has_rule)
    recorded = wl.record(c, w, tmp_path / "ledger.jsonl")
    assert recorded["state"] == wl.CONTRADICTED


def test_witness_for_another_rule_is_refused(tmp_path):
    c = claim("R1")
    w = wl.ablate(claim("R2"), lambda has_rule: has_rule)
    with pytest.raises(wl.EvidenceRequired, match="witness is for rule"):
        wl.record(c, w, tmp_path / "ledger.jsonl")


def test_witness_for_another_task_is_refused(tmp_path):
    c = claim("R1", task="task A")
    w = wl.ablate(claim("R1", task="task B"), lambda has_rule: has_rule)
    with pytest.raises(wl.EvidenceRequired, match="different task"):
        wl.record(c, w, tmp_path / "ledger.jsonl")


def test_chain_links_records(tmp_path):
    path = tmp_path / "ledger.jsonl"
    first = wl.record(claim("R1"), wl.ablate(claim("R1"), lambda h: h), path)
    second = wl.record(claim("R2"), wl.ablate(claim("R2"), lambda h: True), path)

    assert first["prev_sha256"] == wl.GENESIS
    assert second["prev_sha256"] == first["record_sha256"]
    assert wl.verify_ledger(path)


def test_tampered_record_is_detected(tmp_path):
    path = tmp_path / "ledger.jsonl"
    wl.record(claim("R1"), wl.ablate(claim("R1"), lambda h: h), path)

    record = json.loads(path.read_text().splitlines()[0])
    record["state"] = wl.REFUTED  # flip the verdict without recomputing the hash
    path.write_text(json.dumps(record) + "\n")

    assert wl.verify_ledger(path) is False


def test_assert_supported_fails_closed(tmp_path):
    path = tmp_path / "ledger.jsonl"
    wl.record(claim("R1"), wl.ablate(claim("R1"), lambda h: True), path)  # REFUTED

    with pytest.raises(wl.EvidenceRequired, match="no SUPPORTED witness"):
        wl.assert_supported(path, "R1")

    with pytest.raises(wl.EvidenceRequired):
        wl.assert_supported(path, "R-unknown")


def test_deterministic_runner_gives_identical_witness(tmp_path):
    c = claim()
    first = wl.ablate(c, lambda has_rule: has_rule)
    second = wl.ablate(c, lambda has_rule: has_rule)

    assert first.rule_id == second.rule_id
    assert first.task_sha256 == second.task_sha256
    assert first.flipped == second.flipped
