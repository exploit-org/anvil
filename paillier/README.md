# anvil-paillier

Coordinates:

```text
org.exploit.anvil:paillier:0.3.0
```

Java package:

```text
org.exploit.crypto.paillier
```

`paillier` provides Paillier key generation, encryption/decryption, randomness
tracking, MtA helper flows, and Paillier-related zero-knowledge proof types.

## Primary API

| Area | Types |
| --- | --- |
| Encryption | `Paillier`, `PaillierEncryption`, `PaillierRandomizer` |
| Keys | `PaillierKeyPair`, `PaillierPublicKey`, `PaillierPrivateKey` |
| MtA | `MtAProtocol`, `MtAEncryptionResult`, `MtAInitiatorMessage`, `BasicMtAResult`, `ProvedMtAResult` |
| Setup | `ZKSetup` |
| ZK proofs | `PaillierRangeProof`, `PaillierRespondentProof`, `BiPrimeBlumProof`, `NoSmallFactorProof` |
| ZK provers | `PaillierRangeProver`, `PaillierRespondentProver`, `BiPrimeProver`, `NoSmallFactorProver` |
| ZK verifiers | `PaillierRangeVerifier`, `PaillierRespondentVerifier`, `BiPrimeVerifier`, `NoSmallFactorVerifier` |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.3.0")
    implementation "org.exploit.anvil:paillier"
}
```

```java
import org.exploit.bigint.BigInt;
import org.exploit.crypto.paillier.Paillier;

var keyPair = Paillier.generateKeyPair(2048);
var paillier = new Paillier(keyPair);

try (var message = BigInt.valueOf(42);
     var ciphertext = paillier.encrypt(message);
     var decrypted = paillier.decrypt(ciphertext)) {
    boolean ok = message.equals(decrypted);
}
```

## Message Range

`Paillier.encrypt(BigInt)` accepts messages in `[0, n)`.
`Paillier.decrypt(BigInt)` accepts ciphertexts in `[0, n^2)`.

`encryptWithRandomness(BigInt)` returns both the ciphertext and the random
value used by the encryption operation.

## MtA Flow

`MtAProtocol` exposes initiator and respondent helpers for encrypted
multiplication-to-additive-share flows:

```text
generateEncryption
generatePeerMessage
generateInitiatorMessage
computeCjWithY
verifyInitiatorRangeProof
verifyInitiatorFactorProof
verifyInitiatorBiPrimeProof
verifyRespondentProof
decryptCj
computeBeta
```

The proved respondent path is generic over `WeierstrassPointOps` and is used by
threshold modules that bind the proof to elliptic-curve values.

## Auxiliary setup certificates

`ZKSetup.generate(bits)` and `generateWithSecrets(bits)` generate a tough Blum
modulus and related bases `h1 = h2^lambda mod hatN`. Production parameters should
use at least 2048 bits; 512-bit parameters are supported for tests. Each factor's
quadratic-residue order is a product of distinct primes of at least 255 bits,
and the two orders are coprime. The shifted 256-bit random exponent relies on
the Short Exponent Indistinguishability (SEI) assumption described in
[ePrint 2024/1950, sections 2.3.2–2.3.3 and 5.6](https://eprint.iacr.org/2024/1950.pdf).

Transport all four fields, including the 6544-byte `proof()`:

```java
var received = new ZKSetup(hatN, h1, h2, proof);
received.requireVerified();
```

The 128-bit Fiat–Shamir proof establishes the exact relation `h1 in <h2>`;
it does not certify the factors or toughness of a received modulus. The honest
party's generator supplies the modulus structure needed for commitment binding.
Verifying the relation in a peer's parameters prevents an unmatched subgroup
from removing the commitment mask. Range, Respondent, NoSmallFactor, and proved
MtA paths enforce this check before secret computations. GG20 also checks at
`storeZKSetup`. Missing or invalid certificates are rejected.

Successful verification is cached only on that immutable certificate object.
It does not reuse setup generation or session proofs. `generateWithSecrets`
keeps local CRT factors until `ZKSetupSecrets.destroy()`; the exponent and proof
masks are erased during generation. Only `publicSetup()` goes on the wire.

Public proof responses use a temporary native GMP table for the common base;
secret proof masks still use secure CRT exponentiation. Independent arithmetic
runs in at most four slices per operation, with all slices joined before cleanup.
GG20 generates fresh Paillier keys and auxiliary parameters concurrently.

BiPrime sigma generation uses secure CRT with the prover's prime factors.
Local auxiliary verification also reduces long public exponents modulo the
prime orders in fixed-width native buffers. Short exponents retain the direct
path. These arithmetic changes preserve the proof values and formats.

The existing three-argument constructor and numeric accessors remain available;
that constructor creates an unverified representation. `ZKSetup` is now a final
class rather than a Java record. Transport adapters must add one byte-array
field and use the four-argument constructor. For threshold-keeper this means
adding `proof: ByteArray = byteArrayOf()` to `ZKSetupDto`, passing it to `unwrap`,
and including `proof()` in `ZKSetup.dto()`. All peers must send certificates;
the empty default allows decoding old data but does not authorize its use.

## Dependencies

This module depends on `bigint`, `ecc-spi`, `util`, and the ZK proof interfaces.
Paillier private-key and randomness-bearing model types implement
`Destroyable`, `AutoCloseable`, or both where the code stores native `BigInt`
values.
