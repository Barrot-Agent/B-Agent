"""
Tests for the Millennium reasoning orchestration module.
"""

from __future__ import annotations

from barrot_agent.millennium_reasoning import (
    CapabilityTargets,
    FormalArtifact,
    KnowledgeAsset,
    MillenniumReasoningEngine,
)


def test_capability_target_evaluation() -> None:
    engine = MillenniumReasoningEngine(
        CapabilityTargets(
            formal_proof_success_rate=0.3,
            conjecture_generation_quality=0.5,
            citation_reliability=0.9,
            cross_domain_transfer_score=0.4,
            assist_discovery_target=0.7,
            machine_checkable_target=0.25,
        )
    )
    result = engine.evaluate_capability_progress(
        {
            "formal_proof_success_rate": 0.31,
            "conjecture_generation_quality": 0.8,
            "citation_reliability": 0.95,
            "cross_domain_transfer_score": 0.42,
            "assist_discovery_target": 0.72,
            "machine_checkable_target": 0.3,
        }
    )
    assert result["all_targets_met"] is True
    assert result["score"] == 1.0


def test_retrieve_grounded_prioritizes_peer_reviewed() -> None:
    engine = MillenniumReasoningEngine()
    engine.register_knowledge_asset(
        KnowledgeAsset(
            asset_id="a1",
            title="Low confidence non-peer source",
            source_url="https://example.com/a1",
            source_class="paper",
            peer_reviewed=False,
            published_on="2026-01-01",
            confidence=0.4,
            tags=["riemann"],
        )
    )
    engine.register_knowledge_asset(
        KnowledgeAsset(
            asset_id="a2",
            title="Peer reviewed source",
            source_url="https://example.com/a2",
            source_class="paper",
            peer_reviewed=True,
            published_on="2026-01-02",
            confidence=0.7,
            tags=["riemann"],
        )
    )
    results = engine.retrieve_grounded(query="riemann", tags=["riemann"], min_confidence=0.3, limit=2)
    assert len(results) == 2
    assert results[0].asset_id == "a2"


def test_assess_claim_requires_three_source_classes() -> None:
    engine = MillenniumReasoningEngine()
    engine.register_knowledge_asset(
        KnowledgeAsset(
            asset_id="paper1",
            title="Published paper",
            source_url="https://example.com/paper",
            source_class="paper",
            peer_reviewed=True,
            published_on="2026-02-01",
            confidence=0.9,
            tags=["p-vs-np"],
        )
    )
    engine.register_formal_artifact(
        FormalArtifact(
            artifact_id="formal1",
            problem_name="P vs NP",
            artifact_type="lean-proof",
            uri="https://example.com/formal1",
            machine_checkable=True,
            verifier="Lean",
            checksum_sha256="abc123",
        )
    )

    partial = engine.assess_claim(
        claim="Claim without replication",
        evidence_ids=["paper1"],
        replication_passed=False,
        formal_artifact_id="formal1",
    )
    assert partial.status == "partial_result"
    assert "computational_replication" in partial.missing_source_classes

    verified = engine.assess_claim(
        claim="Claim with replication and formal proof",
        evidence_ids=["paper1"],
        replication_passed=True,
        formal_artifact_id="formal1",
    )
    assert verified.status == "verified_theorem"


def test_governance_blocks_verified_theorem_without_bundle() -> None:
    engine = MillenniumReasoningEngine()
    assessment = engine.assess_claim(
        claim="Insufficient evidence",
        evidence_ids=[],
        replication_passed=False,
    )
    decision = engine.decide_publication(assessment, reproducibility_artifacts=[])
    assert decision.approved is True

    engine.register_knowledge_asset(
        KnowledgeAsset(
            asset_id="paper2",
            title="Published paper 2",
            source_url="https://example.com/paper2",
            source_class="paper",
            peer_reviewed=True,
            published_on="2026-03-01",
            confidence=0.95,
            tags=["riemann"],
        )
    )
    engine.register_formal_artifact(
        FormalArtifact(
            artifact_id="formal2",
            problem_name="Riemann Hypothesis",
            artifact_type="lean-proof",
            uri="https://example.com/formal2",
            machine_checkable=True,
            verifier="Lean",
            checksum_sha256="def456",
        )
    )
    verified = engine.assess_claim(
        claim="High confidence claim",
        evidence_ids=["paper2"],
        replication_passed=True,
        formal_artifact_id="formal2",
    )
    blocked = engine.decide_publication(verified, reproducibility_artifacts=[])
    assert blocked.approved is False


def test_map_finding_to_domains() -> None:
    engine = MillenniumReasoningEngine()
    engine.register_domain_mapping(
        domain="cryptography",
        tags=["number-theory", "complexity"],
        datasets=["millennium_problems_unified"],
    )
    report = engine.map_finding_to_domains(
        finding="Observed structural relation in zeta zero distributions.",
        changed_capability="conjecture_generation",
        tags=["number-theory"],
        confidence=0.82,
    )
    assert "cryptography" in report.applicable_domains
    assert "millennium_problems_unified" in report.applicable_datasets
