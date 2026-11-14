import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T174430Z-sbic-west-chatgpt-event-status-correction.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_west_is_only_an_announced_scheduled_event_without_completion_evidence():
    data = load()
    west = data["corrected_event_status"]["sbic_west"]
    assert west == "ANNOUNCED_SCHEDULED_EVENT; ACTUAL_OCCURRENCE_NOT_INDEPENDENTLY_VERIFIED"
    assert "That the seminar actually took place" in data["source_registry"][0]["what_it_does_not_establish"][0]


def test_east_page_marks_course_ended_but_does_not_prove_attendance_or_partnership():
    data = load()
    east = data["corrected_event_status"]["sbic_east"]
    assert east == "OFFICIAL_PAGE_MARKS_COURSE_ENDED; INDIVIDUAL_ATTENDANCE_NOT_VERIFIED"
    assert "marks the course as ended" in data["source_registry"][1]["what_it_establishes"][0]
    assert "An OpenAI partnership" in data["source_registry"][1]["what_it_does_not_establish"][1]


def test_event_status_correction_is_append_only_and_model_ineligible():
    data = load()
    assert data["supersedes_artifact_id"] == "sbic_japan_chatgpt_primary_source_reconciliation_20261105T173711Z"
    assert data["source_capture_policy"]["model_eligible"] is False
