from __future__ import annotations

from pathlib import Path

from barrot_agent.research import (
    ClaimStatus,
    ConvergenceIndependence,
    ConvergenceObservation,
    ConvergenceScenarioEngine,
    ConvergenceStatus,
    FormalVerificationRecord,
    NavierStokesProblemAdapter,
    ResearchEvidence,
    ResearchTrack,
    ScenarioMaturity,
    ScenarioRelationshipType,
    ScientificDiscoveryController,
    StaticResearchProblemAdapter,
    VerificationIndependence,
)
from tests.v3_test_harness import write_science_bundle


def obs(
    observation_id: str,
    *,
    track_id: str,
    statement: str,
    features: list[str],
    source: str,
    evidence_ids: list[str],
    provenance_id: str,
    parent_observations: list[str] | None = None,
    timestamp: float = 1.0,
) -> ConvergenceObservation:
    return ConvergenceObservation(
        observation_id=observation_id,
        track_id=track_id,
        research_problem_id="problem",
        statement=statement,
        features=features,
        source=source,
        evidence_ids=evidence_ids,
        provenance_id=provenance_id,
        confidence=0.8,
        timestamp=timestamp,
        dependencies=[],
        parent_observations=parent_observations or [],
    )


def test_independent_convergence() -> None:
    engine = ConvergenceScenarioEngine()
    analysis = engine.analyze_observations(
        research_problem_id="problem",
        domain="math",
        observations=[
            obs("a", track_id="t1", statement="bounded velocity estimate", features=["claim:c1", "dependency:d1"], source="s1", evidence_ids=["e1"], provenance_id="p1"),
            obs("b", track_id="t2", statement="bounded velocity estimate", features=["claim:c1", "dependency:d1"], source="s2", evidence_ids=["e2"], provenance_id="p2"),
        ],
    )

    assert analysis.patterns[0]["status"] == ConvergenceStatus.CONVERGENCE.value
    assert analysis.patterns[0]["independence_analysis"]["status"] == ConvergenceIndependence.INDEPENDENT.value


def test_dependent_convergence() -> None:
    engine = ConvergenceScenarioEngine()
    analysis = engine.analyze_observations(
        research_problem_id="problem",
        domain="math",
        observations=[
            obs("a", track_id="t1", statement="same claim", features=["claim:c1"], source="s1", evidence_ids=["e1"], provenance_id="shared"),
            obs("b", track_id="t2", statement="same claim", features=["claim:c1"], source="s2", evidence_ids=["e1"], provenance_id="shared"),
        ],
    )

    assert analysis.patterns[0]["independence_analysis"]["status"] == ConvergenceIndependence.DEPENDENT.value
    assert analysis.patterns[0]["status"] == ConvergenceStatus.DUPLICATION.value


def test_partial_independence() -> None:
    engine = ConvergenceScenarioEngine()
    analysis = engine.analyze_observations(
        research_problem_id="problem",
        domain="technology",
        observations=[
            obs("a", track_id="t1", statement="shared source claim", features=["claim:c1", "source:paper"], source="paper", evidence_ids=["e1"], provenance_id="p1"),
            obs("b", track_id="t2", statement="shared source claim", features=["claim:c1", "source:paper"], source="paper", evidence_ids=["e2"], provenance_id="p2"),
        ],
    )

    assert analysis.patterns[0]["independence_analysis"]["status"] == ConvergenceIndependence.PARTIALLY_INDEPENDENT.value
    assert analysis.patterns[0]["status"] == ConvergenceStatus.PARTIAL_CONVERGENCE.value


def test_duplicate_observations() -> None:
    engine = ConvergenceScenarioEngine()
    pattern = engine.analyze_observations(
        research_problem_id="problem",
        domain="math",
        observations=[
            obs("a", track_id="t1", statement="repeat", features=["claim:c1"], source="s1", evidence_ids=["e1"], provenance_id="p1"),
            obs("b", track_id="t2", statement="repeat", features=["claim:c1"], source="s2", evidence_ids=["e1"], provenance_id="p1"),
        ],
    ).patterns[0]

    assert pattern["status"] == ConvergenceStatus.DUPLICATION.value


