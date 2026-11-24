from ..algebra.finite_field import FiniteField
from ..algebra.polynomial import Polynomial
from .reconstruction import interpolate_at_zero
from ..randomness.sampler import CoefficientSampler
from .share import Share


class ShamirScheme:
    """Esquema de Shamir em Z_p; anéis compostos são estudados nos experimentos."""

    def __init__(
        self,
        field: FiniteField,
        threshold: int,
        participants: int,
        sampler: CoefficientSampler,
    ):
        if not isinstance(field, FiniteField):
            raise TypeError("O esquema padrão exige um FiniteField (Z_p com p primo).")
        if any(not isinstance(value, int) or isinstance(value, bool)
               for value in (threshold, participants)):
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
        """Admite apenas segredos inteiros no intervalo canônico do corpo."""
        if not isinstance(secret, int) or isinstance(secret, bool):
            raise TypeError("O segredo precisa ser um inteiro.")
        if not 0 <= secret < self.field.p:
            raise ValueError(
                f"O segredo precisa estar entre 0 e {self.field.p - 1} "
                f"(recebido {secret})."
            )

    def split(self, secret) -> list[Share]:
        """Gera n pontos não nulos de um polinômio com termo constante secreto."""
        _, shares = self.split_with_polynomial(secret)
        return shares

    def split_with_polynomial(self, secret) -> tuple[Polynomial, list[Share]]:
        """Como `split`, mas devolve também o polinômio sorteado.

        Útil para fins didáticos: numa distribuição real, o distribuidor
        descarta o polinômio depois de entregar os fragmentos.
        """
        self.validate_secret(secret)
        polynomial = Polynomial.random(
            self.field, self.sampler, self.threshold - 1, secret
        )
        shares = [
            Share(x, polynomial.evaluate(x), self.field.p)
            for x in range(1, self.participants + 1)
        ]
        return polynomial, shares

    def reconstruct(self, shares: list[Share]):
        """Reconstrói o segredo com pelo menos k fragmentos distintos."""
        if len(shares) < self.threshold:
            raise ValueError(
                f"São necessários pelo menos {self.threshold} fragmentos "
                f"(recebidos {len(shares)})."
            )
        for share in shares:
            if not isinstance(share, Share):
                raise TypeError("Cada fragmento precisa ser um Share.")
            if share.modulus != self.field.p:
                raise ValueError("O módulo do fragmento difere do módulo do esquema.")
        return interpolate_at_zero(shares, self.field)
