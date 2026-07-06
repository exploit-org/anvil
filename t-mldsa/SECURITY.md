# Threshold ML-DSA Security Notes

This module implements the fresh-key Threshold ML-DSA construction from
"Efficient Threshold ML-DSA". It does not claim a new unconditional security
proof. Its security is conditional on the assumptions below.

## Security Model

- At most `T - 1` parties are statically corrupted.
- Party indices and the `(T, N, ML-DSA parameter set)` tuple are fixed before a
  protocol execution.
- The caller provides authenticated confidential point-to-point delivery for
  DKG subset seeds and consistent authenticated delivery for broadcasts.
- Honest parties use a cryptographically secure random source and erase
  short-lived signing and DKG state after use.
- SHAKE256 is modeled as a domain-separated random oracle. MLWE for the
  distributions used by ML-DSA and Threshold ML-DSA remains hard.
- An execution may abort. This module does not provide guaranteed output,
  robustness, proactive refresh, or a network blame protocol.

The paper proves signing in the classical random-oracle model with static
corruptions. It does not provide a QROM reduction for the complete threshold
protocol. Consequently, standard ML-DSA verification compatibility is proven,
but post-quantum security of the complete distributed protocol remains
conditional on extending the reduction to the QROM.

## Hyperball Sampler

For dimension `d`, the implementation samples independent standard normal
coordinates, normalizes their direction, and independently samples radius
`r * U^(1/d)`. In exact real arithmetic this is uniform in the `d`-dimensional
ball. Scaling the first `256*l` coordinates by `nu` produces the imbalanced
distribution used by the paper. Coefficient-wise rounding then produces the
specified integer distribution.

The implementation uses `StrictMath`, open-interval uniforms, compensated norm
summation, checked dimensions/nonces, and zeroes temporary buffers. The JUnit
suite checks radial distribution, directional moments, norm bounds, and a
control vector generated at 100 decimal digits by
`src/test/python/hypball_mpfr_oracle.py`.

These checks can find implementation errors; they are not a proof that binary64
sampling has negligible statistical distance from the ideal real distribution.
A complete proof additionally needs an anti-concentration bound for coordinates
near rounding boundaries and vectors near the rejection boundary.

## Parameter Bound

The paper chooses the partial-secret norm bound `B` as 1.3 times its predicted
root-mean-square norm and describes this as an experimental 13-standard-
deviation bound. `ThresholdMLDSAParameterAuditTest` performs two checks:

1. For all 45 supported parameter tuples, the published integer radii satisfy
   the paper's hyperball inequality using its `B` and `phi`, allowing one unit
   for the published radius rounding.
2. A deterministic Monte Carlo run computes the actual negacyclic product of
   uniformly sampled RSS partial secrets and sparse ML-DSA challenges and checks
   that no sample exceeds `B`.

The first check is deterministic. The second is reproducible empirical evidence,
not a tail proof at `2^-128` or at the paper's `2^50` query budget. A formal
production claim still requires a concentration bound for the correlated
negacyclic product followed by a union bound over signing queries and parties.
For a-posteriori keys, exact integer convolution additionally checks that the
second moment of every possible partial sum of conditioned shares, averaged over
the standard uniform ML-DSA source-secret distribution, does not exceed the
fresh-RSS variance budget used to derive `B`. This removes a variance mismatch;
it does not turn the paper's heuristic tail bound into a proof.

## DKG Argument

Let `C` be the corrupted set with `|C| < T`. There exists a subset `S*` of
`N - T + 1` honest parties. Its leader samples a secret seed unknown to `C`.
After the global commit/reveal, domain-separated `Hkeygen(S*, K_S*, R)` has the
required short-secret distribution in the random-oracle model. Under MLWE, its
public image hides that contribution and makes the aggregate public key
pseudorandom to `C`.

Every active set of `T` parties intersects every RSS subset of size
`N - T + 1`, so the deterministic recovery partition contains every base share
exactly once. This combinatorial property is exhaustively tested for every
`2 <= T <= N <= 6` and every active set.

Each DKG leader now publishes a 512-bit commitment to every private subset seed.
Recipients verify it before deriving shares. Therefore an accepted execution
binds all honest members of a subset to the same seed under SHAKE256 collision
resistance, without relying on equality of public MLWE images. Public
share commitments and the complete ordered commitment transcript are also
512-bit SHAKE256 values.

