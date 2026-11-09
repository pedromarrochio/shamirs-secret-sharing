import pytest

from shamir.algebra.finite_field import FiniteField
from shamir.algebra.integer_mod_ring import IntegerModRing, NonInvertibleElementError
from shamir.cryptography.reconstruction import lagrange_coefficients

"""Testes do anel Z_m composto e da falha da interpolação."""

Z12 = IntegerModRing(12)


def test_units_of_z12():
    # em Z_12 só têm inverso os elementos coprimos com 12
    assert [a for a in range(12) if Z12.is_unit(a)] == [1, 5, 7, 11]
    for a in (1, 5, 7, 11):
        assert Z12.multiply(a, Z12.inverse(a)) == 1


def test_missing_inverse():
    with pytest.raises(NonInvertibleElementError) as info:
        Z12.inverse(4)
    assert (info.value.element, info.value.gcd) == (4, 4)


def test_lagrange_fails_in_composite_ring():
    # o mesmo conjunto de pontos funciona em Z_17 e falha em Z_12
    assert lagrange_coefficients([1, 2, 4], 0, FiniteField(17)) == [14, 15, 6]
    with pytest.raises(NonInvertibleElementError) as info:
        lagrange_coefficients([1, 2, 4], 0, Z12)
    assert info.value.element == 3          # denominador (1-2)(1-4) = 3


def test_lagrange_works_when_differences_are_units():
    # em Z_15, os pontos 1, 2, 3 têm diferenças 1 e 2, ambas invertíveis
    Z15 = IntegerModRing(15)
    lambdas = lagrange_coefficients([1, 2, 3], 0, Z15)
    assert sum(lambdas) % 15 == 1