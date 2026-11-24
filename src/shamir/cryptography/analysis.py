"""Enumeração exata para estudar exemplos modulares pequenos.

Contar candidatos investiga determinação do segredo; comparar distribuições
investiga sigilo. Não são testes intercambiáveis. Os limites evitam que uma
entrada interativa dispare uma enumeração impraticável.
"""

from collections import Counter
from itertools import combinations, product
from math import gcd

from ..algebra.integer_mod_ring import IntegerModRing
from ..algebra.polynomial import Polynomial
from .share import Share


MAX_ENUMERATION_WORK = 1_000_000


def _parameters(modulus: int, threshold: int) -> IntegerModRing:
    ring = IntegerModRing(modulus)
    if not isinstance(threshold, int) or isinstance(threshold, bool):
        raise TypeError("O limiar precisa ser um inteiro.")
    if threshold < 1:
        raise ValueError("O limiar precisa ser pelo menos 1.")
    return ring


def _coordinates(modulus: int, x_values) -> list[int]:
    xs = list(x_values)
    for x in xs:
        Share(x, 0, modulus)
    if len(set(xs)) != len(xs):
        raise ValueError("As abscissas precisam ser distintas.")
    return xs


def _check_budget(modulus: int, exponent: int, width: int) -> None:
    work = max(1, width)
    for _ in range(exponent):
        work *= modulus
        if work > MAX_ENUMERATION_WORK:
            raise ValueError(
                "Enumeração muito grande; reduza o módulo, o limiar ou os pontos "
                f"(limite de {MAX_ENUMERATION_WORK} avaliações estimadas)."
            )


def compatible_secret_counts(modulus: int, threshold: int,
                             points: list[tuple[int, int]]) -> Counter:
    """Conta polinômios de grau < threshold por segredo, dados os pontos.

    Um resultado vazio significa observações incompatíveis com o grau admitido.
    Mais de um polinômio pode corresponder a um mesmo segredo.
    """
    ring = _parameters(modulus, threshold)
    points = list(points)
    _coordinates(modulus, [x for x, _ in points])
    for x, y in points:
        Share(x, y, modulus)
    _check_budget(modulus, threshold, len(points))
    if not points:
        return Counter({s: modulus ** (threshold - 1) for s in range(modulus)})
    counts = Counter()
    for coefficients in product(range(modulus), repeat=threshold):
        polynomial = Polynomial(coefficients, ring)
        if all(polynomial.evaluate(x) == y for x, y in points):
            counts[coefficients[0]] += 1
    return counts


def _distribution(ring, threshold, xs, secret) -> Counter:
    observations = Counter()
    for tail in product(range(ring.m), repeat=threshold - 1):
        polynomial = Polynomial([secret, *tail], ring)
        observations[tuple(polynomial.evaluate(x) for x in xs)] += 1
    return observations


def observation_distribution(modulus: int, threshold: int, x_values,
                             secret: int) -> Counter:
    """Distribuição conjunta dos fragmentos, com coeficientes uniformes.

    As contagens têm denominador comum modulus^(threshold-1), inclusive
    quando o coeficiente de maior grau é zero.
    """
    ring = _parameters(modulus, threshold)
    xs = _coordinates(modulus, x_values)
    if not isinstance(secret, int) or isinstance(secret, bool):
        raise TypeError("O segredo precisa ser um inteiro.")
    if not 0 <= secret < modulus:
        raise ValueError("O segredo precisa estar entre 0 e m - 1.")
    _check_budget(modulus, threshold - 1, len(xs))
    return _distribution(ring, threshold, xs, secret)


def observations_independent_of_secret(modulus: int, threshold: int,
                                       x_values) -> bool:
    """Compara exatamente as distribuições para todos os segredos."""
    ring = _parameters(modulus, threshold)
    xs = _coordinates(modulus, x_values)
    _check_budget(modulus, threshold, len(xs))
    reference = _distribution(ring, threshold, xs, 0)
    return all(_distribution(ring, threshold, xs, s) == reference
               for s in range(1, modulus))


def has_unit_separations(modulus: int, x_values) -> bool:
    """Condição suficiente para Shamir: diferenças invertíveis incluindo 0.

    Incluir 0 exige que cada x_i seja unidade, além de cada x_i - x_j.
    Verificar apenas diferenças entre participantes não garante sigilo.
    """
    IntegerModRing(modulus)
    xs = [0, *_coordinates(modulus, x_values)]
    return all(gcd(a - b, modulus) == 1 for a, b in combinations(xs, 2))
