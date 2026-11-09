import pytest

from shamir.algebra.finite_field import FiniteField, is_prime

"""Testes para a implementação de corpos finitos."""


def test_finite_field_creation():
    F = FiniteField(17)
    assert F.p == 17

    # primo grande (primo de Mersenne 2^127 - 1) é aceito sem travar
    assert FiniteField(2**127 - 1).p == 2**127 - 1

    # números que não são primos são recusados
    for n in (0, 1, 12, 561, 2**127 + 1):   # 561 é número de Carmichael
        with pytest.raises(ValueError):
            FiniteField(n)

    with pytest.raises(TypeError):
        FiniteField(17.0)

def test_is_prime():
    primos = [n for n in range(50) if is_prime(n)]
    assert primos == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

def test_finite_field_operations():
    F = FiniteField(17)
    assert F.add(15, 9) == 7
    assert F.subtract(1, 2) == 16
    assert F.negate(5) == 12
    assert F.multiply(3, 6) == 1
    assert F.divide(8, 3) == 14 

def test_finite_field_inverse():
    F = FiniteField(17)
    assert F.inverse(3) == 6
    assert F.inverse(15) == 8
    assert F.inverse(-2) == 8
    for a in range(1, 17):
        assert F.multiply(a, F.inverse(a)) == 1
    with pytest.raises(ZeroDivisionError):
        F.inverse(0)
