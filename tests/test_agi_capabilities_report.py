"""Regression tests for the documented AGI capability report."""

from barrot_agent.agi.agi_orchestrator import AGICapability, AGIOrchestrator, AGIStatus


def test_capabilities_report_has_documented_read_only_shape():
    orchestrator = AGIOrchestrator()

    report = orchestrator.get_agi_capabilities_report()

    assert report["orchestrator_status"] == AGIStatus.OPERATIONAL.value
    assert report["initialization_time"] == orchestrator.initialization_time
    assert report["capabilities"]["count"] == len(AGICapability)
    assert set(report["capabilities"]["available"]) == {
        capability.value for capability in AGICapability
    }
    assert report["knowledge_domains"] == {
        "count": 0,
        "domains": [],
        "total_items": 0,
    }
    assert report["learning_history"] == {
        "total_learning_sessions": 0,
        "decision_count": 0,
        "improvement_cycles": 0,
    }
    assert report["active_integrations"]
    assert report["timestamp"]
    assert orchestrator.decision_history == []
    assert orchestrator.improvement_cycles == []


def test_capabilities_report_reflects_recorded_knowledge_and_learning():
    orchestrator = AGIOrchestrator()
    orchestrator.integrate_new_knowledge(
        {
            "domain": "xrp_market_structure",
            "content": {"feature": "spread"},
            "metadata": {"source": "unit_test"},
        }
    )
    orchestrator.self_improve()

    report = orchestrator.get_agi_capabilities_report()

    assert report["knowledge_domains"] == {
        "count": 1,
        "domains": ["xrp_market_structure"],
        "total_items": 1,
    }
    assert report["learning_history"]["total_learning_sessions"] == 1
    assert report["learning_history"]["improvement_cycles"] == 1
