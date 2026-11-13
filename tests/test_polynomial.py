from unittest.mock import Mock

import pytest

from shamir.algebra.finite_field import FiniteField
from shamir.algebra.polynomial import Polynomial
from shamir.randomness.finite_sampler import FiniteFieldSampler


"""Testes para operações com polinômios."""
F17 = FiniteField(17)

def test_polynomial_creation():
    # f(x) = 2x² + 5x + 8  ->  coeficientes do menor para o maior grau
    f = Polynomial([8, 5, 2], F17)
    assert f.coefficients == [8, 5, 2]
    assert f.degree == 2

    # coeficientes fora de 0..16 são reduzidos mod 17
    g = Polynomial([25, -1, 17], F17)
    assert g.coefficients == [8, 16, 0]
    assert g.degree == 1  # o coeficiente de x² virou 0
    with pytest.raises(ValueError):
        Polynomial([], F17)
    zero = Polynomial([0, 0, 0], F17)
    assert zero.degree == -1
    assert all(zero.evaluate(x) == 0 for x in range(17))
    constant = Polynomial([8, 0, 0], F17)
    assert constant.degree == 0
    assert all(constant.evaluate(x) == 8 for x in range(17))


def test_polynomial_evaluation():
    # exemplo feito à mão: f(x) = 2x² + 5x + 8 em Z_17
    f = Polynomial([8, 5, 2], F17)
    esperados = {0: 8, 1: 15, 2: 9, 3: 7, 4: 9, 5: 15}
    for x, y in esperados.items():
        assert f.evaluate(x) == y
        assert f.evaluate(x + 17) == y
        assert f.evaluate(x - 17) == y


def test_polynomial_operations():
    # polinômio aleatório: grau certo e segredo no termo constante
    sampler = FiniteFieldSampler(F17)
    f = Polynomial.random(F17, sampler, degree=2, constant_term=8)
    assert len(f.coefficients) == 3
    assert f.evaluate(0) == 8
    deterministic = Mock()
    deterministic.sample.side_effect = [5, 0]
    reduced = Polynomial.random(F17, deterministic, degree=2, constant_term=8)
    assert reduced.coefficients == [8, 5, 0]
    assert reduced.degree == 1
    assert deterministic.sample.call_count == 2
    deterministic.reset_mock()
    constant = Polynomial.random(F17, deterministic, degree=0, constant_term=8)
    assert constant.coefficients == [8]
    deterministic.sample.assert_not_called()
    with pytest.raises(ValueError):
        Polynomial.random(F17, deterministic, -1, 8)
    for invalid in (True, 1.5, "2", None):
        with pytest.raises(TypeError):
            Polynomial.random(F17, deterministic, invalid, 8)
