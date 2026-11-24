"""O limiar visto pela contagem de polinômios e de segredos compatíveis."""

from itertools import combinations

from shamir.algebra.integer_mod_ring import IntegerModRing
from shamir.algebra.polynomial import Polynomial
from shamir.cryptography.analysis import (
    MAX_ENUMERATION_WORK, compatible_secret_counts, observations_independent_of_secret,
)


def threshold_analysis(m: int, k: int, x_values: list[int], coefficients: list) -> list[dict]:
    """Analisa todos os subconjuntos dos fragmentos de um polinômio fixo.

    Limita a oito participantes: a quantidade de subconjuntos é exponencial.
    Além do limite de cada enumeração no núcleo, limita o trabalho total
    estimado para contagens e comparação de distribuições de todos os subconjuntos.
    """
    ring = IntegerModRing(m)
    polynomial = Polynomial(coefficients, ring)
    points = [(x, polynomial.evaluate(x)) for x in x_values]
    if len(points) > 8:
        raise ValueError("A análise do limiar admite no máximo 8 participantes.")
    # Valida k, orçamento, coordenadas e duplicatas antes de gerar subconjuntos.
    full_counts = compatible_secret_counts(m, k, points)
    if polynomial.degree >= k:
        raise ValueError("O polinômio precisa ter grau menor que k.")
    if 2 * 2 ** len(points) * m ** k * max(1, len(points)) > MAX_ENUMERATION_WORK:
        raise ValueError("Análise de todos os subconjuntos muito grande; reduza os parâmetros.")
    rows = []
    for count in range(len(points) + 1):
        for subset in combinations(points, count):
            counts = (full_counts if count == len(points)
                      else compatible_secret_counts(m, k, list(subset)))
            independent = (observations_independent_of_secret(m, k, [x for x, _ in subset])
                           if count < k else None)
            rows.append({"points": list(subset), "counts": counts, "independent": independent})
    return rows


def main(out=print):
    m, k = 5, 3
    rows = threshold_analysis(m, k, [1, 2, 3, 4], [2, 1, 4])
    out("=== Limiar 3 de 4 em Z_5: f(x) = 2 + x + 4x² ===")
    out(f"{'fragmentos':>10} {'subconjuntos':>12} {'segredos possíveis':>19} {'polinômios':>12}")
    for count in range(5):
        selected = [r for r in rows if len(r["points"]) == count]
        candidates = sorted({len(r["counts"]) for r in selected})
        polynomials = sorted({sum(r["counts"].values()) for r in selected})
        out(f"{count:>10} {len(selected):>12} {str(candidates):>19} {str(polynomials):>12}")
    out("Com 0, 1 ou 2 fragmentos, todos os 5 segredos continuam possíveis.")
    independent = all(row["independent"] for row in rows if len(row["points"]) < k)
    out("Comparação das distribuições completas de todo subconjunto abaixo de k: "
        + ("iguais para todos os segredos." if independent else "dependem do segredo."))
    out("Como os coeficientes são uniformes, as probabilidades observadas não dependem do segredo.")
    out("A partir de 3 fragmentos, o segredo é único. A recusa da API sozinha não prova sigilo.")


if __name__ == "__main__":
    main()
