"""Exemplo de recuperação distribuída de um segredo."""

from shamir.algebra.finite_field import FiniteField
from shamir.application.participant import Participant
from shamir.application.secret_manager import SecretManager
from shamir.cryptography.shamir import ShamirScheme
from shamir.randomness.finite_sampler import FiniteFieldSampler
from shamir.serialization.share_text import ShareTextSerializer


def main():
    field = FiniteField(257)
    scheme = ShamirScheme(field, threshold=3, participants=5,
                          sampler=FiniteFieldSampler(field))
    manager = SecretManager(scheme)
    secret = 123
    participants = [
        Participant(index, name)
        for index, name in enumerate(("Alice", "Bruno", "Carla", "Diego", "Eva"), start=1)
    ]

    print("Distribuição simulada: cada participante recebe um fragmento em texto.")
    print(f"Segredo de demonstração: {secret}; limiar: 3 de 5, em Z_257.")
    for participant, share in zip(participants, manager.distribute_secret(secret)):
        text = ShareTextSerializer.serialize(share)
        participant.receive_share(ShareTextSerializer.deserialize(text))
        print(f"  {participant.name} recebeu {text}")

    available = [participants[0], participants[2], participants[4]]
    print("\nAlice, Carla e Eva apresentam seus fragmentos; Bruno e Diego estão ausentes.")
    presented = []
    for participant in available:
        text = ShareTextSerializer.serialize(participant.present_share())
        presented.append(ShareTextSerializer.deserialize(text))
        print(f"  {participant.name} apresentou {text}")

    recovered = manager.recover_secret(presented)
    print(f"Segredo recuperado: {recovered}")
    if recovered != secret:
        raise RuntimeError("O segredo recuperado difere do original.")

    print("\nTentativa de apresentar duas vezes o fragmento de Alice:")
    try:
        manager.recover_secret([presented[0], presented[0], presented[1]])
    except ValueError as error:
        print(f"  Recusada: {error}")
    else:
        raise RuntimeError("Fragmentos duplicados deveriam ser recusados.")


if __name__ == "__main__":
    main()
