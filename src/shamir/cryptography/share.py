from dataclasses import dataclass


@dataclass(frozen=True)
class Share:
    """Compartilhamento individual de um segredo: o ponto (x, y) de Z_p x Z_p.."""

    x: int
    y: int
    modulus: int

    def __post_init__(self):
        if not 0 < self.x < self.modulus:
            raise ValueError(
                f"A abscissa precisa estar entre 1 e {self.modulus - 1} "
                f"(recebido x = {self.x}); x = 0 guardaria o próprio segredo."
            )
        if not 0 <= self.y < self.modulus:
            raise ValueError(
                f"O valor precisa estar entre 0 e {self.modulus - 1} "
                f"(recebido y = {self.y})."
            )
