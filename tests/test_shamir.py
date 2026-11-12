"""Distribuição, reconstrução e integração do esquema de Shamir."""
from itertools import combinations
from unittest.mock import Mock

import pytest

from shamir.algebra.finite_field import FiniteField
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


def test_secret_manager_round_trip(scheme):
    manager = SecretManager(scheme)
    assert manager.recover_secret(manager.distribute_secret(8)[:3]) == 8
