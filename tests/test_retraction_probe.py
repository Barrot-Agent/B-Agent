"""Retraction probe: the fixture set, the direction of the relation, and the guard."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.retraction_probe as probe_module
from scripts.retraction_probe import check, notices_for, probe

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "data" / "research" / "retraction_fixtures.json"


def test_probe_reports_retracted_when_a_notice_names_the_doi():
    lookup = lambda doi: [{"notice_doi": "10.1/notice", "notice_title": "Retraction", "update_type": "retraction"}]
    result = probe("10.1/original", notice_lookup=lookup)
    assert result["retracted"] is True
    assert result["notices"][0]["notice_doi"] == "10.1/notice"


def test_probe_reports_clean_when_no_notice_exists():
    result = probe("10.1/clean", notice_lookup=lambda doi: [])
    assert result["retracted"] is False
    assert result["notices"] == []


def test_notice_pointing_at_another_doi_is_not_counted(monkeypatch):
    payload = {
        "message": {
            "items": [
                {
                    "DOI": "10.1/notice",
                    "title": ["Retraction: something else"],
                    "update-to": [{"type": "retraction", "DOI": "10.1/some-other-paper"}],
                }
            ]
        }
    }
    monkeypatch.setattr(probe_module, "fetch_json", lambda url, attempts=3: payload)
    assert notices_for("10.1/target") == []


def test_notice_with_the_right_doi_is_counted(monkeypatch):
    payload = {
        "message": {
            "items": [
                {
                    "DOI": "10.1/notice",
                    "title": ["Retraction: target"],
                    "update-to": [{"type": "retraction", "DOI": "10.1/target"}],
                }
            ]
        }
    }
    monkeypatch.setattr(probe_module, "fetch_json", lambda url, attempts=3: payload)
    found = notices_for("10.1/target")
    assert len(found) == 1
    assert found[0]["update_type"] == "retraction"


def test_non_retraction_updates_do_not_count(monkeypatch):
    payload = {
        "message": {
            "items": [
                {
                    "DOI": "10.1/correction",
                    "title": ["Correction"],
                    "update-to": [{"type": "correction", "DOI": "10.1/target"}],
                }
            ]
        }
    }
    monkeypatch.setattr(probe_module, "fetch_json", lambda url, attempts=3: payload)
    assert notices_for("10.1/target") == []


def test_stored_fixture_set_is_consistent_and_passes_check():
    payload = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(payload["entries"]) == 6
    assert payload["summary"] == {
        "retracted_expected": 4,
        "controls": 2,
        "retracted_detected": 4,
        "controls_clear": 2,
    }
    for entry in payload["entries"]:
        if entry["expected"] == "retracted":
            assert entry["notices"], entry["doi"]
            assert all(n["update_type"].lower() == "retraction" for n in entry["notices"])
        else:
            assert entry["notices"] == [], entry["doi"]
    assert check() == 0
