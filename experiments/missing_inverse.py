"""Denominadores de Lagrange e ambiguidade em anéis modulares.

Em Z_m, a é invertível exatamente quando mdc(a, m) = 1. Uma divisão
impossível impede esta fórmula de Lagrange; não prova, por si só, que o
segredo seja ambíguo. Veja também experiments/ring_comparison.py.
"""

from itertools import combinations
from math import comb

from shamir.algebra.finite_field import FiniteField, is_prime
from shamir.algebra.integer_mod_ring import IntegerModRing, NonInvertibleElementError
from shamir.algebra.polynomial import Polynomial
from shamir.cryptography.reconstruction import lagrange_coefficients

def reconstruction_attempt(ring, coefficients: list, x_values: list) -> dict:
    """Tenta recuperar f(0) pela fórmula de Lagrange, sem outros métodos.

    `success=False` significa apenas falha desta fórmula, não indeterminação
    do segredo. Exige mais pontos que o grau do polinômio fornecido.
    """
    
    f = Polynomial(coefficients, ring)
    if len(x_values) <= f.degree:
        raise ValueError("São necessários mais pontos que o grau do polinômio.")
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


def lagrange_applicable_fraction(m: int, k: int) -> tuple[int, int]:
    """Conta quantos conjuntos de k abscissas em {1, ..., m-1} permitem
    calcular os coeficientes de Lagrange em Z_m.

    Devolve (quantidade que permite a fórmula, total de conjuntos). Não mede
    todos os métodos de recuperação nem a segurança abaixo do limiar.
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
            print("  A fórmula falhou; é preciso outra análise para decidir se o segredo é único.")

    print("\n=== 2. Quantos conjuntos de 3 pontos permitem a fórmula de Lagrange? ===")
    print(f"{'m':>4} {'tipo':>9} {'funcionam':>10} {'total':>6} {'fração':>8}")
    for m in (12, 13, 15, 16, 17, 21, 25, 29, 35):
        ok, total = lagrange_applicable_fraction(m, 3)
        kind = "primo" if is_prime(m) else "composto"
        print(f"{m:>4} {kind:>9} {ok:>10} {total:>6} {ok / total:>8.1%}")
    print("A tabela mede denominadores invertíveis, não determinação do segredo ou sigilo.")

    print("\n=== 3. Ambiguidade: mesmos fragmentos, segredos diferentes ===")
    a = ambiguity_example()
    print(f"pontos x:      {a['points']}")
    print(f"f(x) mod 12:   {a['f_values']}   segredo f(0) = {a['f_secret']}")
    print(f"g(x) mod 12:   {a['g_values']}   segredo g(0) = {a['g_secret']}")
    print("Nesses pontos ímpares o segredo é ambíguo; não é uma afirmação sobre todo conjunto em Z_12.")


if __name__ == "__main__":
    main()
