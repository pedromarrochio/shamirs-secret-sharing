from ..cryptography.share import Share


class ShareTextSerializer:
    """Converte fragmentos para o formato textual 'p:x:y' e vice-versa."""

    @staticmethod
    def serialize(share: Share) -> str:
        if not isinstance(share, Share):
            raise TypeError("O fragmento precisa ser um Share.")
        return f"{share.modulus}:{share.x}:{share.y}"

    @staticmethod
    def deserialize(text: str) -> Share:
        if not isinstance(text, str):
            raise TypeError("O fragmento serializado precisa ser um texto.")
        parts = text.strip().split(":")
        if len(parts) != 3:
            raise ValueError(f"Formato inválido: esperado 'p:x:y', recebido '{text}'.")
        try:
            modulus, x, y = (int(part) for part in parts)
        except ValueError:
            raise ValueError(f"O fragmento '{text}' contém valores que não são inteiros.")
        return Share(x=x, y=y, modulus=modulus)
