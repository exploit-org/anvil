#!/usr/bin/env python3
import json
import math
import re
from pathlib import Path


BASES = {
    "44": {"k": 4, "l": 4, "eta": 2, "tau": 39, "nu": 3},
    "65": {"k": 6, "l": 5, "eta": 4, "tau": 49, "nu": 6},
    "87": {"k": 8, "l": 7, "eta": 2, "tau": 60, "nu": 7},
}
Q = 8_380_417
RING_DEGREE = 256


def parameter_rows(source: str, level: str):
    block = re.search(
        rf"private static Values forMlDsa{level}\(.*?return switch \(T \* 10 \+ N\) \{{(.*?)default",
        source,
        re.S,
    )
    if block is None:
        raise RuntimeError(f"cannot find ML-DSA-{level} parameter table")
    return re.findall(
        r"case (\d+) -> new Values\((\d+), (\d+), (\d+), nu\)",
        block.group(1),
    )


def distribution(radius: int, dimension: int, nu: int):
    sigma = radius / math.sqrt(dimension + 2)
    return {
        "radius": radius,
        "first_l_sigma": nu * sigma,
        "last_k_sigma": sigma,
        "first_l_alpha": nu * sigma / Q,
        "last_k_alpha": sigma / Q,
        "first_l_support": [-nu * radius, nu * radius],
        "last_k_support": [-radius, radius],
    }


def main() -> None:
    module = Path(__file__).resolve().parents[3]
    source = (module / "src/main/java/org/exploit/mldsa/params/ThresholdMLDSAParameters.java").read_text()
    profiles = []

    for level, base in BASES.items():
        dimension = RING_DEGREE * (base["k"] + base["l"])
        for code, radius, radius_prime, repetitions in parameter_rows(source, level):
            threshold, parties = map(int, code)
            profiles.append({
                "parameter_set": f"ML-DSA-{level}",
                "T": threshold,
                "N": parties,
                "q": Q,
                "ring_degree": RING_DEGREE,
                "module_rows_k": base["k"],
                "module_columns_l": base["l"],
                "dimension": dimension,
                "K": int(repetitions),
                "nu": base["nu"],
                "random_chi_r": distribution(int(radius_prime), dimension, base["nu"]),
                "target_chi_z": distribution(int(radius), dimension, base["nu"]),
                "model_note": "coordinates are correlated uniform-hyperball marginals; an independent Gaussian with these sigmas is only an estimator proxy",
            })

    print(json.dumps(profiles, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
