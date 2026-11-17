"""End-to-end wiring test: every cross-domain link resolves.

One command proves the parts of the repo still talk to each other:
runtime config, sync config, mirror copy, flight recorder, registry, docs index.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from barrot_agent.flight_recorder import REQUIRED_FIELDS, load_records
from scripts.cross_domain_audit import KNOWN_BREAKS, audit


def test_all_links_resolve_or_are_documented():
    report = audit()
    assert report["breaking"] == [], report
    assert report["ok"] is True


def test_recorder_records_are_machine_readable():
    records, breaks = load_records()
    assert breaks == []
    assert records, "recorder should hold at least one record"
    for record in records:
        for name in REQUIRED_FIELDS:
            assert name in record


def test_known_breaks_carry_a_reason():
    assert KNOWN_BREAKS
    for link, reason in KNOWN_BREAKS.items():
        assert reason.strip(), link
