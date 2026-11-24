"""Reconstrução, unicidade e sigilo: três perguntas diferentes."""

from itertools import combinations

from shamir.algebra.finite_field import FiniteField
from shamir.algebra.integer_mod_ring import IntegerModRing
from shamir.algebra.polynomial import Polynomial
from shamir.cryptography.analysis import (
    compatible_secret_counts,
    has_unit_separations,
    observations_independent_of_secret,
)
from shamir.cryptography.shamir import ShamirScheme
from shamir.cryptography.share import Share
from shamir.randomness.finite_sampler import FiniteFieldSampler

from experiments.missing_inverse import reconstruction_attempt


def comparison_cases() -> list[dict]:
    """Mesmo segredo e grau admitido, variando módulo e coordenadas."""
    rows = []
    for m, xs in ((17, [1, 2, 4]), (12, [1, 2, 4]), (12, [1, 2, 3]),
                  (12, [1, 3, 5]), (15, [1, 2, 3]), (25, [1, 2, 3])):
        attempt = reconstruction_attempt(IntegerModRing(m), [8, 5, 2], xs)
        counts = compatible_secret_counts(m, 3, attempt["shares"])
        rows.append({"modulus": m, "xs": xs, "lagrange": attempt["success"],
                     "polynomials": sum(counts.values()), "secrets": sorted(counts)})
    return rows


def division_free_example() -> dict:
    ring = IntegerModRing(12)
    polynomial = Polynomial([8, 5, 2], ring)
    points = [(x, polynomial.evaluate(x)) for x in (1, 2, 3)]
    counts = compatible_secret_counts(12, 3, points)
    ys = [y for _, y in points]
    recovered = (3 * ys[0] - 3 * ys[1] + ys[2]) % 12
    return {"points": points, "counts": counts, "recovered": recovered,
            "lagrange": reconstruction_attempt(ring, [8, 5, 2], [1, 2, 3])["success"]}


def composite_success_example() -> dict:
    """Verifica todos os trios e todos os subconjuntos abaixo de k em Z_25."""
    m, k, xs = 25, 3, [1, 2, 3, 4]
    ring = IntegerModRing(m)
    polynomial = Polynomial([8, 5, 2], ring)
    recoveries = [reconstruction_attempt(ring, polynomial.coefficients, list(subset))
                  for subset in combinations(xs, k)]
    privacy = {
        subset: observations_independent_of_secret(m, k, subset)
        for count in range(k) for subset in combinations(xs, count)
    }
    return {"points": [(x, polynomial.evaluate(x)) for x in xs],
            "unit_separations": has_unit_separations(m, xs),
            "recoveries": recoveries, "privacy": privacy}


def tampering_example() -> dict:
    """Fragmentos válidos em formato podem pertencer a distribuições distintas."""
    field = FiniteField(17)
    scheme = ShamirScheme(field, 3, 5, FiniteFieldSampler(field))
    original = Polynomial([8, 5, 2], field)
    other = Polynomial([3, 7, 1], field)
    shares = [Share(x, original.evaluate(x), 17) for x in (1, 2, 4)]
    changed = [*shares[:2], Share(4, (shares[2].y + 1) % 17, 17)]
    mixed = [*shares[:2], Share(4, other.evaluate(4), 17)]
    return {"original_shares": shares, "changed_shares": changed, "mixed_shares": mixed,
            "original": scheme.reconstruct(shares), "changed": scheme.reconstruct(changed),
            "mixed": scheme.reconstruct(mixed)}


def print_comparison(out=print) -> None:
    out("=== Mesmo f(x) = 8 + 5x + 2x²; grau admitido <= 2 (k = 3) ===")
    out(f"{'m':>3} {'pontos x':>12} {'Lagrange':>10} {'polinômios':>11} {'segredos possíveis':>20}")
    for row in comparison_cases():
        out(f"{row['modulus']:>3} {str(row['xs']):>12} "
            f"{('sim' if row['lagrange'] else 'não'):>10} {row['polynomials']:>11} "
            f"{str(row['secrets']):>20}")
    out("Lagrange: apenas a fórmula com denominadores invertíveis.")
    out("Polinômios: contagem exata de todas as escolhas de coeficientes compatíveis.")
    out("Segredos: termos constantes distintos desses polinômios.")
    out("Em Z_12 com x = 1, 2, 3 há dois polinômios, mas só um segredo.")
    out("Em Z_15 com x = 1, 2, 3 a fórmula funciona, mas x = 3 revela s mod 3.")
    out("Determinar o segredo com k fragmentos não garante sigilo com menos de k.")


