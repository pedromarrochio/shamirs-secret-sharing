from .finite_field import extended_gcd


class NonInvertibleElementError(ValueError):
    """Erro lançado quando um elemento não tem inverso em Z_m."""

    def __init__(self, element: int, modulus: int, gcd: int):
        self.element = element
        self.modulus = modulus
        self.gcd = gcd
        super().__init__(
            f"{element} não tem inverso em Z_{modulus}: "
            f"mdc({element}, {modulus}) = {gcd} ≠ 1."
        )


class IntegerModRing:
    """Anel Z_m dos inteiros módulo m, com m qualquer (primo ou composto).

    Oferece os mesmos métodos que um Field para poder ser usado nos
    experimentos, mas NÃO é um corpo quando m é composto: alguns elementos
    não nulos não têm inverso.
    """

    def __init__(self, m: int):
        if not isinstance(m, int) or m < 2:
            raise ValueError("O módulo precisa ser um inteiro maior ou igual a 2.")
        self.m = m

    def normalize(self, value):
        return value % self.m

    def add(self, a, b):
        return self.normalize(a + b)

    def negate(self, a):
        return self.normalize(-a)

    def subtract(self, a, b):
        return self.add(a, self.negate(b))

    def multiply(self, a, b):
        return self.normalize(a * b)

    def is_unit(self, value) -> bool:
        """Diz se o elemento é invertível, isto é, se mdc(value, m) = 1."""
        
        d, _, _ = extended_gcd(self.normalize(value), self.m)
        return d == 1

    def inverse(self, value):
        a = self.normalize(value)
        d, u, _ = extended_gcd(a, self.m)
        if d != 1:
            raise NonInvertibleElementError(a, self.m, d)
        return self.normalize(u)

    def divide(self, a, b):
        return self.multiply(a, self.inverse(b))

    def zero(self):
        return 0

    def one(self):
        return self.normalize(1)