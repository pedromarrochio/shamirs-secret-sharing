from unittest.mock import patch

import pytest

from shamir.algebra.finite_field import FiniteField
from shamir.algebra.integer_mod_ring import IntegerModRing
from shamir.cryptography.shamir import ShamirScheme
from shamir.randomness.finite_sampler import FiniteFieldSampler

"""Testes de validação dos parâmetros do esquema."""

F17 = FiniteField(17)
SAMPLER = FiniteFieldSampler(F17)


def test_valid_parameters():
    scheme = ShamirScheme(F17, threshold=3, participants=5, sampler=SAMPLER)
    assert (scheme.threshold, scheme.participants) == (3, 5)
    ShamirScheme(F17, threshold=16, participants=16, sampler=SAMPLER)  # caso limite n = p - 1


def test_standard_scheme_explicitly_requires_a_prime_field():
    for arithmetic in (IntegerModRing(12), IntegerModRing(17), None):
        with pytest.raises(TypeError, match="FiniteField"):
            ShamirScheme(arithmetic, 3, 5, SAMPLER)


@pytest.mark.parametrize("k, n", [(0, 5), (6, 5), (3, 17), (3, 20)])
def test_invalid_parameters(k, n):
    with pytest.raises(ValueError):
        ShamirScheme(F17, threshold=k, participants=n, sampler=SAMPLER)
    for invalid in (True, 2.5, "3", None):
        with pytest.raises(TypeError):
            ShamirScheme(F17, invalid, 5, SAMPLER)
        with pytest.raises(TypeError):
            ShamirScheme(F17, 3, invalid, SAMPLER)


def test_invalid_secret():
    scheme = ShamirScheme(F17, threshold=3, participants=5, sampler=SAMPLER)
    scheme.validate_secret(0)
    scheme.validate_secret(16)
    for s in (-1, 17, 100):
        with pytest.raises(ValueError):
            scheme.validate_secret(s)
    for invalid in ("8", 8.0, True, None):
        with pytest.raises(TypeError):
            scheme.validate_secret(invalid)


def test_sampler_range():
    valores = {SAMPLER.sample() for _ in range(2000)}
    assert valores <= set(range(17))
    # Cobertura do intervalo sem depender da sorte de uma execução.
    with patch("shamir.randomness.finite_sampler.secrets.randbelow", side_effect=range(17)) as draw:
        assert [SAMPLER.sample() for _ in range(17)] == list(range(17))
        assert all(call.args == (17,) for call in draw.call_args_list)
