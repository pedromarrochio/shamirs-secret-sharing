from dataclasses import dataclass
from ..cryptography.share import Share


@dataclass
class Participant:
    """Representa um participante que possui um compartilhamento."""

    participant_id: int
    share: Share
