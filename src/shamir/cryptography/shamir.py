from ..algebra.field import Field
from ..algebra.finite_field import FiniteField
from ..algebra.polynomial import Polynomial
from .reconstruction import interpolate_at_zero
from .secret_domain import PrimeFieldDomain, SecretDomain
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
        domain: SecretDomain | None = None,
    ):
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
        if domain is None:
            if not isinstance(field, FiniteField):
                raise TypeError("Informe um domínio para corpos diferentes de FiniteField.")
            domain = PrimeFieldDomain(field)
        self.domain = domain
        self.domain.validate_participants(participants)

        self.field = field
        self.threshold = threshold
        self.participants = participants
        self.sampler = sampler

    def validate_secret(self, secret) -> None:
        """Valida o segredo conforme as regras do domínio configurado."""
        self.domain.validate_secret(secret)

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
            self.domain.create_share(x, polynomial.evaluate(x))
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
            self.domain.validate_share(share)
        return interpolate_at_zero(shares, self.field)
