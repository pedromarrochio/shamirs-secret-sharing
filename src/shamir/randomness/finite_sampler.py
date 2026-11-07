from .sampler import CoefficientSampler
from ..algebra.finite_field import FiniteField
import random


class FiniteFieldSampler(CoefficientSampler):
    """Gera elementos aleatórios de um corpo finito."""

    def __init__(self, field: FiniteField):
        self.field = field

    def sample(self, elements : list[int]):
        return random.choice(elements)
