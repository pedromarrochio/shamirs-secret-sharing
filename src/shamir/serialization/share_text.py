from ..cryptography.share import Share


class ShareTextSerializer:
    """Converte fragmentos para o formato textual 'p:x:y' e vice-versa."""

    @staticmethod
    def serialize(share: Share) -> str:
        return f"{share.modulus}:{share.x}:{share.y}"

    @staticmethod
    def deserialize(text: str) -> Share:
        parts = text.strip().split(":")
        if len(parts) != 3:
            raise ValueError(f"Formato inválido: esperado 'p:x:y', recebido '{text}'.")
        try:
            modulus, x, y = (int(part) for part in parts)
        except ValueError:
            raise ValueError(f"O fragmento '{text}' contém valores que não são inteiros.")
        return Share(x=x, y=y, modulus=modulus)
