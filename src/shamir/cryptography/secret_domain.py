from typing import Protocol

from ..algebra.finite_field import FiniteField
from .share import Share


class SecretDomain(Protocol):
    """Regras de admissão de segredos e participantes de um esquema."""

    def validate_secret(self, secret) -> None: ...

    def validate_participants(self, participants: int) -> None: ...

    def create_share(self, x, y) -> Share: ...

    def validate_share(self, share: Share) -> None: ...


class PrimeFieldDomain:
    """Regras para segredos inteiros e coordenadas não nulas em Z_p."""

    def __init__(self, field: FiniteField):
        self.field = field

    def create_share(self, x, y) -> Share:
        return Share(x=x, y=y, modulus=self.field.p)

    def validate_share(self, share: Share) -> None:
        if not isinstance(share, Share):
            raise TypeError("Cada fragmento precisa ser um Share.")
        if share.modulus != self.field.p:
            raise ValueError("O módulo do fragmento difere do módulo do esquema.")
        if not isinstance(share.x, int) or not isinstance(share.y, int):
            raise TypeError("As coordenadas do fragmento precisam ser inteiras.")

    def validate_secret(self, secret) -> None:
        if not isinstance(secret, int):
            raise TypeError("O segredo precisa ser um inteiro.")
        if not 0 <= secret < self.field.p:
            raise ValueError(
                f"O segredo precisa estar entre 0 e {self.field.p - 1} "
                f"(recebido {secret})."
            )

    def validate_participants(self, participants: int) -> None:
        if participants >= self.field.p:
            raise ValueError(
                f"São necessários n pontos distintos e não nulos em Z_{self.field.p}, "
                f"então n precisa ser menor que p (recebido n = {participants})."
            )
