"""Distribuição, reconstrução e integração do esquema de Shamir."""
from itertools import combinations
from unittest.mock import Mock

import pytest

from shamir.algebra.finite_field import FiniteField
from shamir.application.participant import Participant
from shamir.serialization.share_text import ShareTextSerializer
from shamir.application.secret_manager import SecretManager
from shamir.cryptography.shamir import ShamirScheme
from shamir.cryptography.share import Share
from shamir.randomness.finite_sampler import FiniteFieldSampler


@pytest.fixture
def scheme():
    field = FiniteField(17)
    return ShamirScheme(field, 3, 5, FiniteFieldSampler(field))


def test_secret_distribution(scheme):
    scheme.sampler = Mock()
    scheme.sampler.sample.side_effect = [5, 2]
    assert scheme.split(8) == [
        Share(1, 15, 17), Share(2, 9, 17), Share(3, 7, 17),
        Share(4, 9, 17), Share(5, 15, 17),
    ]
    assert scheme.sampler.sample.call_count == 2


@pytest.mark.parametrize('secret', [0, 8, 16])
def test_secret_reconstruction(scheme, secret):
    shares = scheme.split(secret)
    for count in range(scheme.threshold, scheme.participants + 1):
        for subset in combinations(shares, count):
            assert scheme.reconstruct(list(reversed(subset))) == secret


def test_insufficient_shares(scheme):
    shares = scheme.split(8)
    for count in range(scheme.threshold):
        with pytest.raises(ValueError, match='pelo menos'):
            scheme.reconstruct(shares[:count])


def test_duplicate_coordinates(scheme):
    shares = scheme.split(8)
    with pytest.raises(ValueError, match='distintas'):
        scheme.reconstruct([shares[0], shares[1], shares[0]])


def test_incompatible_shares(scheme):
    shares = scheme.split(8)
    with pytest.raises(ValueError, match='módulo'):
        scheme.reconstruct([shares[0], shares[1], Share(3, 7, 19)])
    with pytest.raises(TypeError, match='Share'):
        scheme.reconstruct([shares[0], shares[1], None])


@pytest.mark.parametrize('secret', [-1, 17, '8'])
def test_split_validates_secret_before_sampling(scheme, secret):
    scheme.sampler = Mock()
    with pytest.raises((ValueError, TypeError)):
        scheme.split(secret)
    scheme.sampler.sample.assert_not_called()


def test_threshold_one():
    field = FiniteField(17)
    sampler = Mock()
    scheme = ShamirScheme(field, 1, 5, sampler)
    shares = scheme.split(8)
    sampler.sample.assert_not_called()
    for share in shares:
        assert share.y == 8
        assert scheme.reconstruct([share]) == 8
    # Menor corpo suportado e caso em que todos os participantes são necessários.
    for prime, threshold, count in ((2, 1, 1), (5, 4, 4)):
        boundary_field = FiniteField(prime)
        boundary = ShamirScheme(boundary_field, threshold, count, FiniteFieldSampler(boundary_field))
        for secret in range(prime):
            fragments = boundary.split(secret)
            assert len(fragments) == count
            assert boundary.reconstruct(fragments) == secret
            with pytest.raises(ValueError):
                boundary.reconstruct(fragments[:-1])


def test_secret_manager_round_trip(scheme):
    manager = SecretManager(scheme)
    shares = manager.distribute_secret(8)
    participants = [Participant(i) for i in range(1, 6)]
    for participant, share in zip(participants, shares):
        participant.receive_share(ShareTextSerializer.deserialize(ShareTextSerializer.serialize(share)))
    assert manager.recover_secret([participants[i].present_share() for i in (0, 2, 4)]) == 8
    with pytest.raises(ValueError):
        manager.recover_secret([participants[0].present_share()])


def test_split_with_polynomial(scheme):
    scheme.sampler = Mock()
    scheme.sampler.sample.side_effect = [5, 2]
    polynomial, shares = scheme.split_with_polynomial(8)
    assert polynomial.coefficients == [8, 5, 2]
    assert [share.y for share in shares] == [15, 9, 7, 9, 15]
    assert all(polynomial.evaluate(s.x) == s.y for s in shares)