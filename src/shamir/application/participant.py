from dataclasses import dataclass
from typing import Optional
from ..cryptography.share import Share


@dataclass
class Participant:
    """Representa um participante que possui um compartilhamento."""

    participant_id: int
    name: str = ""
    share: Optional[Share] = None

    def __post_init__(self):
        if self.share is not None and not isinstance(self.share, Share):
            raise TypeError("O fragmento precisa ser um Share.")
        if not self.name:
            self.name = f"Participante {self.participant_id}"

    @property
    def has_share(self) -> bool:
        return self.share is not None

    def receive_share(self, share: Share) -> None:
        """Guarda o fragmento entregue pelo distribuidor (só pode receber um)."""
        
        if not isinstance(share, Share):
            raise TypeError("O fragmento precisa ser um Share.")
        if self.has_share:
            raise ValueError(f"{self.name} já possui um fragmento.")
        self.share = share

    def present_share(self) -> Share:
        """Entrega o fragmento para a reconstrução."""
        
        if not self.has_share:
            raise ValueError(f"{self.name} ainda não recebeu um fragmento.")
        return self.share

    def __str__(self) -> str:
        status = str(self.share) if self.has_share else "sem fragmento"
        return f"{self.name}: {status}"
