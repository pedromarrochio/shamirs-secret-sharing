import pytest

from shamir.application.participant import Participant
from shamir.cryptography.share import Share
from shamir.serialization.share_text import ShareTextSerializer

"""Testes para fragmentos e participantes."""

def test_share_creation():
    s = Share(x=1, y=15, modulus=17)
    assert (s.x, s.y, s.modulus) == (1, 15, 17)
    assert str(s) == "(1, 15) em Z_17"
    for x, y, modulus in ((1.5, 2, 17), (1, 2.5, 17), (1, 2, 17.0), (True, 2, 17)):
        with pytest.raises(TypeError):
            Share(x, y, modulus)


@pytest.mark.parametrize("x, y", [(0, 5), (17, 5), (-1, 5), (1, 17), (1, -1)])
def test_invalid_share(x, y):
    with pytest.raises(ValueError):
        Share(x=x, y=y, modulus=17)


def test_share_is_immutable():
    s = Share(x=1, y=15, modulus=17)
    with pytest.raises(AttributeError):
        s.y = 12


def test_share_text_round_trip():
    s = Share(x=4, y=9, modulus=17)
    assert ShareTextSerializer.serialize(s) == "17:4:9"
    assert ShareTextSerializer.deserialize("17:4:9") == s
    assert ShareTextSerializer.deserialize("  17:4:9\n") == s   # espaços ao copiar e colar

    for invalid in (None, 17, b"17:4:9"):
        with pytest.raises(TypeError):
            ShareTextSerializer.deserialize(invalid)
    with pytest.raises(TypeError):
        ShareTextSerializer.serialize(None)
    for text in ("", "17:4", "17:4:9:1", "17:a:9", "17:0:9", "17:4:17", "1:1:0"):
        with pytest.raises(ValueError):
            ShareTextSerializer.deserialize(text)


def test_participant_lifecycle():
    alice = Participant(1, "Alice")
    with pytest.raises(TypeError):
        alice.receive_share(None)
    assert not alice.has_share
    assert str(alice) == "Alice: sem fragmento"
    with pytest.raises(ValueError):
        alice.present_share()

    s = Share(x=1, y=15, modulus=17)
    alice.receive_share(s)
    assert alice.has_share
    assert alice.present_share() == s
    assert str(alice) == "Alice: (1, 15) em Z_17"
    assert alice.present_share() is s  # apresentar não consome o fragmento

    with pytest.raises(ValueError):
        alice.receive_share(Share(x=1, y=3, modulus=17))


def test_participant_default_name():
    assert Participant(3).name == "Participante 3"
    fragment = Share(1, 8, 17)
    participant = Participant(1, share=fragment)
    assert participant.has_share
    assert participant.present_share() is fragment
    with pytest.raises(TypeError):
        Participant(1, share="17:1:8")