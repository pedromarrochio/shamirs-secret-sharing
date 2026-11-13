import secrets
from .field import Field


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Algoritmo de Euclides estendido.

    Devolve (d, u, v) com d = mdc(a, b) e a*u + b*v = d (identidade de Bézout).
    """
    old_r, r = a, b
    old_u, u = 1, 0
    old_v, v = 0, 1

    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_u, u = u, old_u - q * u
        old_v, v = v, old_v - q * v

    if old_r < 0:
        return -old_r, -old_u, -old_v
    return old_r, old_u, old_v

_SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_prime(n: int) -> bool:
    """Teste de primalidade de Miller-Rabin.

    Determinístico para n < 3,3 * 10^24; acima disso, probabilístico
    (com chance de erro desprezível).
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("O número precisa ser um inteiro.")
    if n < 2:
        return False
    for q in _SMALL_PRIMES:
        if n % q == 0:
            return n == q

    # escreve n - 1 = 2^s * d com d ímpar
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1

    bases = list(_SMALL_PRIMES)
    if n >= 3_317_044_064_679_887_385_961_981:
        bases += [secrets.randbelow(n - 3) + 2 for _ in range(20)]

    for a in bases:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False   # a é testemunha de que n é composto
    return True


class FiniteField(Field):
    """Corpo finito de ordem prima p."""

    def __init__(self, p: int):
        if not isinstance(p, int) or isinstance(p, bool):
            raise TypeError("A ordem do corpo precisa ser um inteiro.")
        if not is_prime(p):
            raise ValueError(f"{p} não é primo: Z_{p} não é um corpo.")
        self.p = p
        
    def normalize(self, value):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("Os elementos do corpo precisam ser inteiros.")
        return(value % self.p)

    def add(self, a, b):
        return(self.normalize(self.normalize(a) + self.normalize(b)))
    
    def negate(self, a):
        return self.normalize(-self.normalize(a))

    def subtract(self, a, b):
        return self.add(a, self.negate(b))

    def multiply(self, a, b):
        return(self.normalize(self.normalize(a) * self.normalize(b)))

    def inverse(self, value):
        a = self.normalize(value)
        if a == 0:
            raise ZeroDivisionError("0 não tem inverso multiplicativo.")

        d, u, _ = extended_gcd(a, self.p)
        if d != 1:
            raise ValueError(
                f"{a} não tem inverso módulo {self.p}: mdc({a}, {self.p}) = {d}."
            )
        return self.normalize(u)
    
    def divide(self, a, b):
        return self.multiply(a, self.inverse(b))

    def zero(self):
        return(self.normalize(0))

    def one(self):
        return(self.normalize(1))
