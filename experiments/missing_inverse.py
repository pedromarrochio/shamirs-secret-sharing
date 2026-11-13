from itertools import combinations
from math import comb

from shamir.algebra.finite_field import FiniteField, is_prime
from shamir.algebra.integer_mod_ring import IntegerModRing, NonInvertibleElementError
from shamir.algebra.polynomial import Polynomial
from shamir.cryptography.reconstruction import lagrange_coefficients

"""Experimento: a interpolação de Lagrange falha em Z_m com m composto.

Em Z_p (p primo) todo elemento não nulo tem inverso. Em Z_m composto, um
elemento a só tem inverso quando mdc(a, m) = 1. Os coeficientes de Lagrange
exigem dividir por (x_j - x_m); quando alguma dessas diferenças não é
invertível, a reconstrução simplesmente não pode ser calculada.
"""

def reconstruction_attempt(ring, coefficients: list, x_values: list) -> dict:
    """Gera os fragmentos de f nos pontos dados e tenta recuperar f(0)."""
    
    f = Polynomial(coefficients, ring)
    shares = [(x, f.evaluate(x)) for x in x_values]
    result = {"shares": shares, "secret": f.evaluate(0)}

    try:
        Ls = lagrange_coefficients(x_values, 0, ring)
    except NonInvertibleElementError as error:
        result.update(success=False, element=error.element, gcd=error.gcd)
        return result

    recovered = ring.zero()
    for (_, y), lam in zip(shares, Ls):
        recovered = ring.add(recovered, ring.multiply(y, lam))
    result.update(success=True, lambdas=Ls, recovered=recovered)
    return result


def reconstructible_fraction(m: int, k: int) -> tuple[int, int]:
    """Conta quantos conjuntos de k abscissas em {1, ..., m-1} permitem
    calcular os coeficientes de Lagrange em Z_m.

    Devolve (quantidade que funciona, total de conjuntos).
    """
    ring = IntegerModRing(m)
    if not isinstance(k, int) or isinstance(k, bool):
        raise TypeError("O número de pontos precisa ser inteiro.")
    if not 1 <= k < m:
        raise ValueError("O número de pontos precisa estar entre 1 e m - 1.")
    ok = 0
    for xs in combinations(range(1, m), k):
        try:
            lagrange_coefficients(list(xs), 0, ring)
            ok += 1
        except NonInvertibleElementError:
            pass
    return ok, comb(m - 1, k)


def ambiguity_example(m: int = 12) -> dict:
    """Dois polinômios de grau <= 2 em Z_12 que coincidem em todos os x
    ímpares, mas têm termos constantes (segredos) diferentes.

    f(x) = 2x² + 5x + 8    e    g(x) = f(x) + 6(x + 1)

    Para x ímpar, x + 1 é par, então 6(x + 1) é múltiplo de 12, ou seja, 0 em Z_12.
    """

    if not isinstance(m, int) or isinstance(m, bool) or m != 12:
        raise ValueError("Este exemplo de ambiguidade foi construído para módulo 12.")
    ring = IntegerModRing(m)
    f = Polynomial([8, 5, 2], ring)
    g = Polynomial([8 + 6, 5 + 6, 2], ring)
    odd_points = list(range(1, m, 2))
    return {
        "points": odd_points,
        "f_values": [f.evaluate(x) for x in odd_points],
        "g_values": [g.evaluate(x) for x in odd_points],
        "f_secret": f.evaluate(0),
        "g_secret": g.evaluate(0),
    }


def main():
    coefficients = [8, 5, 2]          # f(x) = 2x² + 5x + 8, o exemplo feito à mão
    points = [1, 2, 4]

    print("=== 1. Mesmo polinômio e mesmos pontos, em Z_17 e em Z_12 ===")
    for ring, name in ((FiniteField(17), "Z_17"), (IntegerModRing(12), "Z_12")):
        r = reconstruction_attempt(ring, coefficients, points)
        print(f"\n{name}: fragmentos {r['shares']}, segredo verdadeiro {r['secret']}")
        if r["success"]:
            print(f"  L's = {r['lambdas']} -> segredo recuperado = {r['recovered']}")
        else:
            print(f"  FALHOU: o denominador {r['element']} não tem inverso "
                  f"(mdc({r['element']}, {ring.m}) = {r['gcd']})")

    print("\n=== 2. Quantos conjuntos de 3 pontos permitem a reconstrução? ===")
    print(f"{'m':>4} {'tipo':>9} {'funcionam':>10} {'total':>6} {'fração':>8}")
    for m in (12, 13, 15, 16, 17, 21, 25, 29, 35):
        ok, total = reconstructible_fraction(m, 3)
        kind = "primo" if is_prime(m) else "composto"
        print(f"{m:>4} {kind:>9} {ok:>10} {total:>6} {ok / total:>8.1%}")

    print("\n=== 3. Ambiguidade: mesmos fragmentos, segredos diferentes ===")
    a = ambiguity_example()
    print(f"pontos x:      {a['points']}")
    print(f"f(x) mod 12:   {a['f_values']}   segredo f(0) = {a['f_secret']}")
    print(f"g(x) mod 12:   {a['g_values']}   segredo g(0) = {a['g_secret']}")


if __name__ == "__main__":
    main()
