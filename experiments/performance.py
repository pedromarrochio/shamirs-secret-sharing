"""Medições locais de distribuição e reconstrução no corpo primo."""

from statistics import median
from time import perf_counter

from shamir.algebra.finite_field import FiniteField
from shamir.cryptography.shamir import ShamirScheme
from shamir.randomness.finite_sampler import FiniteFieldSampler


def benchmark(p: int, k: int, n: int, repetitions: int = 15) -> dict:
    """Mede medianas; construção do corpo e teste de primalidade ficam fora.

    A distribuição inclui sorteio criptográfico. A reconstrução usa exatamente
    k fragmentos. Cada resultado é conferido antes de registrar a medição.
    """
    if not isinstance(repetitions, int) or isinstance(repetitions, bool):
        raise TypeError("O número de repetições precisa ser inteiro.")
    if repetitions < 1:
        raise ValueError("É preciso pelo menos uma repetição.")
    field = FiniteField(p)
    scheme = ShamirScheme(field, k, n, FiniteFieldSampler(field))
    split_times, reconstruction_times = [], []
    secret = min(8, p - 1)
    for _ in range(repetitions):
        start = perf_counter()
        shares = scheme.split(secret)
        after_split = perf_counter()
        recovered = scheme.reconstruct(shares[:k])
        after_reconstruction = perf_counter()
        if recovered != secret:
            raise RuntimeError("A medição encontrou uma reconstrução incorreta.")
        split_times.append(after_split - start)
        reconstruction_times.append(after_reconstruction - after_split)
    return {"p": p, "k": k, "n": n, "repetitions": repetitions,
            "split_seconds": median(split_times),
            "reconstruction_seconds": median(reconstruction_times)}


def main(out=print):
    out("=== Desempenho: medianas de 15 execuções, tempos em microssegundos ===")
    out(f"{'bits de p':>9} {'k':>3} {'n':>3} {'distribuição':>14} {'recuperação':>14}")
    for p, k, n in ((257, 3, 5), (65537, 3, 5), (65537, 5, 10), (2**61 - 1, 5, 10)):
        row = benchmark(p, k, n)
        out(f"{p.bit_length():>9} {k:>3} {n:>3} "
            f"{row['split_seconds'] * 1e6:>14.2f} "
            f"{row['reconstruction_seconds'] * 1e6:>14.2f}")
    out("Construção do corpo excluída; sorteio incluído; recuperação com exatamente k fragmentos.")
    out("Horner custa O(nk) operações; Lagrange direto, O(k²), além do custo dos inversos.")
    out("Tempos variam com máquina e carga; não medem sigilo nem justificam usar anéis inseguros.")


if __name__ == "__main__":
    main()
