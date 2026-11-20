from __future__ import annotations

import json
import runpy
from pathlib import Path

from barrot_agent import mem_palace
from barrot_agent.monetization.mmi_data_analyzer import MMIDataAnalyzer
from barrot_agent.monetization.monetization_engine import MonetizationEngine
from barrot_agent.monetization.trial_tracker import (
    DiscoveryExtractor,
    EfficacyAnalyzer,
    ParticipantCohort,
    SafetyMonitor,
    TrialMetadata,
)
from barrot_agent.rendering.dataset_analytics import DatasetAnalytics
from barrot_agent.rendering.dataset_manager import DatasetManager


def test_mmi_data_analyzer_generates_recommendations_and_safe_exports(tmp_path: Path) -> None:
    analyzer = MMIDataAnalyzer()

    assert len(analyzer.current_agi_gaps) == 12
    assert all(0.0 <= value <= 1.0 for value in analyzer.current_agi_gaps.values())

    sources = analyzer.analyze_high_impact_datasets()
    assert sources
    assert any(source.immediate_actionability for source in sources)

    recommendations = analyzer.generate_prioritized_recommendations()
    assert [item.priority_tier for item in recommendations] == [1, 2, 3]
    assert sum(len(item.data_sources) for item in recommendations) == len(sources)

    json_path = tmp_path / "mmi-recommendations.json"
    assert analyzer.export_recommendations_to_json(str(json_path)) == str(json_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["total_sources_identified"] == len(sources)
    assert len(payload["recommendations"]) == 3
    assert set(payload["agi_gaps_identified"]) == {
        piece.value for piece in analyzer.current_agi_gaps
    }

    report_path = tmp_path / "mmi-report.md"
    analyzer.generate_markdown_report(str(report_path))
    report = report_path.read_text(encoding="utf-8")
    assert "Barrot MMI" in report
    assert "Priority Tier 1" in report


def test_monetization_engine_generates_metadata_without_executing_revenue_actions(
    tmp_path: Path,
) -> None:
    engine = MonetizationEngine()
    streams = engine.analyze_revolutionary_opportunities()

    assert streams
    assert engine.revenue_streams == streams
    assert all(stream.risk_level in {"low", "medium", "high"} for stream in streams)
    assert all(1.0 <= stream.scalability_factor <= 10.0 for stream in streams)

    protocols = engine.generate_implementation_protocols()
    assert len(protocols) == 3
    assert [protocol.protocol_name for protocol in protocols] == [
        "Immediate Revenue Activation",
        "Passive Income Infrastructure",
        "Premium Service Offerings",
    ]

    json_path = tmp_path / "monetization-protocols.json"
    assert engine.export_to_json(str(json_path)) == str(json_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["total_revenue_streams"] == len(engine.revenue_streams)
    assert len(payload["protocols"]) == 3

    report_path = tmp_path / "monetization-report.md"
    engine.generate_markdown_report(str(report_path))
    report = report_path.read_text(encoding="utf-8")
    assert "Advanced Monetization Protocols" in report
    assert "Revenue Stream Overview" in report


def test_trial_tracker_cohort_efficacy_safety_and_mmi_payload() -> None:
    metadata = TrialMetadata(
        trial_id="synthetic-trial",
        sponsor="test-sponsor",
        phase="2",
        status="completed",
        start_date="2026-01-01",
        expected_end_date="2026-06-30",
    )
    assert metadata.trial_id == "synthetic-trial"

    cohort = ParticipantCohort(phase_number=2, total_participants=3)
    assert cohort.calculate_mean_age_reversal() == 0.0
    assert cohort.compare_treatment_arms() == {}

    cohort.add_participant_outcome("p1", "arm-a", 5.0)
    cohort.add_participant_outcome("p2", "arm-a", 5.0)
    cohort.add_participant_outcome("p3", "arm-b", 1.0)

    assert cohort.calculate_mean_age_reversal() == 3.667
    assert cohort.identify_responders(threshold_years=4.0) == ["p1", "p2"]
    assert cohort.compare_treatment_arms() == {"arm-a": 5.0, "arm-b": 1.0}
    assert EfficacyAnalyzer(cohort).estimate_success_probability(3.0) == 0.667

    empty_monitor = SafetyMonitor()
    assert empty_monitor.calculate_safety_score() == 1.0
    empty_monitor.log_adverse_event("p1", "arm-a", "mild", "synthetic mild event")
    empty_monitor.log_adverse_event("p2", "arm-b", "severe", "synthetic severe event")
    assert empty_monitor.events_by_arm() == {"arm-a": 1, "arm-b": 1}
    assert empty_monitor.calculate_safety_score() == 0.65

    discoveries = DiscoveryExtractor(cohort, empty_monitor).surface_high_impact_discoveries()
    assert any(item["type"] == "efficacy_breakthrough" for item in discoveries)
    assert not any(item["type"] == "safety_signal" for item in discoveries)

    mild_monitor = SafetyMonitor()
    mild_monitor.log_adverse_event("p1", "arm-a", "mild", "synthetic mild event")
    extractor = DiscoveryExtractor(cohort, mild_monitor)
    assert any(item["type"] == "safety_signal" for item in extractor.surface_high_impact_discoveries())
    payload = extractor.to_mmi_payload()
    assert payload["topic"] == "longevity_breakthroughs"
    assert payload["source"] == "trial_tracker"


def test_dataset_manager_default_registry_registration_and_filters() -> None:
    manager = DatasetManager()
    assert len(manager.list_all()) >= 40

    record = manager.register_dataset(
        name="coverage-test-dataset",
        source="https://example.invalid/dataset",
        asset_count=10,
        formats=["OBJ", "GLB"],
        category="coverage-test-category",
        license="CC0",
        lod_levels=[0, 2],
        tags=["coverage-test-tag", "trees"],
        quality_score=4.5,
        size_gb=1.25,
    )

    assert manager.get("coverage-test-dataset") is record
    assert manager.query(
        category="COVERAGE-TEST-CATEGORY",
        asset_type="COVERAGE-TEST-TAG",
        lod=2,
        tags=["trees"],
    ) == [record]
    assert manager.query(category="coverage-test-category", lod=1) == []
    assert manager.total_assets() >= 10
    assert manager.total_size_gb() >= 1.25
    assert record.to_dict()["quality_score"] == 4.5


def test_dataset_analytics_records_usage_and_build_report() -> None:
    manager = DatasetManager()
    manager._registry.clear()
    manager.register_dataset(
        name="oak",
        source="local://oak",
        asset_count=10,
        formats=["OBJ", "GLB"],
        category="nature",
        license="CC0",
        quality_score=5.0,
        size_gb=2.0,
    )
    manager.register_dataset(
        name="city",
        source="local://city",
        asset_count=5,
        formats=["GLB"],
        category="urban",
        license="CC0",
        quality_score=4.5,
        size_gb=1.0,
    )
    manager.register_dataset(
        name="rough",
        source="local://rough",
        asset_count=2,
        formats=["FBX"],
        category="misc",
        license="CC0",
        quality_score=2.5,
        size_gb=0.5,
    )

    analytics = DatasetAnalytics(manager)
    analytics.record_access("oak", load_ms=10.0, bytes_transferred=100, quality_rating=4.0)
    analytics.record_access("oak", load_ms=30.0, bytes_transferred=300, quality_rating=5.0)
    analytics.record_access("city", load_ms=20.0, bytes_transferred=50, quality_rating=3.5)

    summary = analytics.get_summary()
    assert summary.system.total_assets_loaded == 17
    assert summary.system.registered_datasets == 3
    assert summary.category_breakdown == {"nature": 10, "urban": 5, "misc": 2}
    assert summary.format_breakdown == {"OBJ": 1, "GLB": 2, "FBX": 1}
    assert summary.quality_distribution == {"5.0": 1, "4.x": 1, "3.x": 0, "<3": 1}
    assert summary.top_datasets[0].dataset_name == "oak"
    assert summary.top_datasets[0].average_load_ms == 20.0
    assert summary.top_datasets[0].average_quality == 4.5
    assert summary.to_dict()["system"]["registered_datasets"] == 3

    report = analytics.generate_build_report()
    assert "# Barrot Build Report" in report
    assert "oak" in report
    assert "System Metrics" in report


def test_mem_palace_writes_only_to_injected_or_temporary_home(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    isolated_root = tmp_path / "injected-palace"
    monkeypatch.setattr(mem_palace, "PALACE_ROOT", str(isolated_root))

    mem_palace.initialize_palace()
    for hall in mem_palace.HALLS:
        assert (isolated_root / f"hall_{hall}").is_dir()

    mem_palace.store_memory("XRP", "forecast", "facts", "synthetic point-in-time evidence")
    memory_file = isolated_root / "hall_facts" / "XRP_forecast.md"
    assert "synthetic point-in-time evidence" in memory_file.read_text(encoding="utf-8")
    assert "ENTRY:" in memory_file.read_text(encoding="utf-8")
    assert "MemPalace Structure Initialized." in capsys.readouterr().out

    # Exercise the script entrypoint with HOME redirected to pytest's temporary directory.
    monkeypatch.setenv("HOME", str(tmp_path / "isolated-home"))
    module_path = Path(__file__).resolve().parents[1] / "barrot_agent" / "mem_palace.py"
    runpy.run_path(str(module_path), run_name="__main__")
    cli_root = tmp_path / "isolated-home" / "B-Agent" / "MemPalace"
    assert all((cli_root / f"hall_{hall}").is_dir() for hall in mem_palace.HALLS)


def test_monetization_legacy_scripts_are_exercised_in_temporary_working_directory(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    package_dir = Path(__file__).resolve().parents[1] / "barrot_agent" / "monetization"

    runpy.run_path(str(package_dir / "grant_generator.py"))
    output = capsys.readouterr().out
    assert "BARROT-Ω GRANT NARRATIVE" in output
    assert "Quantum-Resilient Triad" in output

    compiler_dir = tmp_path / "compiler-workspace"
    compiler_dir.mkdir()
    (compiler_dir / "sample.py").write_text("VALUE = 7\n", encoding="utf-8")
    (compiler_dir / "sample.sh").write_text("echo safe\n", encoding="utf-8")
    (compiler_dir / "sample.json").write_text('{"ok": true}\n', encoding="utf-8")
    monkeypatch.chdir(compiler_dir)

    runpy.run_path(str(package_dir / "mmi_compiler.py"))
    manifest = compiler_dir / "GLOBAL_STATE_MANIFEST.md"
    content = manifest.read_text(encoding="utf-8")
    assert "sample.py" in content
    assert "sample.sh" in content
    assert "sample.json" in content
