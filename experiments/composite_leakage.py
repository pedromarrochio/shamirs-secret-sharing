"""Experimento: em Z_m composto, menos de k fragmentos vazam informação.

Em Z_p (p primo), um único fragmento (x, f(x)) é compatível com todos os
segredos: para cada segredo s existe o mesmo número de polinômios que passam
por (0, s) e (x, f(x)). Por isso, menos de k fragmentos não revelam nada.

Em Z_m composto isso deixa de valer. Escrevendo

    f(x) = s + a_1 x + ... + a_{k-1} x^{k-1} = s + x * (a_1 + a_2 x + ...),

vemos que f(x) - s é múltiplo de x em Z_m. Logo, com d = mdc(x, m),

    f(x) ≡ s  (mod d).

Ou seja, um único fragmento já revela o segredo módulo d. Em Z_12, um
fragmento com x = 6 reduz os 12 segredos possíveis a apenas 2.
"""

from collections import Counter
from itertools import product
from math import gcd

from shamir.algebra.finite_field import is_prime
from shamir.algebra.integer_mod_ring import IntegerModRing
from shamir.algebra.polynomial import Polynomial


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
    ring = IntegerModRing(m)
    counts = Counter()
    for coefficients in product(range(m), repeat=k - 1):
        f = Polynomial([secret, *coefficients], ring)
        counts[f.evaluate(x)] += 1
    return counts


def candidate_secrets(m: int, x: int, y: int, k: int = 3) -> list[int]:
    """Segredos compatíveis com o fragmento observado (x, y).

    Um segredo s é compatível se algum polinômio de grau <= k-1 com
    f(0) = s satisfaz f(x) = y.
    """
    _validate(m, k, x)
    return [s for s in range(m) if share_distribution(m, x, s, k)[y % m] > 0]


def leakage_table(m: int, k: int = 3) -> list[dict]:
    """Para cada abscissa x, quanto um único fragmento revela sobre o segredo."""
    _validate(m, k)
    rows = []
    for x in range(1, m):
        y = share_distribution(m, x, 0, k).most_common(1)[0][0]
        candidates = candidate_secrets(m, x, y, k)
        rows.append({
            "x": x,
            "gcd": gcd(x, m),
            "candidates": len(candidates),
        })
    return rows


def is_uniform_and_independent(m: int, x: int, k: int = 3) -> bool:
    """Diz se a distribuição de f(x) é a mesma para todos os segredos."""
    _validate(m, k, x)
    reference = share_distribution(m, x, 0, k)
    return all(share_distribution(m, x, s, k) == reference for s in range(1, m))


def print_prime_vs_composite(out=print, k: int = 3) -> None:
    out(f"=== 1. Um único fragmento em x = 6 (limiar k = {k}) ===")
    for m in (13, 12):
        kind = "primo" if is_prime(m) else "composto"
        secret = 5
        y = Polynomial([secret, 7, 3], IntegerModRing(m)).evaluate(6)
        candidates = candidate_secrets(m, 6, y, k)
        independent = is_uniform_and_independent(m, 6, k)
        out(f"\nZ_{m} ({kind}): segredo verdadeiro {secret}, f(x) = {secret} + 7x + 3x²")
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