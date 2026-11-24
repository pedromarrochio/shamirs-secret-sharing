from ..algebra.finite_field import FiniteField
from ..algebra.integer_mod_ring import IntegerModRing
from ..algebra.polynomial import Polynomial
from .share import Share


ModularArithmetic = FiniteField | IntegerModRing


def _abscissas(x_values: list, field: ModularArithmetic) -> list:
    xs = [field.normalize(xi) for xi in x_values]
    if not xs:
        raise ValueError("É preciso pelo menos um ponto para interpolar.")
    if len(set(xs)) != len(xs):
        raise ValueError(
            "As abscissas precisam ser distintas no corpo ou anel "
            "(senão algum denominador x_j - x_m é zero)."
        )
    return xs


def lagrange_coefficients(x_values: list, x, field: ModularArithmetic) -> list:
    """Calcula L_j(x) quando todos os denominadores são invertíveis.

    Para abscissas distintas x_1, ..., x_k, devolve [L_1(x), ..., L_k(x)], com

        L_j(x) = prod_{m != j} (x - x_m) / (x_j - x_m).

    Com x = 0, são os coeficientes usados para reconstruir o segredo. Em um
    anel, uma falha desta fórmula não prova que o segredo seja indeterminado.
    """
    xs = _abscissas(x_values, field)
    x = field.normalize(x)

    coefficients = []
    for j, xj in enumerate(xs):
        numerator = field.one()
        denominator = field.one()
        for m, xm in enumerate(xs):
            if m == j:
                continue
            numerator = field.multiply(numerator, field.subtract(x, xm))
            denominator = field.multiply(denominator, field.subtract(xj, xm))
        coefficients.append(field.divide(numerator, denominator))

    return coefficients


def lagrange_interpolation(shares: list[Share], x, field: ModularArithmetic):
    """Avalia o polinômio interpolador no ponto x."""
    if not shares:
        raise ValueError("É preciso pelo menos um ponto para interpolar.")
    if any(not isinstance(share, Share) for share in shares):
        raise TypeError("Cada fragmento precisa ser um Share.")
    modulus = shares[0].modulus
    if any(share.modulus != modulus for share in shares):
        raise ValueError("Os fragmentos precisam ter o mesmo módulo.")
    expected_modulus = field.p if isinstance(field, FiniteField) else field.m
    if modulus != expected_modulus:
        raise ValueError("O módulo dos fragmentos difere do módulo do corpo ou anel.")
    coefficients = lagrange_coefficients([share.x for share in shares], x, field)
    result = field.zero()
    for share, coefficient in zip(shares, coefficients):
        result = field.add(result, field.multiply(share.y, coefficient))
    return result


def interpolate_at_zero(shares: list[Share], field: ModularArithmetic):
    """Reconstrói o segredo avaliando o polinômio em x = 0."""
    return lagrange_interpolation(shares, field.zero(), field)


def interpolating_polynomial(points: list[tuple[int, int]],
                             field: ModularArithmetic) -> Polynomial:
    """Expande as bases de Lagrange em um polinômio de grau < len(points).

    Aceita x = 0 para construir candidatos didáticos. Em anéis, exige
    denominadores invertíveis, assim como `lagrange_coefficients`.
    """
    xs = _abscissas([x for x, _ in points], field)
    ys = [field.normalize(y) for _, y in points]
    result = [field.zero()] * len(points)
    for j, (xj, yj) in enumerate(zip(xs, ys)):
        basis = [field.one()]
        denominator = field.one()
        for m, xm in enumerate(xs):
            if m == j:
                continue
            expanded = [field.zero()] * (len(basis) + 1)
            for i, c in enumerate(basis):
                expanded[i] = field.add(expanded[i], field.multiply(c, field.negate(xm)))
                expanded[i + 1] = field.add(expanded[i + 1], c)
            basis = expanded
            denominator = field.multiply(denominator, field.subtract(xj, xm))
        factor = field.divide(yj, denominator)
        for i, c in enumerate(basis):
            result[i] = field.add(result[i], field.multiply(c, factor))
    return Polynomial(result, field)
