from ..cryptography.shamir import ShamirScheme
from ..cryptography.share import Share


class SecretManager:
    """Gerencia a distribuição e a recuperação de segredos."""

    def __init__(self, scheme: ShamirScheme):
        pass

    def distribute_secret(self, secret) -> list[Share]:
        pass

    def recover_secret(self, shares: list[Share]):
        pass
