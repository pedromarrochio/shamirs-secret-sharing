import pytest

from shamir.application.participant import Participant
from shamir.cryptography.share import Share

"""Testes para fragmentos e participantes."""

def test_share_creation():
    s = Share(x=1, y=15, modulus=17)
    assert (s.x, s.y, s.modulus) == (1, 15, 17)
    assert str(s) == "(1, 15) em Z_17"


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
    assert s.to_text() == "17:4:9"
    assert Share.from_text("17:4:9") == s
    assert Share.from_text("  17:4:9\n") == s   # espaços ao copiar e colar

    for text in ("17:4", "17:4:9:1", "17:a:9", "17:0:9"):
        with pytest.raises(ValueError):
            Share.from_text(text)


def test_participant_lifecycle():
    alice = Participant(1, "Alice")
    assert not alice.has_share
    assert str(alice) == "Alice: sem fragmento"
    with pytest.raises(ValueError):
        alice.present_share()

    s = Share(x=1, y=15, modulus=17)
    alice.receive_share(s)
    assert alice.has_share
    assert alice.present_share() == s
    assert str(alice) == "Alice: (1, 15) em Z_17"

    with pytest.raises(ValueError):
        alice.receive_share(Share(x=1, y=3, modulus=17))


def test_participant_default_name():
    assert Participant(3).name == "Participante 3"