"""Tests for the typed relational model."""
import pytest

from barrot_agent.geometry.relations import (
    RelationGraph,
    RelationType,
)


def test_relation_requires_a_witness():
    graph = RelationGraph()
    with pytest.raises(ValueError):
        graph.add(RelationType.ADJACENT_TO, "a", "b", witness="")
    with pytest.raises(ValueError):
        graph.add(RelationType.ADJACENT_TO, "a", "b", witness="   ")


def test_relation_requires_endpoints():
    graph = RelationGraph()
    with pytest.raises(ValueError):
        graph.add(RelationType.ADJACENT_TO, "", "b", witness="face:1")
    with pytest.raises(ValueError):
        graph.add(RelationType.ADJACENT_TO, "a", "", witness="face:1")


def test_irreflexive_relation_rejects_self_loop_at_insert():
    graph = RelationGraph()
    with pytest.raises(ValueError):
        graph.add(RelationType.BOUNDARY_OF, "a", "a", witness="edge:1")


def test_symmetric_relation_may_appear_both_ways():
    graph = RelationGraph()
    graph.add(RelationType.ADJACENT_TO, "a", "b", witness="face:1")
    graph.add(RelationType.ADJACENT_TO, "b", "a", witness="face:1")
    assert graph.validate() == []


def test_antisymmetric_relation_violation_is_reported():
    graph = RelationGraph()
    graph.add(RelationType.BOUNDARY_OF, "a", "b", witness="edge:1")
    graph.add(RelationType.BOUNDARY_OF, "b", "a", witness="edge:1")
    errors = graph.validate()
    assert any("antisymmetric" in error for error in errors)


def test_specializes_cycle_is_reported():
    graph = RelationGraph()
    graph.add(RelationType.SPECIALIZES, "a", "b", witness="rule:1")
    graph.add(RelationType.SPECIALIZES, "b", "c", witness="rule:2")
    graph.add(RelationType.SPECIALIZES, "c", "a", witness="rule:3")
    errors = graph.validate()
    assert any("acyclic" in error for error in errors)


def test_derived_from_cycle_is_reported():
    graph = RelationGraph()
    graph.add(RelationType.DERIVED_FROM, "a", "b", witness="op:1")
    graph.add(RelationType.DERIVED_FROM, "b", "a", witness="op:2")
    assert any("acyclic" in error for error in graph.validate())


def test_clean_graph_has_no_violations():
    graph = RelationGraph()
    graph.add(RelationType.BOUNDARY_OF, "edge", "face", witness="incidence:1")
    graph.add(RelationType.CONTAINS, "face", "edge", witness="incidence:1")
    graph.add(RelationType.SPECIALIZES, "cell", "closure", witness="stratum:1")
    assert graph.validate() == []


def test_neighbours_filter_by_direction():
    graph = RelationGraph()
    graph.add(RelationType.BOUNDARY_OF, "edge", "face", witness="incidence:1")
    assert graph.neighbours("edge") == ("face",)
    assert graph.neighbours("edge", direction="in") == ()
    assert graph.neighbours("face", direction="in") == ("edge",)
    assert graph.neighbours("edge", direction="both") == ("face",)


def test_relations_can_be_filtered_by_node_and_type():
    graph = RelationGraph()
    graph.add(RelationType.BOUNDARY_OF, "edge", "face", witness="incidence:1")
    graph.add(RelationType.ADJACENT_TO, "face", "face2", witness="edge:2")
    assert len(graph) == 2
    assert len(graph.relations(RelationType.BOUNDARY_OF)) == 1
    assert len(graph.relations(node="face")) == 2
    assert graph.relations(node="missing") == ()


def test_serialization_preserves_witness():
    graph = RelationGraph()
    record = graph.add(RelationType.BOUNDARY_OF, "edge", "face", witness="incidence:1")
    assert record.to_dict() == {
        "type": "boundary_of",
        "source": "edge",
        "target": "face",
        "witness": "incidence:1",
    }
