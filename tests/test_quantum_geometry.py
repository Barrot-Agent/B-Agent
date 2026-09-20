import math

import pytest

from barrot_agent.geometry.quantum import (
    BlochVector,
    QubitState,
    QubitStateClass,
    maximally_mixed_state,
    pure_state,
)


def test_zero_vector_is_maximally_mixed():
    state = maximally_mixed_state()

    assert state.is_valid()
    assert state.classify() == QubitStateClass.MIXED
    assert state.purity() == pytest.approx(0.5)


def test_bloch_surface_is_pure():
    state = pure_state(0.0, 0.0)

    assert state.bloch.as_tuple() == pytest.approx((0.0, 0.0, 1.0))
    assert state.classify() == QubitStateClass.PURE
    assert state.purity() == pytest.approx(1.0)


def test_bloch_interior_is_mixed():
    state = QubitState.from_xyz(0.0, 0.0, 0.5)

    assert state.is_valid()
    assert state.classify() == QubitStateClass.MIXED
    assert state.purity() == pytest.approx(0.625)


def test_outside_bloch_ball_is_invalid():
    state = QubitState.from_xyz(1.0, 1.0, 1.0)

    assert not state.is_valid()
    assert state.classify() == QubitStateClass.INVALID


def test_density_matrix_round_trip():
    original = QubitState.from_xyz(0.2, -0.3, 0.4)

    matrix = original.to_density_matrix()

    recovered = QubitState.from_density_matrix(
        [
            [matrix.a, matrix.b],
            [matrix.c, matrix.d],
        ]
    )

    assert recovered.bloch.as_tuple() == pytest.approx(
        original.bloch.as_tuple()
    )


def test_density_matrix_rejects_wrong_trace():
    with pytest.raises(ValueError):
        QubitState.from_density_matrix(
            [
                [1.0, 0.0],
                [0.0, 1.0],
            ]
        )


def test_density_matrix_rejects_non_physical_state():
    with pytest.raises(ValueError):
        QubitState.from_density_matrix(
            [
                [1.5, 0.0],
                [0.0, -0.5],
            ]
        )


def test_measurement_probability():
    state = QubitState.from_xyz(0.0, 0.0, 1.0)

    z_axis = BlochVector(0.0, 0.0, 1.0)

    assert state.measurement_probability(z_axis) == pytest.approx(1.0)


def test_measurement_axis_must_be_unit():
    state = maximally_mixed_state()

    with pytest.raises(ValueError):
        state.measurement_probability(BlochVector(0.0, 0.0, 2.0))


def test_structural_signature():
    state = QubitState.from_xyz(0.0, 0.0, 0.5)

    sig = state.structural_signature()

    assert sig.bloch_norm == pytest.approx(0.5)
    assert sig.bloch_norm_squared == pytest.approx(0.25)
    assert sig.purity == pytest.approx(0.625)
    assert sig.trace == pytest.approx(1.0)
    assert sig.positive_semidefinite is True


def test_pure_state_preserves_unit_norm():
    state = pure_state(math.pi / 3.0, math.pi / 7.0)

    assert state.bloch.norm == pytest.approx(1.0)
    assert state.classify() == QubitStateClass.PURE
