"""The bounty API probe must record what answered, not what we hoped would answer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.bounty_api_probe import AMOUNT_KEYS, PROBES

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "money" / "bounty_apis.json"
DOC = ROOT / "docs" / "money" / "BOUNTY-APIS.md"


def load() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def test_every_probe_is_recorded_with_a_status_and_body_head():
    data = load()
    urls = {record["url"] for record in data["probes"]}
    for _, url in PROBES:
        assert url in urls
    for record in data["probes"]:
        assert isinstance(record["status"], int)
        assert "body_head" in record
        assert record["verdict"] in {"amount_source", "no_amount", "unreachable"}


def test_no_endpoint_is_claimed_as_an_amount_source_without_json_amounts():
    data = load()
    for record in data["probes"]:
        if record["verdict"] != "amount_source":
            continue
        assert "json" in record["content_type"], record["url"]
        assert any(f'"{key}"' in record["body_head"].lower() for key in AMOUNT_KEYS), record["url"]


def test_measured_zero_amount_sources_is_stated():
    data = load()
    assert data["amount_sources"] == []
    assert "Amount sources found: 0 of 9." in DOC.read_text(encoding="utf-8")


def test_doc_quotes_the_same_status_codes_as_the_record():
    doc = DOC.read_text(encoding="utf-8")
    for record in load()["probes"]:
        bare = record["url"].split("://", 1)[-1]
        assert bare in doc, record["url"]
        assert f"| {record['status']} |" in doc, (record["url"], record["status"])


def test_doc_separates_absence_of_answer_from_absence_of_bounties():
    doc = DOC.read_text(encoding="utf-8")
    assert "Does not prove" in doc
    assert "no bounties" in doc
    assert "amount is only reported when a bounty word and a number sit on the same line" in doc
