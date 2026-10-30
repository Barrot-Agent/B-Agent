from __future__ import annotations

import pytest

from barrot_agent.mmi import (
    AcquisitionManifest,
    CompletenessReport,
    ContractError,
    DatasetTarget,
    EvidenceOrigin,
    FreshnessPolicy,
    Interpretation,
    Observation,
    ParsabilityState,
    ParseCoverage,
    ScopeDeclaration,
    SourceLineage,
    SourceLocation,
)

DIGEST = "a" * 64


def scope() -> ScopeDeclaration:
    return ScopeDeclaration(included=("abstract", "body", "references"))


def test_scope_requires_four_depths_and_bounded_resources() -> None:
    with pytest.raises(ContractError):
        ScopeDeclaration(included=("all",), component_depth=3)
    with pytest.raises(ContractError):
        ScopeDeclaration(included=("all",), max_nodes=0)


def test_target_requires_explicit_identity_and_supported_uri() -> None:
    DatasetTarget("paper-1", "https://example.org/paper", scope())
    with pytest.raises(ContractError):
        DatasetTarget("paper-2", "ftp://example.org/paper", scope())


def test_acquisition_manifest_binds_actual_content_digest_and_size() -> None:
    record = AcquisitionManifest(
        execution_id="exec-1", target_id="paper-1",
        source_uri="https://example.org/paper", retrieved_at="2026-10-30T00:00:00Z",
        content_sha256=DIGEST, byte_count=100, license="CC-BY-4.0",
    )
    assert record.content_sha256 == DIGEST
    with pytest.raises(ContractError):
        AcquisitionManifest(
            execution_id="exec-1", target_id="paper-1",
            source_uri="https://example.org/paper", retrieved_at="now",
            content_sha256="sha256:" + DIGEST, byte_count=100, license="unknown",
        )


def test_complete_parse_cannot_hide_dropped_or_unsupported_content() -> None:
    ParseCoverage("pdf-v1", ParsabilityState.PARTIAL, 8, 10, ("table-2",))
    with pytest.raises(ContractError):
        ParseCoverage("pdf-v1", ParsabilityState.COMPLETE, 10, 10, dropped_ranges=("appendix",))


def test_observation_and_interpretation_are_separate_and_linked() -> None:
    observation = Observation(
        "obs-1", DIGEST, "Observed value: 42",
        SourceLocation("page:2", start_offset=10, end_offset=28),
    )
    interpretation = Interpretation("int-1", (observation.observation_id,), "rule-engine", "1.0", "value is 42")
    assert interpretation.observation_ids == ("obs-1",)
    assert observation.raw_value.startswith("Observed")


def test_barrot_generated_origin_is_explicit() -> None:
    generated = Observation(
        "obs-generated", DIGEST, "generated summary",
        SourceLocation("artifact:summary.md"),
        origin=EvidenceOrigin.BARROT_GENERATED,
    )
    assert generated.origin is EvidenceOrigin.BARROT_GENERATED


def test_lineage_carries_publisher_owner_and_syndication() -> None:
    lineage = SourceLineage(
        "source-b", publisher_id="publisher-a", owner_id="owner-a",
        syndicated_from="source-a", content_sha256=DIGEST,
    )
    assert lineage.syndicated_from == "source-a"


def test_freshness_policy_is_ordered_and_completeness_is_two_dimensional() -> None:
    FreshnessPolicy(3600, 86400)
    report = CompletenessReport(
        protocol_complete=True, knowledge_complete=False,
        required_scope_units=10, parsed_scope_units=10,
        unresolved_gaps=("independent corroboration",),
    )
    assert report.protocol_complete and not report.knowledge_complete
    with pytest.raises(ContractError):
        CompletenessReport(True, True, 10, 10, unresolved_gaps=("gap",))