def test_contradiction() -> None:
    engine = ConvergenceScenarioEngine()
    analysis = engine.analyze_observations(
        research_problem_id="problem",
        domain="math",
        observations=[
            obs("a", track_id="t1", statement="velocity remains bounded", features=["claim:c1"], source="s1", evidence_ids=["e1"], provenance_id="p1"),
            obs("b", track_id="t2", statement="velocity is not bounded", features=["claim:c1"], source="s2", evidence_ids=["e2"], provenance_id="p2"),
        ],
    )

    assert analysis.patterns[0]["status"] == ConvergenceStatus.CONTRADICTION.value
    assert analysis.contradictions[0]["resolution_status"] in {ClaimStatus.DISPUTED.value, "BOTH_SUPPORTED_UNDER_DIFFERENT_ASSUMPTIONS"}


def test_invalid_observation() -> None:
    engine = ConvergenceScenarioEngine()
    analysis = engine.analyze_observations(
        research_problem_id="problem",
        domain="math",
        observations=[
            obs("a", track_id="t1", statement="unknown", features=["claim:c1"], source="", evidence_ids=[], provenance_id=""),
        ],
    )

    assert analysis.observations[0]["independence_status"] == ConvergenceIndependence.INVALID.value


def test_provenance_loss() -> None:
    engine = ConvergenceScenarioEngine()
    track = ResearchTrack(track_id="t1", role="proof", strategy="derive", hypothesis="h", provenance=[])
    observation = engine.build_observations(
        research_problem_id="problem",
        tracks=[track],
        evidence=[],
        cross_pollination=[],
        formal_records=[],
        blind_mode=False,
    )[0]

    assert engine.analyze_observations(research_problem_id="problem", domain="math", observations=[observation]).observations[0]["independence_status"] == ConvergenceIndependence.INVALID.value


def test_circular_evidence() -> None:
    engine = ConvergenceScenarioEngine()
    analysis = engine.analyze_observations(
        research_problem_id="problem",
        domain="math",
        observations=[
            obs("a", track_id="t1", statement="claim", features=["claim:c1"], source="s1", evidence_ids=["e1"], provenance_id="p1", parent_observations=["t2"]),
            obs("b", track_id="t2", statement="claim", features=["claim:c1"], source="s2", evidence_ids=["e2"], provenance_id="p2", parent_observations=["t1"]),
        ],
    )

    assert analysis.patterns[0]["independence_analysis"]["status"] == ConvergenceIndependence.DEPENDENT.value


def test_inherited_evidence_falsely_appearing_independent() -> None:
    engine = ConvergenceScenarioEngine()
    analysis = engine.analyze_observations(
        research_problem_id="problem",
        domain="math",
        observations=[
            obs("a", track_id="source", statement="claim", features=["claim:c1"], source="s1", evidence_ids=["e1"], provenance_id="p1"),
            obs("b", track_id="child", statement="claim", features=["claim:c1"], source="s2", evidence_ids=["e2"], provenance_id="p2", parent_observations=["source"]),
        ],
    )

    assert analysis.patterns[0]["independence_analysis"]["status"] == ConvergenceIndependence.DEPENDENT.value


def test_temporal_convergence() -> None:
    engine = ConvergenceScenarioEngine()
    analysis = engine.analyze_observations(
        research_problem_id="problem",
        domain="technology",
        observations=[
            obs("a", track_id="t1", statement="signal", features=["claim:c1", "feature:x"], source="s1", evidence_ids=["e1"], provenance_id="p1", timestamp=1.0),
            obs("b", track_id="t2", statement="signal", features=["claim:c1", "feature:x", "feature:y"], source="s2", evidence_ids=["e2"], provenance_id="p2", timestamp=2.0),
            obs("c", track_id="t3", statement="signal", features=["claim:c1", "feature:x", "feature:z"], source="s3", evidence_ids=["e3"], provenance_id="p3", timestamp=3.0),
        ],
    )

    assert analysis.temporal_analysis[0]["recurring_features"] == ["claim:c1", "feature:x"]
    assert "feature:z" in analysis.temporal_analysis[0]["new_features"]


def test_hypothesis_generation() -> None:
    engine = ConvergenceScenarioEngine()
    analysis = engine.analyze_observations(
        research_problem_id="problem",
        domain="math",
        observations=[
            obs("a", track_id="t1", statement="bounded velocity estimate", features=["claim:c1", "dependency:d1"], source="s1", evidence_ids=["e1"], provenance_id="p1"),
            obs("b", track_id="t2", statement="bounded velocity estimate", features=["claim:c1", "dependency:d1"], source="s2", evidence_ids=["e2"], provenance_id="p2"),
        ],
    )

    assert analysis.hypotheses
    assert analysis.hypotheses[0]["status"] == ScenarioMaturity.CORROBORATED.value


