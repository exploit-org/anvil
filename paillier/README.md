# anvil-paillier

Coordinates:

```text
org.exploit.anvil:paillier:0.2.0
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
    implementation platform("org.exploit.anvil:bom:0.2.0")
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

## Dependencies

This module depends on `bigint`, `ecc-spi`, `util`, and the ZK proof interfaces.
Paillier private-key and randomness-bearing model types implement
`Destroyable`, `AutoCloseable`, or both where the code stores native `BigInt`
values.
