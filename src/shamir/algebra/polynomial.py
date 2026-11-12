from .polynomial_arithmetic import PolynomialArithmetic
from ..randomness.sampler import CoefficientSampler

class Polynomial:
    """Polinômio com coeficientes pertencentes a um corpo.
    
    Os coeficientes são guardados do termo de menor grau para o de maior:
    [a0, a1, ..., an] representa a0 + a1*x + ... + an*x^n.
    """

    def __init__(self, coefficients: list, field: PolynomialArithmetic):
        if len(coefficients) == 0:
            raise ValueError("Um polinômio precisa de pelo menos um coeficiente.")

        self.field = field
        self.coefficients = [field.normalize(c) for c in coefficients]

    @classmethod
    def random(cls, field: PolynomialArithmetic, sampler: CoefficientSampler,
               degree: int, constant_term):
        """Cria um polinômio de grau `degree` com termo constante fixo
        e os demais coeficientes sorteados pelo `sampler`."""

        if degree < 0:
            raise ValueError("O grau precisa ser não negativo.")

        coefficients = [constant_term]
        coefficients += [sampler.sample() for _ in range(degree)]
        return cls(coefficients, field)

    @property
    def degree(self) -> int:
        """Maior i com coeficiente a_i não nulo (-1 para o polinômio nulo)."""

        for i in range(len(self.coefficients) - 1, -1, -1):
            if self.coefficients[i] != self.field.zero():
                return i
        return -1

    def evaluate(self, x):
        """Calcula f(x) no corpo pelo método de Horner."""
        x = self.field.normalize(x)
        result = self.field.zero()

        for c in reversed(self.coefficients):
            result = self.field.add(self.field.multiply(result, x), c)

        return result