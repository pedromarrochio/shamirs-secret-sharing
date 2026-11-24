"""Experimento: certas coordenadas em Z_m composto vazam informação (k >= 2).

Em Z_p (p primo), um único fragmento (x, f(x)) é compatível com todos os
segredos: para cada segredo s existe o mesmo número de polinômios que passam
por (0, s) e (x, f(x)). Para vários fragmentos, o sigilo exige comparar a
distribuição conjunta; apenas comparar cada fragmento isoladamente não basta.

Em Z_m composto, coordenadas não invertíveis podem quebrar essa propriedade.
Escrevendo

    f(x) = s + a_1 x + ... + a_{k-1} x^{k-1} = s + x * (a_1 + a_2 x + ...),

vemos que f(x) - s é múltiplo de x em Z_m. Logo, com d = mdc(x, m),

    f(x) ≡ s  (mod d).

Ou seja, um único fragmento já revela o segredo módulo d. Em Z_12, um
fragmento com x = 6 reduz os 12 segredos possíveis a apenas 2.
"""

from collections import Counter
from math import gcd

from shamir.algebra.finite_field import is_prime
from shamir.algebra.integer_mod_ring import IntegerModRing
from shamir.algebra.polynomial import Polynomial
from shamir.cryptography.analysis import (
    observation_distribution, observations_independent_of_secret,
)


def _validate(m: int, k: int, x: int | None = None) -> None:
    for name, value in (("m", m), ("k", k)):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{name} precisa ser um inteiro.")
    if m < 2:
        raise ValueError("O módulo precisa ser pelo menos 2.")
    if k < 2:
        raise ValueError("O limiar precisa ser pelo menos 2 para haver fragmentos abaixo dele.")
    if x is not None:
        if not isinstance(x, int) or isinstance(x, bool):
            raise TypeError("x precisa ser um inteiro.")
        if not 1 <= x < m:
            raise ValueError(f"x precisa estar entre 1 e {m - 1}.")


def share_distribution(m: int, x: int, secret: int, k: int = 3) -> Counter:
    """Distribuição de f(x) sobre todos os polinômios de grau <= k-1 com f(0) = secret.

    Enumera as m^(k-1) escolhas de coeficientes e conta quantas vezes cada
    valor f(x) aparece.
    """
    _validate(m, k, x)
    return Counter({values[0]: count for values, count in
                    observation_distribution(m, k, [x], secret).items()})


def candidate_secrets(m: int, x: int, y: int, k: int = 3) -> list[int]:
    """Segredos compatíveis com o fragmento observado (x, y).

    Um segredo s é compatível se algum polinômio de grau <= k-1 com
    f(0) = s satisfaz f(x) = y.
    """
    _validate(m, k, x)
    y = IntegerModRing(m).normalize(y)
    # Como a_1 é livre, s ≡ y (mod d) também é suficiente, não só necessário.
    d = gcd(x, m)
    return list(range(y % d, m, d))


def leakage_table(m: int, k: int = 3) -> list[dict]:
    """Para cada abscissa x, quanto um único fragmento revela sobre o segredo."""
    _validate(m, k)
    rows = []
    for x in range(1, m):
        d = gcd(x, m)
        rows.append({
            "x": x,
            "gcd": d,
            "candidates": m // d,
        })
    return rows


def is_uniform_and_independent(m: int, x: int, k: int = 3) -> bool:
    """Diz se a distribuição de f(x) é a mesma para todos os segredos."""
    _validate(m, k, x)
    return observations_independent_of_secret(m, k, [x])


def print_prime_vs_composite(out=print, k: int = 3) -> None:
    _validate(12, k, 6)
    out(f"=== 1. Um único fragmento em x = 6 (limiar k = {k}) ===")
    for m in (13, 12):
        kind = "primo" if is_prime(m) else "composto"
        secret = 5
        independent = is_uniform_and_independent(m, 6, k)
        # O exemplo deve respeitar o grau < k mesmo se k for alterado.
        tail = ([7, 3] + [0] * (k - 1))[:k - 1]
        polynomial = Polynomial([secret, *tail], IntegerModRing(m))
        y = polynomial.evaluate(6)
        candidates = candidate_secrets(m, 6, y, k)
        out(f"\nZ_{m} ({kind}): segredo verdadeiro {secret}, f(x) = {polynomial}")
        out(f"  Fragmento observado: (6, {y})")
        out(f"  Segredos ainda possíveis: {candidates} ({len(candidates)} de {m})")
        out(f"  Distribuição de f(6) igual para todo segredo? {'sim' if independent else 'não'}")


def print_leakage_table(out=print, m: int = 12, k: int = 3) -> None:
    out(f"=== 2. O que um fragmento (x, f(x)) revela em Z_{m} ===")
    out(f"{'x':>4} {'mdc(x, m)':>10} {'revela':>12} {'segredos possíveis':>20}")
    for row in leakage_table(m, k):
        revealed = "nada" if row["gcd"] == 1 else f"s mod {row['gcd']}"
        out(f"{row['x']:>4} {row['gcd']:>10} {revealed:>12} {row['candidates']:>20}")
    out("\nExplicação: f(x) - s = x(a_1 + a_2 x + ...) é múltiplo de x,")
    out("então f(x) ≡ s (mod mdc(x, m)). Num corpo, mdc(x, p) = 1 e nada vaza.")


def main():
    print_prime_vs_composite()
    print()
    print_leakage_table()


if __name__ == "__main__":
    main()
