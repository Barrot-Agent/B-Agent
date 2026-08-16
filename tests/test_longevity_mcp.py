"""Tests for the read-only longevity MCP facade."""

from __future__ import annotations

from longevity_mcp import LongevityMCPServer


def test_resources_are_scoped_and_metadata_is_complete():
    server = LongevityMCPServer(source_citations=["paper:doi/example"])
    assert "longevity_unified" in server.list_resources()
    result = server.read_resource("longevity_unified")
    metadata = result["metadata"]
    assert metadata["read_only"] is True
    assert metadata["timestamp"]
    assert metadata["source_citations"]
    assert "real-person" not in str(result["data"])


def test_ingestion_is_deidentified_and_not_persisted():
    server = LongevityMCPServer()
    result = server.call_tool(
        "ingest_research",
        paper_text="Yamanaka factors improved epigenetic age.",
        trial_records=[
            {
                "participant_id": "real-person",
                "name": "Private Person",
                "consented": True,
                "treatment_arm": "OSKM",
                "baseline_epigenetic_age": 60,
                "followup_epigenetic_age": 55,
            }
        ],
        source_citations=["doi:10.0000/example"],
    )
    data = result["data"]
    assert data["trial_outcomes"][0]["participant_id"] != "real-person"
    assert "Private Person" not in str(data)
    assert result["metadata"]["cohort_size"] == 1
    assert result["metadata"]["confidence"] > 0


def test_consent_and_writes_are_blocked():
    server = LongevityMCPServer()
    try:
        server.call_tool(
            "track_biomarker",
            participant_id="p1",
            biomarker="nad_plus",
            measurements=[],
        )
    except PermissionError:
        pass
    else:
        raise AssertionError("tracking without consent must be rejected")

    try:
        server.call_tool("write_dataset")
    except PermissionError:
        pass
    else:
        raise AssertionError("write tools must require approval")


def test_signal_detection_includes_safety_warning():
    server = LongevityMCPServer()
    result = server.call_tool(
        "detect_signals",
        trial_records=[
            {
                "participant_id": "p1",
                "consented": True,
                "treatment_arm": "OSKM",
                "age_reversal": 5,
            }
        ],
    )
    assert result["metadata"]["safety_warnings"]
