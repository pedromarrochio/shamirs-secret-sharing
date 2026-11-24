from dataclasses import dataclass


@dataclass(frozen=True)
class Share:
    """Fragmento modular (x, y); a primalidade é validada pelo esquema padrão."""

    x: int
    y: int
    modulus: int

    def __str__(self) -> str:
        return f"({self.x}, {self.y}) em Z_{self.modulus}"

    def __post_init__(self):
        if any(not isinstance(value, int) or isinstance(value, bool)
               for value in (self.x, self.y, self.modulus)):
            raise TypeError("As coordenadas e o módulo precisam ser inteiros.")
        if self.modulus < 2:
            raise ValueError("O módulo precisa ser pelo menos 2.")
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
