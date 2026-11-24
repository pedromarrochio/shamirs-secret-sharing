import pytest
from unittest.mock import patch

from shamir.algebra.finite_field import FiniteField, is_prime, extended_gcd

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

    for invalid in (17.0, True, "17", None):
        with pytest.raises(TypeError):
            FiniteField(invalid)
    assert FiniteField(2).p == 2

def test_is_prime():
    primos = [n for n in range(50) if is_prime(n)]
    assert primos == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for composite in (-7, 0, 1, 561, 1105, 1729):
        assert not is_prime(composite)
    for invalid in (True, 17.0, "17", None):
        with pytest.raises(TypeError):
            is_prime(invalid)


def test_twelve_base_pseudoprime_is_rejected():
    composite = 318665857834031151167461
    assert composite == 399165290221 * 798330580441
    assert not is_prime(composite)
    with pytest.raises(ValueError, match="não é primo"):
        FiniteField(composite)


def test_thirteen_base_boundary_uses_additional_random_bases():
    # O próprio limite é pseudoprimo para as 13 bases fixas; 43 é testemunha.
    boundary = 3317044064679887385961981
    with patch("shamir.algebra.finite_field.secrets.randbelow", return_value=41) as draw:
        assert not is_prime(boundary)
    assert draw.call_count == 32
    assert all(call.args == (boundary - 3,) for call in draw.call_args_list)

def test_finite_field_operations():
    F = FiniteField(17)
    assert F.add(15, 9) == 7
    assert F.subtract(1, 2) == 16
    assert F.negate(5) == 12
    assert F.multiply(3, 6) == 1
    assert F.divide(8, 3) == 14
    assert F.normalize(-1) == 16
    assert F.normalize(34) == 0
    # Verifica as leis de corpo em todos os elementos de Z_5.
    small = FiniteField(5)
    for a in range(5):
        assert small.add(a, small.zero()) == a
        assert small.multiply(a, small.one()) == a
        assert small.add(a, small.negate(a)) == 0
        for b in range(5):
            assert small.add(a, b) == small.add(b, a)
            assert small.multiply(a, b) == small.multiply(b, a)
            for c in range(5):
                assert small.add(small.add(a, b), c) == small.add(a, small.add(b, c))
                assert small.multiply(small.multiply(a, b), c) == small.multiply(a, small.multiply(b, c))
                assert small.multiply(a, small.add(b, c)) == small.add(small.multiply(a, b), small.multiply(a, c))
    for invalid in (True, 1.5, "1", None):
        for operation in (F.normalize, F.negate, F.inverse):
            with pytest.raises(TypeError):
                operation(invalid)
        for operation in (F.add, F.subtract, F.multiply, F.divide):
            with pytest.raises(TypeError):
                operation(invalid, 1)
            with pytest.raises(TypeError):
                operation(1, invalid)

def test_finite_field_inverse():
    F = FiniteField(17)
    assert F.inverse(3) == 6
    assert F.inverse(15) == 8
    assert F.inverse(-2) == 8
    for a in range(1, 17):
        assert F.multiply(a, F.inverse(a)) == 1
    with pytest.raises(ZeroDivisionError):
        F.inverse(0)
    with pytest.raises(ZeroDivisionError):
        F.divide(8, 17)
    for a, b, expected in ((30, 18, 6), (-30, 18, 6), (30, -18, 6), (0, 7, 7), (0, 0, 0)):
        gcd, u, v = extended_gcd(a, b)
        assert gcd == expected
        assert a * u + b * v == gcd
