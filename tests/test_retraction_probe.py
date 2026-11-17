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


def test_validation_flags_a_claims_record_that_cites_a_retracted_doi(tmp_path):
    """Iteration 4: the probe is called by validation, not by memory."""
    import scripts.re_v2 as re_v2

    claims = {
        "records": [
            {
                "id": "cites-retracted",
                "status": "Q",
                "affirmed": True,
                "excluded_from_evidence": False,
                "exclusion_reason": "",
                "quotes": ["a quote"],
                "evidence": {
                    "identifier": "10.1177/1758835919874651",
                    "abstract": "a quote inside this abstract",
                    "http_status": 200,
                },
            }
        ]
    }
    path = tmp_path / "claims.json"
    path.write_text(json.dumps(claims), encoding="utf-8")
    problems = re_v2.validate(path)
    assert any("retracted source" in problem for problem in problems), problems


def test_validation_does_not_flag_a_control_doi(tmp_path):
    import scripts.re_v2 as re_v2

    claims = {
        "records": [
            {
                "id": "cites-control",
                "status": "Q",
                "affirmed": True,
                "excluded_from_evidence": False,
                "exclusion_reason": "",
                "quotes": ["a quote"],
                "evidence": {
                    "identifier": "10.1137/0204037",
                    "abstract": "a quote inside this abstract",
                    "http_status": 200,
                },
            }
        ]
    }
    path = tmp_path / "claims.json"
    path.write_text(json.dumps(claims), encoding="utf-8")
    assert re_v2.validate(path) == []


def test_stored_claims_files_are_clean_against_the_denylist():
    from scripts.re_v2 import validate

    for path in sorted((ROOT / "data").rglob("claims/*.json")):
        assert validate(path) == [], path



def _write_claims_for_retraction_validation(tmp_path, identifier: str) -> Path:
    claims = {
        "records": [
            {
                "id": "retraction-validation-case",
                "status": "Q",
                "affirmed": True,
                "excluded_from_evidence": False,
                "exclusion_reason": "",
                "quotes": ["a quote"],
                "evidence": {
                    "identifier": identifier,
                    "abstract": "a quote inside this abstract",
                    "http_status": 200,
                },
            }
        ]
    }
    path = tmp_path / "claims.json"
    path.write_text(json.dumps(claims), encoding="utf-8")
    return path


def test_validation_fails_closed_when_retraction_denylist_is_missing(tmp_path, monkeypatch):
    import scripts.re_v2 as re_v2

    path = _write_claims_for_retraction_validation(tmp_path, "10.1137/0204037")
    monkeypatch.setattr(re_v2, "DENYLIST", tmp_path / "missing.json")
    problems = re_v2.validate(path)
    assert any("retraction denylist unavailable" in item for item in problems)
    assert any("missing retracted_dois.json" in item for item in problems)


def test_validation_fails_closed_when_retraction_denylist_is_malformed(tmp_path, monkeypatch):
    import scripts.re_v2 as re_v2

    path = _write_claims_for_retraction_validation(tmp_path, "10.1137/0204037")
    denylist = tmp_path / "retracted_dois.json"
    denylist.write_text("{", encoding="utf-8")
    monkeypatch.setattr(re_v2, "DENYLIST", denylist)
    problems = re_v2.validate(path)
    assert any("retraction denylist unavailable" in item for item in problems)
    assert any("cannot read retracted_dois.json" in item for item in problems)


def test_validation_fails_closed_when_retraction_denylist_omits_verified_fixture_doi(tmp_path, monkeypatch):
    import scripts.re_v2 as re_v2

    path = _write_claims_for_retraction_validation(tmp_path, "10.1137/0204037")
    denylist = tmp_path / "retracted_dois.json"
    denylist.write_text(json.dumps({"retracted": []}), encoding="utf-8")
    monkeypatch.setattr(re_v2, "DENYLIST", denylist)
    problems = re_v2.validate(path)
    assert any("does not cover verified fixture DOIs" in item for item in problems)


def test_validation_normalizes_doi_urls_before_retraction_comparison(tmp_path):
    import scripts.re_v2 as re_v2

    path = _write_claims_for_retraction_validation(
        tmp_path, "https://doi.org/10.1177/1758835919874651"
    )
    problems = re_v2.validate(path)
    assert any("retracted source" in item for item in problems), problems
