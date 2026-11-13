import pytest

from shamir.algebra.finite_field import FiniteField
from shamir.algebra.integer_mod_ring import IntegerModRing, NonInvertibleElementError
from shamir.algebra.polynomial import Polynomial
from shamir.cryptography.reconstruction import lagrange_coefficients

"""Testes do anel Z_m composto e da falha da interpolação."""

Z12 = IntegerModRing(12)


def test_units_of_z12():
    for invalid in (1, 0, -12, True, 12.0, "12"):
        with pytest.raises(ValueError):
            IntegerModRing(invalid)
    assert Z12.normalize(-1) == 11
    assert Z12.add(11, 2) == 1
    assert Z12.subtract(1, 2) == 11
    assert Z12.multiply(3, 4) == 0
    assert Z12.divide(10, 5) == 2
    assert (Z12.zero(), Z12.one()) == (0, 1)
    for invalid in (True, 1.5, "1", None):
        with pytest.raises(TypeError):
            Z12.normalize(invalid)
    # em Z_12 só têm inverso os elementos coprimos com 12
    assert [a for a in range(12) if Z12.is_unit(a)] == [1, 5, 7, 11]
    for a in (1, 5, 7, 11):
        assert Z12.multiply(a, Z12.inverse(a)) == 1


def test_missing_inverse():
    with pytest.raises(NonInvertibleElementError) as info:
        Z12.inverse(4)
    assert (info.value.element, info.value.gcd) == (4, 4)
    for value in (0, 2, 3, 4, 6, 8, 9, 10):
        with pytest.raises(NonInvertibleElementError):
            Z12.inverse(value)
        with pytest.raises(NonInvertibleElementError):
            Z12.divide(1, value)


def test_lagrange_fails_in_composite_ring():
    # o mesmo conjunto de pontos funciona em Z_17 e falha em Z_12
    assert lagrange_coefficients([1, 2, 4], 0, FiniteField(17)) == [14, 15, 6]
    with pytest.raises(NonInvertibleElementError) as info:
        lagrange_coefficients([1, 2, 4], 0, Z12)
    assert info.value.element == 3          # denominador (1-2)(1-4) = 3
    # Mesmo seis fragmentos podem corresponder a segredos diferentes em Z_12.
    f = Polynomial([8, 5, 2], Z12)
    g = Polynomial([14, 11, 2], Z12)
    assert all(f.evaluate(x) == g.evaluate(x) for x in range(1, 12, 2))
    assert f.evaluate(0) != g.evaluate(0)


def test_lagrange_works_when_differences_are_units():
    # em Z_15, os pontos 1, 2, 3 têm diferenças 1 e 2, ambas invertíveis
    Z15 = IntegerModRing(15)
    lambdas = lagrange_coefficients([1, 2, 3], 0, Z15)
    assert sum(lambdas) % 15 == 1