from ..algebra.field import Field
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
    pass


def interpolate_at_zero(shares: list[Share], field: Field):
    """Reconstrói o segredo avaliando o polinômio em x = 0."""
    pass
