#!/usr/bin/env python3
import hashlib
import struct

import mpmath as mp


DIM = 2
L = 1
N = 256
R_PRIME = mp.mpf(1000)
NU = 3
NONCE = 7
OUTPUTS = 16


def uniform_open(bits: int) -> mp.mpf:
    return (mp.mpf(bits >> 12) + mp.mpf("0.5")) * mp.power(2, -52)


def main() -> None:
    mp.mp.dps = 100
    total = DIM * N
    seed = b"H" + bytes(64) + struct.pack("<H", NONCE)
    raw = hashlib.shake_256(seed).digest((total + 1) * 8)
    samples = []

    for offset in range(0, total, 2):
        u1_bits = int.from_bytes(raw[offset * 8:(offset + 1) * 8], "little")
        u2_bits = int.from_bytes(raw[(offset + 1) * 8:(offset + 2) * 8], "little")
        u1 = uniform_open(u1_bits)
        u2 = mp.mpf(u2_bits >> 11) * mp.power(2, -53)
        magnitude = mp.sqrt(-2 * mp.log(u1))
        angle = 2 * mp.pi * u2
        samples.extend((magnitude * mp.cos(angle), magnitude * mp.sin(angle)))

    radius_bits = int.from_bytes(raw[total * 8:(total + 1) * 8], "little")
    radius = R_PRIME * mp.power(uniform_open(radius_bits), mp.mpf(1) / total)
    factor = radius / mp.sqrt(mp.fsum(value * value for value in samples))

    for index, value in enumerate(samples[:OUTPUTS]):
        scaled = value * factor * (NU if index < L * N else 1)
        print(f"{float(scaled):.17g},")


if __name__ == "__main__":
    main()
