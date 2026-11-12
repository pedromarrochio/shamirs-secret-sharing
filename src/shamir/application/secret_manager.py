from ..cryptography.shamir import ShamirScheme
from ..cryptography.share import Share


class SecretManager:
    """Gerencia a distribuição e a recuperação de segredos."""

    def __init__(self, scheme: ShamirScheme):
        self.scheme = scheme

    def distribute_secret(self, secret) -> list[Share]:
        """Gera os fragmentos do segredo usando o esquema configurado."""
        return self.scheme.split(secret)

    def recover_secret(self, shares: list[Share]):
        """Recupera o segredo a partir dos fragmentos apresentados."""
        return self.scheme.reconstruct(shares)
