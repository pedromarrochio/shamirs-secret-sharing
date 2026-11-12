from ..algebra.field import Field
from ..algebra.finite_field import FiniteField
from .share import Share


def lagrange_coefficients(x_values: list, x, field: Field) -> list:
    """Calcula os coeficientes de Lagrange L_j(x) no corpo.

    Para abscissas distintas x_1, ..., x_k, devolve [L_1(x), ..., L_k(x)], com

        L_j(x) = prod_{m != j} (x - x_m) / (x_j - x_m).

    Com x = 0, são os coeficientes usados para reconstruir o segredo.
    """
    xs = [field.normalize(xi) for xi in x_values]
    x = field.normalize(x)

    if len(xs) == 0:
        raise ValueError("É preciso pelo menos um ponto para interpolar.")
    if len(set(xs)) != len(xs):
        raise ValueError(
            "As abscissas precisam ser distintas no corpo "
            "(senão algum denominador x_j - x_m é zero)."
        )

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

def lagrange_interpolation(shares: list[Share], x, field: Field):
    """Avalia o polinômio interpolador no ponto x."""
    if not shares:
        raise ValueError("É preciso pelo menos um ponto para interpolar.")
    if any(not isinstance(share, Share) for share in shares):
        raise TypeError("Cada fragmento precisa ser um Share.")
    modulus = shares[0].modulus
    if any(share.modulus != modulus for share in shares):
        raise ValueError("Os fragmentos precisam ter o mesmo módulo.")
    if isinstance(field, FiniteField) and modulus != field.p:
        raise ValueError("O módulo dos fragmentos difere do módulo do corpo.")
    coefficients = lagrange_coefficients([share.x for share in shares], x, field)
    result = field.zero()
    for share, coefficient in zip(shares, coefficients):
        result = field.add(result, field.multiply(share.y, coefficient))
    return result


def interpolate_at_zero(shares: list[Share], field: Field):
    """Reconstrói o segredo avaliando o polinômio em x = 0."""
    return lagrange_interpolation(shares, field.zero(), field)
