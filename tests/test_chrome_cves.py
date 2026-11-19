"""Governance tests for the CVE evidence directory.

The rule this file enforces: a CVE ID may exist in this repo only if it has a
record that was fetched from an authoritative source and hashed. A number in
prose with no record behind it is exactly the failure mode this whole track is
supposed to avoid.

The record is deliberately explicit about what it does NOT contain. A verified
CVE record is not a patch diff, not a PoC, and not an analysis. The tests below
assert that the records keep saying so.
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CVE_DIR = ROOT / "sandbox/chrome/cves"
RECORDS = sorted(CVE_DIR.glob("CVE-*.json"))
CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,}")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_three_records_exist():
    assert len(RECORDS) == 3, f"expected 3 verified records, found {[p.name for p in RECORDS]}"


@pytest.mark.parametrize("path", RECORDS, ids=lambda p: p.stem)
def test_filename_matches_record(path):
    record = load(path)
    assert path.stem == record["cve_id"]
    assert CVE_PATTERN.fullmatch(record["cve_id"])


@pytest.mark.parametrize("path", RECORDS, ids=lambda p: p.stem)
def test_record_is_published_and_assigned_by_chrome(path):
    record = load(path)
    assert record["state"] == "PUBLISHED"
    assert record["assigner"] == "Chrome"
    # The CNA encodes the product as vendor "Google" + product "Chrome", not
    # as the single string "Google Chrome" that the description uses.
    assert record["vendor"] == "Google"
    assert record["product"] == "Chrome"


@pytest.mark.parametrize("path", RECORDS, ids=lambda p: p.stem)
def test_fixed_version_is_usable(path):
    """Either the structured field has a version, or the description does.

    CVE-2020-6418 is the interesting case: its structured version field is
    literally "unspecified", so the only usable version is in the prose. That is
    a property of the published record, not a defect in the fetch, and an
    analysis that trusts the field blindly would cite nothing.
    """
    record = load(path)
    version = record["fixed_version"]
    if version == "unspecified":
        assert re.search(r"prior to (\d+\.\d+\.\d+\.\d+)", record["description"])
    else:
        assert re.fullmatch(r"\d+\.\d+\.\d+\.\d+", version), version
        assert "prior to" in record["description"]


@pytest.mark.parametrize("path", RECORDS, ids=lambda p: p.stem)
def test_verification_block_is_complete(path):
    v = load(path)["verification"]
    assert v["http_status"] == 200
    assert v["url"].startswith("https://raw.githubusercontent.com/")
    assert "cvelistV5" in v["source"]
    assert re.fullmatch(r"[0-9a-f]{64}", v["payload_sha256"])
    assert v["payload_bytes"] > 1000
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", v["fetched_at_utc"])


@pytest.mark.parametrize("path", RECORDS, ids=lambda p: p.stem)
def test_record_does_not_claim_artifacts_it_does_not_have(path):
    record = load(path)
    assert record["artifacts"] == {"patch_diff": None, "poc": None, "variant": None}
    assert "UNRESOLVED" in record["analysis_status"]


@pytest.mark.parametrize("path", RECORDS, ids=lambda p: p.stem)
def test_record_has_upstream_references(path):
    refs = load(path)["references"]
    assert len(refs) >= 2
    # The first reference in every Chrome advisory record is the release note.
    assert refs[0].startswith("https://chromereleases.googleblog.com/")
    # Some third-party mirrors are plain http; only the primary ref must be https.
    assert sum(url.startswith("https://") for url in refs) >= len(refs) - 1


def test_all_three_cves_are_distinct():
    ids = [load(p)["cve_id"] for p in RECORDS]
    assert len(set(ids)) == 3


def test_the_published_facts_are_the_ones_the_analysis_relies_on():
    by_id = {load(p)["cve_id"]: load(p) for p in RECORDS}
    assert "Type confusion in V8" in by_id["CVE-2020-6418"]["description"]
    assert "Type Confusion in WebAssembly" in by_id["CVE-2024-2887"]["description"]
    assert "Heap buffer overflow in WebRTC" in by_id["CVE-2023-7024"]["description"]


def test_no_unverified_cve_id_appears_in_reverse_engineering_notes():
    """Every CVE ID in the main analysis doc must have a hashed record."""
    verified = {load(p)["cve_id"] for p in RECORDS}
    text = (ROOT / "REVERSE_ENGINEERED_BUGS.md").read_text(encoding="utf-8")
    cited = set(CVE_PATTERN.findall(text))
    assert cited <= verified, f"unverified IDs cited: {sorted(cited - verified)}"


def test_cve_records_make_no_network_calls():
    """Evidence is fetched once and stored; tests must work offline."""
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & {"socket", "urllib", "ssl", "requests", "http", "httpx"})