def test_hypothesis_falsification() -> None:
    engine = ConvergenceScenarioEngine()
    pattern = engine._analyze_pair(
        obs("a", track_id="t1", statement="claim", features=["claim:c1"], source="s1", evidence_ids=["e1"], provenance_id="p1"),
        obs("b", track_id="t2", statement="claim", features=["claim:c1"], source="s2", evidence_ids=["e2"], provenance_id="p2"),
    )
    pattern.contradicting_evidence = ["e9"]

    assert engine._hypothesis_status(pattern, {}) == ScenarioMaturity.UNRESOLVED.value


def test_unsupported_hypothesis() -> None:
    engine = ConvergenceScenarioEngine()
    analysis = engine.analyze_observations(
        research_problem_id="problem",
        domain="economics",
        observations=[
            obs("a", track_id="t1", statement="alpha", features=["feature:a"], source="s1", evidence_ids=["e1"], provenance_id="p1"),
            obs("b", track_id="t2", statement="beta", features=["feature:b"], source="s2", evidence_ids=["e2"], provenance_id="p2"),
        ],
    )

    assert analysis.hypotheses == []


def test_external_verification_required() -> None:
    engine = ConvergenceScenarioEngine()
    analysis = engine.analyze_observations(
        research_problem_id="problem",
        domain="math",
        observations=[
            obs("a", track_id="t1", statement="bounded velocity estimate", features=["claim:c1", "dependency:d1"], source="s1", evidence_ids=["e1"], provenance_id="p1"),
            obs("b", track_id="t2", statement="bounded velocity estimate", features=["claim:c1", "dependency:d1"], source="s2", evidence_ids=["e2"], provenance_id="p2"),
        ],
    )

    assert analysis.external_verification_required is True
    assert analysis.hypotheses[0]["required_tests"]


def test_blind_track_isolation() -> None:
    engine = ConvergenceScenarioEngine()
    source = ResearchTrack(track_id="source", role="proof", strategy="derive", hypothesis="claim", intermediate_results=[{"claim_id": "c1", "summary": "claim", "status": "SUPPORTED"}], provenance=["s1"])
    recipient = ResearchTrack(track_id="recipient", role="proof", strategy="derive", hypothesis="claim", provenance=["s2"])
    observations = engine.build_observations(
        research_problem_id="problem",
        tracks=[source, recipient],
        evidence=[],
        cross_pollination=[],
        formal_records=[],
        blind_mode=True,
    )

    assert all(not item.parent_observations for item in observations)


def test_controlled_release_after_blind_phase() -> None:
    engine = ConvergenceScenarioEngine()
    analysis = engine.analyze_observations(
        research_problem_id="problem",
        domain="technology",
        observations=[
            obs("a", track_id="t1", statement="signal", features=["claim:c1", "feature:x"], source="s1", evidence_ids=["e1"], provenance_id="p1"),
            obs("b", track_id="t2", statement="signal", features=["claim:c1", "feature:x"], source="s2", evidence_ids=["e2"], provenance_id="p2"),
        ],
        blind_mode=True,
    )

    assert analysis.blind_mode is True
    assert analysis.controlled_release_ready is True


def test_shared_source_false_convergence() -> None:
    engine = ConvergenceScenarioEngine()
    analysis = engine.analyze_observations(
        research_problem_id="problem",
        domain="technology",
        observations=[
            obs("a", track_id="t1", statement="shared source claim", features=["claim:c1", "source:shared"], source="shared", evidence_ids=["e1"], provenance_id="p1"),
            obs("b", track_id="t2", statement="shared source claim", features=["claim:c1", "source:shared"], source="shared", evidence_ids=["e2"], provenance_id="p2"),
        ],
    )

    assert analysis.patterns[0]["status"] == ConvergenceStatus.PARTIAL_CONVERGENCE.value


def test_correlation_versus_causation_protection() -> None:
    relationship = ConvergenceScenarioEngine().build_relationship(
        source_node="tech_a",
        target_node="tech_b",
        relationship_type=ScenarioRelationshipType.CAUSES.value,
        evidence=["e1"],
        source="report",
        confidence=0.9,
        assumptions=["A1"],
        provenance=["p1"],
    )

    assert relationship.relationship_type == ScenarioRelationshipType.MAY_CAUSE.value
    assert relationship.status == ScenarioMaturity.SPECULATIVE.value


