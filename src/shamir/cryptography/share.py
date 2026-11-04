from dataclasses import dataclass


@dataclass(frozen=True)
class Share:
    """Compartilhamento individual de um segredo."""

    x: int
    y: int
