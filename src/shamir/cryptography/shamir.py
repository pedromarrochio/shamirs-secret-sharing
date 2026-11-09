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
        if not isinstance(threshold, int) or not isinstance(participants, int):
            raise TypeError("O limiar k e o número de participantes n precisam ser inteiros.")
        if threshold < 1:
            raise ValueError(f"O limiar k precisa ser pelo menos 1 (recebido k = {threshold}).")
        if threshold > participants:
            raise ValueError(
                f"O limiar não pode passar do número de participantes "
                f"(k = {threshold} > n = {participants})."
            )
        if participants >= field.p:
            raise ValueError(
                f"São necessários n pontos distintos e não nulos em Z_{field.p}, "
                f"então n precisa ser menor que p (recebido n = {participants})."
            )

        self.field = field
        self.threshold = threshold
        self.participants = participants
        self.sampler = sampler

    def validate_secret(self, secret) -> None:
        """Verifica se o segredo é um elemento de Z_p, isto é, 0 <= s < p."""
        if not isinstance(secret, int):
            raise TypeError("O segredo precisa ser um inteiro.")
        if not 0 <= secret < self.field.p:
            raise ValueError(
                f"O segredo precisa estar entre 0 e {self.field.p - 1} "
                f"(recebido {secret})."
            )

    def split(self, secret) -> list[Share]:
        pass

    def reconstruct(self, shares: list[Share]):
        pass
