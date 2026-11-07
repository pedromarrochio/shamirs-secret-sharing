from .finite_field import FiniteField
from ..randomness.finite_sampler import FiniteFieldSampler

class Polynomial:
    """Polinômio com coeficientes pertencentes a um corpo."""

    def __init__(self, field: FiniteField, sampler : FiniteFieldSampler, degree: int):

        self.field = field
        self.degree = degree
        self.coeficients = [sampler.sample(field.elements) for i in range(degree)]

    def evaluate(self, x):
        value = int()

        for i in range(self.degree):
            self.field.add(self.field.multiply(x ** i, self.coeficients[i]))
            
        return self.field.normalize(value)

