from .field import Field


class FiniteField(Field):
    """Corpo finito de ordem prima p."""

    def __init__(self, p: int):
        self.p = p
        self.elements : list[int] = list(range(p))

    def normalize(self, value):
        return(value % self.p)

    def add(self, a, b):
        return(self.normalize(a + b))

    def multiply(self, a, b):
        return(self.normalize(a * b))
    
    def zero(self):
        return(self.normalize(0))

    def one(self):
        return(self.normalize(1))