Commit/reveal prevents a rushing party from choosing its randomness after an
honest reveal, but it does not prevent selective abort across repeated DKG
sessions. A malicious party can condition termination on public `rho`. Retry
limits, session policy, authenticated transcripts, and exclusion/blame are the
responsibility of the integrating system.

## A-Posteriori Key Sharing

`ThresholdMLDSAKeySplitter` preserves the public key of an existing standard
ML-DSA private key. The source key must come from conforming randomized ML-DSA
key generation; structural validation cannot prove that provenance or the
required uniform secret distribution. For every coefficient `s`, the splitter
produces `S = C(N, T - 1)`
integer shares whose sum is exactly `s`. It samples `S - 1` independent
discrete Gaussians and accepts the forced last coordinate with probability
`rho(x) / rho(0)`. Conditioned on acceptance, the joint mass is therefore
proportional to

```text
product_i exp(-x_i^2 / (2 sigma^2))
```

on the coset `sum_i x_i = s`, which is the ideal distribution required by
Section E.2 of the paper. Centering at `(s/S,...,s/S)` gives the same
distribution because `sum_i (x_i-s/S)^2 = sum_i x_i^2-s^2/S` on that coset.
The full lattice is the direct product `A_(S-1)^m`, so coefficients may be
sampled independently. Unlike the paper's approximate `SampleDs`, this direct
rejection sampler targets the ideal coset Gaussian itself, up to the finite
table error below.

The practical profile uses conventional standard deviation
`sigma^2 = Var(U[-eta, eta])`: 2 for `eta = 2` and 20/3 for `eta = 4`. The
paper's appendix writes lattice Gaussian width `a` as `exp(-x^2/a^2)`; the
conversion is `a = sqrt(2) sigma`. Thus the implementation's eta-2 profile is
the paper's compact `sigma = sqrt(2)` standard-deviation profile, not a profile
narrower by a factor of `sqrt(2)`.

Sampling uses integer CDT tables with weights
`floor(2^384 exp(-x^2 / (2 sigma^2)))`, not binary floating point. Supports are
`[-30,30]` and `[-54,54]`. The omitted Gaussian tail and table quantization,
including conditioning for every supported `S <= 20`, are conservatively below
`2^-300` statistical distance. Exact integer convolution proves acceptance is
greater than 1/5 for every supported target and share count, so exhausting the
1024-attempt fail-closed limit has probability below `2^-300` with a correct
CSPRNG. Uniform integer draws also fail closed after 384 retries; each retry
accepts with probability at least 1/2, giving a per-draw failure bound of
`2^-384` and a full-operation union bound below `2^-350`. JUnit checks these
bounds from the actual tables; the independent
`src/test/python/key_sharing_gaussian_oracle.py` regenerates all table entries
at both 220 and 320 decimal digits and requires identical integer tables.

The paper explicitly does not reduce this compact profile with the standard
uniform ML-DSA secret distribution to standard MLWE. The formally analyzed
profile with at most 7 bits of loss uses wider shares and up to 10 times more
communication; it is not the profile implemented here. For the compact eta-2
profile, the paper's at-most-12-bit estimate is a lattice-estimator heuristic.
The eta-4 variance-matched profile follows the same construction, but the paper
does not publish a separate concrete 7-to-12-bit estimate for it. Security of
the compact profiles therefore relies on the generalized Hint-MLWE assumption,
not a reduction to standard MLWE. This implementation does not strengthen that
claim.

A source key must be shared only once: multiple independent short sharings
provide multiple hints about the same secret. For migration,
`splitAndDestroy` erases the in-memory source key after a successful split;
external copies and backups remain the caller's responsibility.

The sampler and Java `BigInteger` are not claimed to be constant-time. Key
sharing must run in the same protected local environment as ordinary ML-DSA key
generation, without exposing fine-grained timing to an attacker.

## Distribution Estimation

`src/test/python/hyperball_estimator_profile.py` emits exact support and marginal
variance profiles for `chi_r` and `chi_z` for all supported tuples. Standard
lattice estimators assume independent coefficient distributions, while uniform
hyperball coordinates are correlated. Treating the emitted marginal standard
deviations as independent Gaussian inputs is a heuristic proxy, not a reduction
or proof for the actual MLWE distribution.
