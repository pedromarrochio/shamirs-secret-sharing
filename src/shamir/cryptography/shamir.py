from ..algebra.field import Field
from ..randomness.sampler import CoefficientSampler
from .share import Share


class ShamirScheme:
    """Implementação do esquema de compartilhamento secreto de Shamir."""

    def __init__(
        self,
        field: Field,
        threshold: int,
        participants: int,
        sampler: CoefficientSampler,
    ):
        pass

    def split(self, secret) -> list[Share]:
        pass

    def reconstruct(self, shares: list[Share]):
        pass
