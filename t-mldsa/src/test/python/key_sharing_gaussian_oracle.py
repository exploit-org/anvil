#!/usr/bin/env python3
"""Independent stdlib oracle for the a-posteriori Gaussian weight tables."""

from decimal import Decimal, ROUND_FLOOR, getcontext, localcontext
from pathlib import Path
import re


getcontext().prec = 100
SCALE = 1 << 384
SOURCE = (
    Path(__file__).resolve().parents[3]
    / "src/main/java/org/exploit/mldsa/rss/ConditionedGaussianSampler.java"
)


def parse_profiles():
    source = SOURCE.read_text(encoding="ascii")
    pattern = re.compile(
        r"ETA_(?P<eta>[24])\s*=\s*new Profile\((?P<bound>\d+),\s*weights\((?P<body>.*?)\)\);",
        re.DOTALL,
    )
    profiles = {}
    for match in pattern.finditer(source):
        eta = int(match.group("eta"))
        bound = int(match.group("bound"))
        weights = [int(value, 16) for value in re.findall(r'"([0-9a-f]+)"', match.group("body"))]
        profiles[eta] = (bound, weights)
    if set(profiles) != {2, 4}:
        raise AssertionError("failed to parse both Gaussian profiles")
    return profiles


def verify_profile(eta, bound, weights):
    if len(weights) != bound + 1:
        raise AssertionError(f"eta={eta}: wrong table length")

    variance = Decimal(eta * (eta + 1)) / Decimal(3)
    expected = []
    for precision in (220, 320):
        with localcontext() as context:
            context.prec = precision
            local_variance = Decimal(eta * (eta + 1)) / Decimal(3)
            expected.append([
                int(
                    (Decimal(SCALE) * (-(Decimal(x * x) / (2 * local_variance))).exp()).to_integral_value(
                        rounding=ROUND_FLOOR
                    )
                )
                for x in range(bound + 1)
            ])
    if expected[0] != expected[1]:
        raise AssertionError(f"eta={eta}: generated table is not precision-stable")
    if weights != expected[1]:
        raise AssertionError(f"eta={eta}: table differs from floor(2^384 exp(-x^2/(2 variance)))")

    total = weights[0] + 2 * sum(weights[1:])
    if 8 * weights[0] <= total:
        raise AssertionError(f"eta={eta}: zero mass is not greater than 1/8")

    distribution = {x: weights[abs(x)] for x in range(-bound, bound + 1)}
    convolution = {0: 1}
    minimum_acceptance = Decimal(1)
    minimum_case = None
    for share_count in range(1, 21):
        next_convolution = {}
        for current_sum, current_mass in convolution.items():
            for value, value_mass in distribution.items():
                target = current_sum + value
                next_convolution[target] = next_convolution.get(target, 0) + current_mass * value_mass
        convolution = next_convolution

        if share_count < 2:
            continue
        denominator = weights[0] * total ** (share_count - 1)
        for target in range(-eta, eta + 1):
            acceptance = Decimal(convolution[target]) / Decimal(denominator)
            if acceptance < minimum_acceptance:
                minimum_acceptance = acceptance
                minimum_case = (share_count, target)

    if minimum_acceptance <= Decimal(1) / Decimal(5):
        raise AssertionError(f"eta={eta}: rejection acceptance is not above 1/5")

    exponent = Decimal(1) / (2 * variance)
    first_omitted = bound + 1
    tail_ratio = (-(exponent * Decimal(2 * first_omitted + 1))).exp()
    tail_bound = 2 * (-(exponent * Decimal(first_omitted * first_omitted))).exp() / (1 - tail_ratio)
    quantization_bound = Decimal(2 * bound + 1) / Decimal(SCALE)
    scalar_distance_bound = tail_bound + quantization_bound
    conditioned_distance_bound = scalar_distance_bound * Decimal(20 * 82)
    if conditioned_distance_bound >= Decimal(2) ** Decimal(-300):
        raise AssertionError(f"eta={eta}: conditioned distance bound exceeds 2^-300")

    print(
        f"eta={eta} bound={bound} min_acceptance={minimum_acceptance:.8f} "
        f"case={minimum_case} conditioned_distance_bound={conditioned_distance_bound:.3E}"
    )


def main():
    for eta, (bound, weights) in sorted(parse_profiles().items()):
        verify_profile(eta, bound, weights)


if __name__ == "__main__":
    main()
