"""Focused tests for longevity integration modules."""

from __future__ import annotations

import json

from barrot_agent.ingestion.biomarker_analyzer import (
    AgingClockCalculator,
    BiomarkerTracker,
    BiomarkerVisualizer,
    TrialProgressMonitor,
)
from barrot_agent.analysis.epigenetic_reprogramming_engine import EpigeneticReprogrammingEngine
from barrot_agent.ingestion.longevity_micro_ingestion import LongevityMicroIngestion
from barrot_agent.monetization.trial_tracker import DiscoveryExtractor, EfficacyAnalyzer, ParticipantCohort, SafetyMonitor


def test_longevity_ingestion_builds_unified_payload() -> None:
    ingestion = LongevityMicroIngestion()
    payload = ingestion.build_unified_payload(
        paper_text="Transient Yamanaka factor expression improved epigenetic clocks and NAD+.",
        trial_records=[
            {
                "participant_id": "P-1",
                "treatment_arm": "OSKM",
                "baseline_epigenetic_age": 58,
                "followup_epigenetic_age": 54,
                "nad_baseline": 100,
                "nad_followup": 120,
                "adverse_events": ["mild headache"],
            }
        ],
        methylation_samples=[{"cg16867657": 0.6, "cg06639320": 0.52}],
        biomarker_measurements={
            "epigenetic_age_horvath": [
                {"timestamp": "2026-01-01", "value": 58.0},
                {"timestamp": "2026-07-01", "value": 54.0},
            ]
        },
    )

    assert payload["research_domain"] == "longevity"
    assert payload["aging_mechanisms"]
    assert payload["epigenetic_pattern_matrices"]
    assert payload["_meta"]["schema_version"] == "1.0"
    assert "epigenetic_pattern_matrix" not in payload
    assert payload["omega_ingest"]["compatibility"] == "omega_ingest_v1"
    assert payload["mmi_breakthroughs"]


def test_biomarker_tracker_and_monitor_predictive_outputs() -> None:
    tracker = BiomarkerTracker()
    tracker.record("nad_plus", "2026-01-01", 1.0)
    tracker.record("nad_plus", "2026-02-01", 1.01)
    tracker.record("nad_plus", "2026-03-01", 1.0)
    assert tracker.detect_plateau("nad_plus", window=3, tolerance=0.02)

    monitor = TrialProgressMonitor()
    monitor.add_outcome("OSK", 60, 55)
    monitor.add_outcome("OSK", 62, 57)
    assert monitor.reversal_by_arm()["OSK"] == 5.0
    assert monitor.estimate_time_to_reversal(target_reversal_years=10.0)["OSK"] == 2.0


def test_age_biomarker_trend_directionality() -> None:
    ingestion = LongevityMicroIngestion()
    age_timeline = ingestion.track_biomarker_progression(
        participant_id="P-9",
        biomarker="epigenetic_age_horvath",
        measurements=[
            {"timestamp": "2026-01-01", "value": 60.0},
            {"timestamp": "2026-04-01", "value": 57.0},
        ],
        higher_is_better=False,
    )
    assert age_timeline["trend"] == "improving"


def test_aging_clock_and_visualizer_outputs() -> None:
    calc = AgingClockCalculator(baseline_age=50)
    age = calc.compute_epigenetic_age(
        {
            "cg16867657": 0.62,
            "cg06639320": 0.59,
            "cg02228185": 0.57,
            "cg21572722": 0.58,
        }
    )
    assert age > 50

    tracker = BiomarkerTracker()
    tracker.record("horvath", "2026-01-01", 59)
    tracker.record("horvath", "2026-04-01", 57)
    points = tracker.trajectory("horvath")
    series = BiomarkerVisualizer.trend_series(points)
    heatmap = BiomarkerVisualizer.heatmap_matrix({"horvath": points})

    assert series["x"] == ["2026-01-01", "2026-04-01"]
    assert heatmap["biomarkers"] == ["horvath"]


def test_reprogramming_engine_returns_safe_protocol() -> None:
    engine = EpigeneticReprogrammingEngine()
    result = engine.optimize_protocol(target_cell_type="eye", max_risk=8.0)
    assert result["candidate_count"] > 0
    assert result["best_protocol"].target_cell_type == "eye"


def test_trial_tracker_mmi_discovery_hooks() -> None:
    cohort = ParticipantCohort(phase_number=2, total_participants=3)
    cohort.add_participant_outcome("A", "OSKM", 5.2)
    cohort.add_participant_outcome("B", "OSKM", 4.1)
    cohort.add_participant_outcome("C", "Control", 0.2)

    efficacy = EfficacyAnalyzer(cohort)
    assert efficacy.estimate_success_probability(efficacy_threshold=3.0) == 0.667

    safety = SafetyMonitor()
    safety.log_adverse_event("A", "OSKM", "mild", "fatigue")

    extractor = DiscoveryExtractor(cohort=cohort, safety_monitor=safety)
    payload = extractor.to_mmi_payload()
    assert payload["topic"] == "longevity_breakthroughs"
    assert payload["discoveries"]

    # Ensure payload remains JSON serializable for MMI consumers.
    json.dumps(payload)
