import pytest

from shamir.algebra.finite_field import FiniteField
from shamir.algebra.polynomial import Polynomial
from shamir.cryptography.reconstruction import (
    lagrange_coefficients, lagrange_interpolation, interpolate_at_zero,
)
from shamir.cryptography.share import Share

"""Testes para interpolação de Lagrange."""

F17 = FiniteField(17)

def test_lagrange_coefficients_example():
    # exemplo feito à mão: pontos x = 1, 2, 4 em Z_17, avaliados em 0
    assert lagrange_coefficients([1, 2, 4], 0, F17) == [14, 15, 6]

def test_lagrange_coefficients_sum_to_one():
    # interpolar o polinômio constante 1 tem de dar 1, em qualquer ponto
    for xs in ([1, 2, 4], [3, 5, 9, 16], [7]):
        for x in range(17):
            assert sum(lagrange_coefficients(xs, x, F17)) % 17 == 1

def test_lagrange_basis_property():
    # L_j(x_i) = 1 se i == j e 0 caso contrário
    xs = [2, 5, 11, 13]
    for i, xi in enumerate(xs):
        expected = [1 if j == i else 0 for j in range(len(xs))]
        assert lagrange_coefficients(xs, xi, F17) == expected


def test_lagrange_coefficients_recover_polynomial():
    # sum y_j * L_j(0) recupera f(0) = 8, para qualquer trio de pontos
    f = Polynomial([8, 5, 2], F17)
    for xs in ([1, 2, 4], [1, 3, 5], [2, 3, 4], [6, 10, 15]):
        lambdas = lagrange_coefficients(xs, 0, F17)
        ys = [f.evaluate(xj) for xj in xs]
        assert sum(y * l for y, l in zip(ys, lambdas)) % 17 == 8


def test_lagrange_coefficients_invalid_points():
    with pytest.raises(ValueError):
        lagrange_coefficients([], 0, F17)
    with pytest.raises(ValueError):
        lagrange_coefficients([1, 2, 1], 0, F17)
    with pytest.raises(ValueError):
        lagrange_coefficients([1, 18], 0, F17)   # 18 ≡ 1 em Z_17

def test_lagrange_interpolation():
    polynomial = Polynomial([8, 5, 2], F17)
    shares = [Share(x, polynomial.evaluate(x), 17) for x in (1, 2, 4)]
    for x in range(17):
        assert lagrange_interpolation(shares, x, F17) == polynomial.evaluate(x)
    for invalid in ([], [shares[0], shares[0]], [shares[0], Share(2, 9, 19)]):
        with pytest.raises(ValueError):
            lagrange_interpolation(invalid, 0, F17)
    with pytest.raises(TypeError):
        lagrange_interpolation([None], 0, F17)
    with pytest.raises(ValueError, match="módulo"):
        lagrange_interpolation([Share(1, 5, 19)], 0, F17)


def test_interpolation_at_zero():
    assert interpolate_at_zero([Share(1, 15, 17), Share(2, 9, 17), Share(4, 9, 17)], F17) == 8
    assert interpolate_at_zero([Share(1, 8, 17)], F17) == 8
    assert interpolate_at_zero([Share(1, 0, 17)], F17) == 0
    with pytest.raises(ValueError):
        interpolate_at_zero([], F17)
