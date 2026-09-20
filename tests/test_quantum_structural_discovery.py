from barrot_agent.geometry.quantum import (
    QubitState,
    QubitStateClass,
)
from barrot_agent.geometry.quantum_discovery import (
    QubitStructuralDiscovery,
    QuantumDiscoveryResult,
)


def test_qubit_structural_discovery_returns_generic_invariants():
    state = QubitState.from_xyz(0.0, 0.0, 0.5)

    result = QubitStructuralDiscovery().analyze(state)

    assert isinstance(result, QuantumDiscoveryResult)
    assert result.valid is True
    assert result.state_class == QubitStateClass.MIXED
    assert result.invariants["bloch_norm"] == 0.5
    assert result.invariants["purity"] == 0.625
    assert result.invariants["trace"] == 1.0


def test_qubit_representation_payload_contains_constraints():
    state = QubitState.from_xyz(0.0, 0.0, 1.0)

    payload = QubitStructuralDiscovery().representation_payload(state)

    assert payload["domain"] == "quantum"
    assert payload["kind"] == "qubit_bloch"
    assert payload["constraints"][0]["satisfied"] is True
    assert payload["constraints"][1]["satisfied"] is True
    assert payload["evidence"]["state"] == "COMPUTED"
    assert payload["evidence"]["invariants"] == "DERIVED"


def test_invalid_qubit_is_structurally_invalid():
    state = QubitState.from_xyz(1.0, 1.0, 1.0)

    result = QubitStructuralDiscovery().analyze(state)
    signature = QubitStructuralDiscovery().structural_signature(state)

    assert result.valid is False
    assert result.state_class == QubitStateClass.INVALID
    assert signature["feasibility"] == "INVALID"


def test_structural_signature_is_deterministic():
    state = QubitState.from_xyz(0.2, -0.3, 0.4)
    discovery = QubitStructuralDiscovery()

    first = discovery.structural_signature(state)
    second = discovery.structural_signature(state)

    assert first == second
