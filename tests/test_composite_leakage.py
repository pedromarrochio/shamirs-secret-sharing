"""Testes do experimento de vazamento de informação em Z_m composto."""

from math import gcd

import pytest

from experiments.composite_leakage import (
    candidate_secrets,
    is_uniform_and_independent,
    leakage_table,
    share_distribution,
)


def test_prime_field_leaks_nothing():
    # em Z_13, um fragmento tem a mesma distribuição para qualquer segredo
    for x in range(1, 13):
        assert is_uniform_and_independent(13, x)
        assert len(share_distribution(13, x, 0)) == 13
    assert candidate_secrets(13, 6, 12) == list(range(13))


def test_one_share_reveals_secret_mod_gcd():
    # f(x) ≡ s (mod mdc(x, m)): o fragmento em x = 6 deixa só 2 candidatos
    assert candidate_secrets(12, 6, 11) == [5, 11]
    assert candidate_secrets(12, 2, 7) == [1, 3, 5, 7, 9, 11]
    assert not is_uniform_and_independent(12, 6)
    for row in leakage_table(12):
        assert row["gcd"] == gcd(row["x"], 12)
        assert row["candidates"] == 12 // row["gcd"]


def test_units_of_composite_ring_leak_nothing_alone():
    for x in (1, 5, 7, 11):
        assert is_uniform_and_independent(12, x)


def test_true_secret_is_always_a_candidate():
    from shamir.algebra.integer_mod_ring import IntegerModRing
    from shamir.algebra.polynomial import Polynomial

    ring = IntegerModRing(12)
    for secret in range(12):
        f = Polynomial([secret, 7, 3], ring)
        for x in range(1, 12):
            assert secret in candidate_secrets(12, x, f.evaluate(x))


@pytest.mark.parametrize("args", [(1, 3, 1), (12, 1, 1), (12, 3, 0), (12, 3, 12)])
def test_invalid_parameters(args):
    m, k, x = args
    with pytest.raises(ValueError):
        share_distribution(m, x, 0, k)