def print_division_free(out=print) -> None:
    result = division_free_example()
    out("=== Z_12: falha de Lagrange não implica segredo ambíguo ===")
    out("Grau admitido <= 2, k = 3; f(x) = 8 + 5x + 2x².")
    out(f"Fragmentos: {result['points']}")
    out("A fórmula de Lagrange tenta inverter 2, que não tem inverso em Z_12.")
    out("Por enumeração, os polinômios compatíveis são 8 + 5x + 2x² e 8 + 11x + 8x².")
    out(f"Polinômios compatíveis: {sum(result['counts'].values())}; "
        f"segredos possíveis: {sorted(result['counts'])}.")
    out("Para qualquer f de grau <= 2, a identidade 3f(1) - 3f(2) + f(3) = f(0)")
    out("cancela os termos em x e x², sem divisão:")
    out(f"  f(0) = (3·3 - 3·2 + 5) mod 12 = {result['recovered']}")
    out("O polinômio não é único, mas o segredo é. Isso não estabelece sigilo abaixo de k.")


def print_composite_success(out=print) -> None:
    result = composite_success_example()
    out("=== Z_25: anel composto com limiar 3 de 4 e pontos adequados ===")
    out("f(x) = 8 + 5x + 2x²; coordenadas 1, 2, 3, 4.")
    out(f"Fragmentos: {result['points']}")
    out("Unidade = elemento com inverso; em Z_25, são os que não são múltiplos de 5.")
    out("Os pontos e todas as diferenças entre eles são unidades.")
    out("Condição suficiente, incluindo o ponto secreto 0: "
        + ("satisfeita" if result["unit_separations"] else "não satisfeita"))
    for attempt in result["recoveries"]:
        xs = [x for x, _ in attempt["shares"]]
        out(f"  Trio {xs}: segredo recuperado = {attempt['recovered']}")
    for count in range(3):
        checks = [valid for xs, valid in result["privacy"].items() if len(xs) == count]
        out(f"  Com {count} fragmento(s): {len(checks)} subconjunto(s), "
            f"distribuições iguais para todos os 25 segredos? {'sim' if all(checks) else 'não'}")
    out("A comparação é conjunta e enumera todos os coeficientes, inclusive zero.")
    out("Ser primo garante inversos para quaisquer diferenças não nulas.")
    out("Em um anel composto, essa garantia depende dos pontos; aqui a condição é satisfeita.")
    out("Z_25 continua sendo um anel com divisores de zero, e não o corpo GF(25).")


def print_tampering(out=print) -> None:
    result = tampering_example()
    out("=== Limitação: fragmentos sem autenticação ===")
    out(f"Originais: {[(s.x, s.y) for s in result['original_shares']]} -> segredo {result['original']}")
    out(f"Um valor y adulterado: {[(s.x, s.y) for s in result['changed_shares']]} "
        f"-> resultado {result['changed']}")
    out(f"Um fragmento de outra distribuição: {[(s.x, s.y) for s in result['mixed_shares']]} "
        f"-> resultado {result['mixed']}")
    out("Os pontos têm formato válido e o mesmo módulo, mas o programa não detecta a troca.")
    out("Com exatamente k pontos distintos há sempre um interpolador de grau < k em Z_p.")
    out("Shamir protege o sigilo; autenticidade dos fragmentos exige um mecanismo adicional.")


def main():
    for demonstration in (print_comparison, print_division_free,
                          print_composite_success, print_tampering):
        demonstration()
        print()


if __name__ == "__main__":
    main()
