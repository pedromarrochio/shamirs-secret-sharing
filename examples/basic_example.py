"""Exemplo básico de utilização do esquema de Shamir."""

from shamir.algebra.finite_field import FiniteField
from shamir.cryptography.reconstruction import lagrange_coefficients
from shamir.cryptography.shamir import ShamirScheme
from shamir.randomness.finite_sampler import FiniteFieldSampler


def main():
    field = FiniteField(17)
    secret = 8
    scheme = ShamirScheme(field, threshold=3, participants=5,
                          sampler=FiniteFieldSampler(field))

    print("Esquema de Shamir: 3 de 5 participantes, em Z_17")
    print(f"Segredo de demonstração: {secret}")
    shares = scheme.split(secret)
    print("\nFragmentos gerados (mudam a cada execução):")
    for share in shares:
        print(f"  {share}")

    selected = [shares[0], shares[1], shares[3]]
    coefficients = lagrange_coefficients([s.x for s in selected], 0, field)
    print("\nInterpolação em x = 0 com os fragmentos 1, 2 e 4:")
    print(f"  Coeficientes de Lagrange: {coefficients}")
    expression = " + ".join(
        f"{share.y} * {coefficient}"
        for share, coefficient in zip(selected, coefficients)
    )
    recovered = scheme.reconstruct(selected)
    print(f"  f(0) = ({expression}) mod {field.p} = {recovered}")
    if recovered != secret:
        raise RuntimeError("O segredo recuperado difere do original.")

    print("\nTentativa com apenas dois fragmentos:")
    try:
        scheme.reconstruct(selected[:2])
    except ValueError as error:
        print(f"  Recusada: {error}")
    else:
        raise RuntimeError("A reconstrução deveria exigir três fragmentos.")
    print("A recusa aplica o limiar da API; não é, sozinha, uma demonstração de sigilo.")
    print("Veja o exemplo guiado e experiments.threshold_analysis para a análise dos candidatos e distribuições.")


if __name__ == "__main__":
    main()
