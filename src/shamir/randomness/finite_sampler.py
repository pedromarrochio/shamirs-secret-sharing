from .sampler import CoefficientSampler
from ..algebra.finite_field import FiniteField


class FiniteFieldSampler(CoefficientSampler):
    """Gera elementos aleatórios de um corpo finito."""

    def __init__(self, field: FiniteField):
        pass

    def sample(self):
        pass
