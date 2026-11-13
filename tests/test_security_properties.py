"""Testes e experimentos relacionados às propriedades de segurança."""

from collections import Counter
from itertools import combinations, product
from unittest.mock import Mock

import pytest

from shamir.algebra.finite_field import FiniteField
from shamir.cryptography.shamir import ShamirScheme
from shamir.randomness.finite_sampler import FiniteFieldSampler


def test_reconstruction_threshold():
    field = FiniteField(17)
    scheme = ShamirScheme(field, 3, 5, FiniteFieldSampler(field))
    shares = scheme.split(8)
    for count in range(scheme.participants + 1):
        for subset in combinations(shares, count):
            if count < scheme.threshold:
                with pytest.raises(ValueError, match="pelo menos"):
                    scheme.reconstruct(list(subset))
            else:
                assert scheme.reconstruct(list(subset)) == 8


def test_secret_independence():
    # Enumera todos os sorteios em Z_5: com menos de k fragmentos,
    # a distribuição observada é exatamente a mesma para qualquer segredo.
    field = FiniteField(5)
    sampler = Mock()
    scheme = ShamirScheme(field, 3, 4, sampler)
    for count in (1, 2):
        for indices in combinations(range(scheme.participants), count):
            distributions = []
            for secret in range(field.p):
                observations = Counter()
                for coefficients in product(range(field.p), repeat=2):
                    sampler.sample.side_effect = coefficients
                    shares = scheme.split(secret)
                    observations[tuple(shares[i].y for i in indices)] += 1
                distributions.append(observations)
            assert all(distribution == distributions[0] for distribution in distributions)
            assert len(distributions[0]) == field.p ** count
