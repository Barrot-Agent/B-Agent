from data.animal_research import (
    ReviewQueue,
    cross_reference,
    merge_versions,
    normalize_record,
    search_records,
)


def _record(**overrides):
    record = {
        "title": "Dolphin signature whistle study",
        "species": ["Tursiops truncatus"],
        "study_context": "controlled communication experiment",
        "communication_method": ["signature whistles"],
        "observations": ["whistles changed after separation"],
        "findings": ["whistles identify individuals"],
        "uncertainty": ["intent remains uncertain"],
        "provenance": {"source_url": "https://doi.org/10.1234/example", "license": "CC-BY"},
        "ethics_approval": {"status": "approved", "protocol": "A-1"},
        "reproducibility": {"status": "replicated"},
        "study_design": "controlled",
        "status": "draft",
    }
    record.update(overrides)
    return record


def test_normalize_and_merge_versions():
    first = normalize_record(_record(version=1))
    second = normalize_record(_record(version=2, findings=["whistles identify individuals", "not food calls"]))
    assert first["record_id"] == second["record_id"]
    assert merge_versions([first, second])[0]["version"] == 2


def test_cross_reference_flags_opposing_findings():
    positive = normalize_record(_record())
    negative = normalize_record(_record(title="Follow-up", findings=["whistles do not identify individuals"]))
    result = cross_reference([positive, negative])
    assert result["contradictions"]


def test_review_gate_and_local_search():
    record = normalize_record(_record())
    queue = ReviewQueue([record])
    queue.approve(record["record_id"], "researcher")
    assert len(queue.publishable()) == 1
    assert search_records("dolphin whistles", queue.publishable())
