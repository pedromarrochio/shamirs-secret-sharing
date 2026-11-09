import secrets

from .sampler import CoefficientSampler
from ..algebra.finite_field import FiniteField


class FiniteFieldSampler(CoefficientSampler):
    """Gera elementos aleatórios de um corpo finito."""

    def __init__(self, field: FiniteField):
        self.field = field

    def sample(self, elements : list[int]):
        """Sorteia um elemento uniforme de Z_p = {0, 1, ..., p - 1}."""
        
        return secrets.randbelow(self.field.p)
