from __future__ import annotations

import json
from pathlib import Path

import pytest

from barrot_agent.ingestion.mmi_contract import MMI_MAX_DEPTH
from barrot_agent.sources.mmi_adapter import (
    ADAPTER_VERSION,
    PlannerMMIAdapter,
)
from barrot_agent.sources.source_acquisition import AcquisitionTarget


def make_target(
    target_id="target-1",
    need_id="need-1",
    *,
    discovery_uri="https://example.org/discovery",
    acquisition_uri="https://example.org/data",
):
    return AcquisitionTarget(
        target_id=target_id,
        need_id=need_id,
        source_type="dataset",
        name="Example Dataset",
        purpose="MMI adapter integration test",
        discovery_uri=discovery_uri,
        acquisition_uri=acquisition_uri,
        publisher="Example Publisher",
        provenance_requirements=[
            "publisher",
            "retrieval_timestamp",
        ],
        verification_requirements=[
            "hash",
        ],
        mmi_required=True,
        independent_corroboration_required=True,
    )


def test_direct_target_conversion_requires_no_planner():
    target = make_target()

    request = PlannerMMIAdapter().build_request(target)

    assert request.target_id == "target-1"
    assert request.need_id == "need-1"
    assert request.source_uri == "https://example.org/data"


def test_acquisition_uri_has_priority_over_discovery_uri():
    target = make_target(
        acquisition_uri="https://example.org/acquire",
        discovery_uri="https://example.org/discover",
    )

    request = PlannerMMIAdapter().build_request(target)

    assert request.source_uri == "https://example.org/acquire"


def test_discovery_uri_is_fallback():
    target = make_target(
        acquisition_uri=None,
        discovery_uri="https://example.org/discover",
    )

    request = PlannerMMIAdapter().build_request(target)

    assert request.source_uri == "https://example.org/discover"


def test_unresolved_target_uses_explicit_internal_marker():
    target = make_target(
        acquisition_uri=None,
        discovery_uri=None,
    )

    request = PlannerMMIAdapter().build_request(target)

    assert request.source_uri == (
        "acquisition-target://target-1"
    )


def test_actual_planner_fields_are_preserved():
    target = make_target()

    request = PlannerMMIAdapter().build_request(target)

    assert request.source_type == "dataset"
    assert request.name == "Example Dataset"
    assert request.purpose == "MMI adapter integration test"
    assert request.publisher == "Example Publisher"
    assert request.provenance_requirements == [
        "publisher",
        "retrieval_timestamp",
    ]
    assert request.verification_requirements == ["hash"]
    assert request.mmi_required is True
    assert request.independent_corroboration_required is True


def test_mmi_depth_limits_are_canonical():
    request = PlannerMMIAdapter().build_request(
        make_target("target-2", "need-2")
    )

    assert request.max_component_depth == 4
    assert request.max_provenance_depth == 4
    assert request.max_component_depth == MMI_MAX_DEPTH
    assert request.max_provenance_depth == MMI_MAX_DEPTH


def test_request_hash_is_deterministic():
    target = make_target()

    adapter = PlannerMMIAdapter()

    first = adapter.build_request(target)
    second = adapter.build_request(target)

    assert first.content_hash() == second.content_hash()


def test_export_is_persisted(tmp_path: Path):
    request = PlannerMMIAdapter().build_request(
        make_target("target-export", "need-export")
    )

    path = PlannerMMIAdapter().export_request(
        request,
        tmp_path,
    )

    assert path.exists()

    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    assert payload["adapter_version"] == ADAPTER_VERSION
    assert payload["request_hash"] == request.content_hash()
    assert payload["request"]["target_id"] == "target-export"


def test_non_target_is_rejected_without_planner_error():
    with pytest.raises(
        TypeError,
        match="AcquisitionTarget",
    ):
        PlannerMMIAdapter().build_request(object())


def test_lookup_requires_explicit_planner():
    with pytest.raises(
        RuntimeError,
        match="explicit.*SourceAcquisitionPlanner",
    ):
        PlannerMMIAdapter().build_request_by_id("missing")
