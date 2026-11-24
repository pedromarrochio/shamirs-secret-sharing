"""Resultados matemáticos e metodologia dos experimentos executáveis."""

from itertools import product
from unittest.mock import patch

import pytest

from experiments.composite_leakage import candidate_secrets, print_prime_vs_composite
from experiments.missing_inverse import reconstruction_attempt, lagrange_applicable_fraction
from experiments.performance import benchmark
from experiments.ring_comparison import (
    comparison_cases, composite_success_example, division_free_example, tampering_example,
)
from experiments.threshold_analysis import threshold_analysis
from shamir.algebra.integer_mod_ring import IntegerModRing
from shamir.cryptography.analysis import compatible_secret_counts


def test_division_free_identity_for_every_quadratic_over_z12():
    for a, b, c in product(range(12), repeat=3):
        y1, y2, y3 = [(a + b*x + c*x*x) % 12 for x in (1, 2, 3)]
        assert (3*y1 - 3*y2 + y3) % 12 == a
    result = division_free_example()
    assert not result["lagrange"]
    assert result["counts"] == {8: 2}
    assert result["recovered"] == 8


def test_z25_every_trio_recovers_and_every_smaller_subset_preserves_privacy():
    result = composite_success_example()
    assert result["unit_separations"]
    assert len(result["recoveries"]) == 4
    assert all(r["success"] and r["recovered"] == 8 for r in result["recoveries"])
    assert len(result["privacy"]) == 11  # vazio, quatro indivíduos e seis pares
    assert all(result["privacy"].values())


def test_comparison_separates_formula_polynomials_and_secrets():
    rows = {(r["modulus"], tuple(r["xs"])): r for r in comparison_cases()}
    assert not rows[12, (1, 2, 3)]["lagrange"]
    assert rows[12, (1, 2, 3)]["polynomials"] == 2
    assert rows[12, (1, 2, 3)]["secrets"] == [8]
    assert rows[12, (1, 2, 4)]["secrets"] == [0, 4, 8]
    assert rows[15, (1, 2, 3)]["lagrange"]
    assert rows[25, (1, 2, 3)]["secrets"] == [8]


def test_fraction_measures_lagrange_not_all_recovery_methods():
    assert lagrange_applicable_fraction(12, 3) == (0, 165)
    assert lagrange_applicable_fraction(13, 3) == (220, 220)
    assert lagrange_applicable_fraction(25, 3) == (1100, 2024)
    # Mesmo com fração zero em Z_12, estes pontos determinam o segredo.
    assert compatible_secret_counts(12, 3, [(1, 3), (2, 2), (3, 5)]) == {8: 2}


def test_reconstruction_experiment_does_not_accept_too_few_points():
    with pytest.raises(ValueError, match="mais pontos"):
        reconstruction_attempt(IntegerModRing(17), [8, 5, 2], [1, 2])


def test_threshold_analysis_counts_all_subsets_and_equal_candidates():
    rows = threshold_analysis(5, 3, [1, 2, 3, 4], [2, 1, 4])
    assert len(rows) == 16
    for row in rows:
        count = len(row["points"])
        if count < 3:
            assert row["counts"] == {s: 5 ** (2 - count) for s in range(5)}
            assert row["independent"]
        else:
            assert row["counts"] == {2: 1}


def test_threshold_analysis_refuses_invalid_degree_duplicates_and_size():
    for m, k, xs, coefficients in (
        (5, 2, [1, 2], [2, 1, 4]),
        (5, 3, [1, 1], [2, 1, 4]),
        (11, 2, list(range(1, 10)), [2, 1]),
        (25, 3, list(range(1, 9)), [2, 1, 4]),
    ):
        with pytest.raises(ValueError):
            threshold_analysis(m, k, xs, coefficients)


def test_tampering_and_mixing_are_not_detected_by_shamir_alone():
    result = tampering_example()
    assert result["original"] == 8
    assert result["changed"] == 14
    assert result["mixed"] == 15


def test_benchmark_reports_medians_of_distinct_phases():
    timestamps = [0, 3, 5, 10, 11, 15, 20, 22, 30]
    with patch("experiments.performance.perf_counter", side_effect=timestamps):
        result = benchmark(17, 3, 5, repetitions=3)
    assert result["split_seconds"] == 2
    assert result["reconstruction_seconds"] == 4
    assert result["repetitions"] == 3


def test_benchmark_checks_recovery_and_repetitions():
    for invalid in (0, -1, True, 1.5):
        with pytest.raises((TypeError, ValueError)):
            benchmark(17, 3, 5, invalid)
    with patch("experiments.performance.ShamirScheme.reconstruct", return_value=9):
        with pytest.raises(RuntimeError, match="incorreta"):
            benchmark(17, 3, 5, 1)


def test_single_share_formula_matches_independent_polynomial_enumeration():
    for m in (4, 6, 9, 12):
        for x in range(1, m):
            counts = compatible_secret_counts(m, 2, [(x, 1)])
            assert candidate_secrets(m, x, 1, 2) == sorted(counts)


def test_leakage_example_respects_threshold_two_degree_bound():
    output = []
    print_prime_vs_composite(output.append, k=2)
    text = "\n".join(output)
    assert "f(x) = 5 + 7x" in text
    assert "x²" not in text