def test_scenario_maturity_promotion() -> None:
    hypothesis = ConvergenceScenarioEngine().analyze_observations(
        research_problem_id="problem",
        domain="math",
        observations=[
            obs("a", track_id="t1", statement="bounded velocity estimate", features=["claim:c1", "dependency:d1"], source="s1", evidence_ids=["e1"], provenance_id="p1"),
            obs("b", track_id="t2", statement="bounded velocity estimate", features=["claim:c1", "dependency:d1"], source="s2", evidence_ids=["e2"], provenance_id="p2"),
        ],
    ).hypotheses[0]

    assert hypothesis["status"] == ScenarioMaturity.CORROBORATED.value


def test_scenario_maturity_rejection() -> None:
    hypothesis = ConvergenceScenarioEngine().analyze_observations(
        research_problem_id="problem",
        domain="technology",
        observations=[
            obs("a", track_id="t1", statement="same claim", features=["claim:c1", "source:shared"], source="shared", evidence_ids=["e1"], provenance_id="p1"),
            obs("b", track_id="t2", statement="same claim", features=["claim:c1", "source:shared"], source="shared", evidence_ids=["e2"], provenance_id="p2"),
        ],
    ).hypotheses[0]

    assert hypothesis["status"] == ScenarioMaturity.EMERGING.value


def test_navier_stokes_convergence() -> None:
    adapter = NavierStokesProblemAdapter()
    problem, _, _, evidence, tracks, _, formal_specs, _ = adapter.ingest()
    verifier = ScientificDiscoveryController(workspace=Path("/tmp")).verifier
    formal_records = [verifier.verify(spec) for spec in formal_specs]
    analysis = ConvergenceScenarioEngine().analyze(
        research_problem_id=problem.problem_id,
        domain=problem.domain,
        tracks=tracks,
        evidence=evidence,
        cross_pollination=[],
        formal_records=formal_records,
    )

    assert analysis.observations
    assert analysis.external_verification_required is True


def test_source_team_verification_versus_independent_verification() -> None:
    engine = ConvergenceScenarioEngine()
    observations = engine.build_observations(
        research_problem_id="problem",
        tracks=[],
        evidence=[],
        cross_pollination=[],
        formal_records=[
            FormalVerificationRecord(verification_id="f1", system="lean", theorem_names=["T"], source_files=["A.lean"], repository="repo", source_commit="abc", compiled=True, independently_verified=False),
            FormalVerificationRecord(verification_id="f2", system="lean", theorem_names=["T"], source_files=["A.lean"], repository="repo2", source_commit="def", compiled=True, independently_verified=True),
        ],
        blind_mode=False,
    )

    statuses = {item.track_id: item.independence_status for item in observations}
    assert statuses["f1"] == ConvergenceIndependence.DEPENDENT.value
    assert statuses["f2"] == ConvergenceIndependence.INDEPENDENT.value


def test_remote_viewing_material_classified_as_unverified() -> None:
    material = ConvergenceScenarioEngine().classify_source_material(source="remote_viewing_material", statement="Future interface scenario")

    assert material.classification == ["SOURCE_REPORTED", "UNVERIFIED", "HYPOTHESIS_MATERIAL"]


def test_persistence_reload(tmp_path: Path) -> None:
    bundle = write_science_bundle(tmp_path / "bundle.json", independent=False, adversarial_status=ClaimStatus.SUPPORTED.value)
    controller = ScientificDiscoveryController(workspace=tmp_path)
    adapter = StaticResearchProblemAdapter(bundle)

    cycle = controller.run(adapter)
    loaded = controller.ledger_store.load_cycle_by_fingerprint(adapter.problem_fingerprint())

    assert cycle.convergence_analysis
    assert loaded is not None
    assert loaded.convergence_analysis == cycle.convergence_analysis


def test_idempotent_repeated_analysis() -> None:
    engine = ConvergenceScenarioEngine()
    observations = [
        obs("a", track_id="t1", statement="bounded velocity estimate", features=["claim:c1", "dependency:d1"], source="s1", evidence_ids=["e1"], provenance_id="p1"),
        obs("b", track_id="t2", statement="bounded velocity estimate", features=["claim:c1", "dependency:d1"], source="s2", evidence_ids=["e2"], provenance_id="p2"),
    ]

    first = engine.analyze_observations(research_problem_id="problem", domain="math", observations=observations)
    second = engine.analyze_observations(research_problem_id="problem", domain="math", observations=observations)

    assert first.analysis_id == second.analysis_id
