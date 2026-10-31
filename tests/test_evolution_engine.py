from barrot_agent.evolution.evolution_engine import EvolutionEngine


def test_synthesis_returns_structure():
    engine = EvolutionEngine()
    result = engine.synthesize()
    assert "knowledge_items" in result
    assert "domains" in result
