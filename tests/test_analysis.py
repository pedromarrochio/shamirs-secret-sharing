"""Candidatos, contagens e distribuições: verificação exata em espaços pequenos."""

from collections import Counter
from itertools import combinations

import pytest

from shamir.cryptography.analysis import (
    compatible_secret_counts,
    has_unit_separations,
    observation_distribution,
    observations_independent_of_secret,
)


def test_empty_observation_and_threshold_one():
    assert compatible_secret_counts(5, 3, []) == Counter({s: 25 for s in range(5)})
    assert observation_distribution(5, 3, [], 2) == Counter({(): 25})
    assert compatible_secret_counts(5, 1, [(1, 2)]) == Counter({2: 1})
    assert compatible_secret_counts(5, 1, [(1, 2), (2, 3)]) == Counter()
    assert not observations_independent_of_secret(5, 1, [1])


def test_prime_candidates_have_equal_multiplicities_below_threshold():
    for points, multiplicity in (([(1, 4)], 5), ([(1, 4), (2, 3)], 1)):
        assert compatible_secret_counts(5, 3, points) == Counter({s: multiplicity for s in range(5)})


def test_joint_distributions_include_zero_leading_coefficients():
    for xs in combinations([1, 2, 3, 4], 2):
        expected = Counter({(a, b): 1 for a in range(5) for b in range(5)})
        for secret in range(5):
            assert observation_distribution(5, 3, xs, secret) == expected


def test_nonunit_coordinate_leaks_but_units_do_not_leak_alone():
    assert observation_distribution(12, 2, [6], 5) == Counter({(5,): 6, (11,): 6})
    assert not observations_independent_of_secret(12, 3, [6])
    for x in (1, 5, 7, 11):
        assert observations_independent_of_secret(12, 3, [x])


def test_polynomial_nonuniqueness_does_not_imply_secret_nonuniqueness():
    assert compatible_secret_counts(12, 3, [(1, 3), (2, 2), (3, 5)]) == Counter({8: 2})
    assert compatible_secret_counts(12, 3, [(1, 3), (2, 2), (4, 0)]) == Counter({0: 2, 4: 2, 8: 2})


def test_unit_condition_includes_zero_and_all_pairwise_differences():
    assert has_unit_separations(25, [1, 2, 3, 4])
    assert not has_unit_separations(15, [1, 2, 3])  # diferenças boas, x = 3 não é unidade
    assert not has_unit_separations(12, [1, 5, 7])  # pontos unidades, diferenças ruins


@pytest.mark.parametrize("m,k,points", [
    (1, 3, []), (5, 0, []), (5, 3, [(0, 1)]), (5, 3, [(5, 1)]),
    (5, 3, [(1, 5)]), (5, 3, [(1, 1), (1, 2)]),
])
def test_invalid_candidate_parameters(m, k, points):
    with pytest.raises(ValueError):
        compatible_secret_counts(m, k, points)


@pytest.mark.parametrize("k,points", [(True, []), (2.5, []), (3, [(True, 1)]), (3, [(1, False)])])
def test_invalid_candidate_types(k, points):
    with pytest.raises(TypeError):
        compatible_secret_counts(5, k, points)


@pytest.mark.parametrize("secret", [-1, 5, True, "2"])
def test_distribution_validates_secret(secret):
    with pytest.raises((TypeError, ValueError)):
        observation_distribution(5, 3, [1], secret)


def test_enumeration_budget_is_checked_before_large_work():
    with pytest.raises(ValueError, match="Enumeração muito grande"):
        compatible_secret_counts(257, 10, [(1, 1)])
    with pytest.raises(ValueError, match="Enumeração muito grande"):
        observation_distribution(257, 10, [1], 1)
    with pytest.raises(ValueError, match="Enumeração muito grande"):
        observations_independent_of_secret(257, 10, [1])
