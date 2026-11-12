from abc import ABC, abstractmethod


class CoefficientSampler(ABC):
    """Interface para geração de coeficientes aleatórios."""

    @abstractmethod
    def sample(self):
        pass
