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

    def to_text(self) -> str:
        """Representação em texto para copiar e entregar ao participante: 'p:x:y'."""
        
        return f"{self.modulus}:{self.x}:{self.y}"

    @classmethod
    def from_text(cls, text: str) -> "Share":
        """Reconstrói um fragmento a partir do texto gerado por `to_text`."""
        
        parts = text.strip().split(":")
        if len(parts) != 3:
            raise ValueError(f"Formato inválido: esperado 'p:x:y', recebido '{text}'.")
        try:
            modulus, x, y = (int(part) for part in parts)
        except ValueError:
            raise ValueError(f"O fragmento '{text}' contém valores que não são inteiros.")
        return cls(x=x, y=y, modulus=modulus)