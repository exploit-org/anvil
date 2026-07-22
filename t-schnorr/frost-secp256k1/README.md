# anvil-frost-secp256k1

Coordinates:

```text
org.exploit.anvil:frost-secp256k1:0.2.0-SNAPSHOT
```

Java package:

```text
org.exploit.tss.frost.secp256k1
```

`frost-secp256k1` binds the FROST core module to secp256k1 point operations. It
contains schemes for generic Schnorr signatures, BIP340 signatures, and Taproot
tweaked BIP340 signatures.

## Primary API

| Area | Types |
| --- | --- |
| Schemes | `FrostSecp256k1Scheme`, `FrostBIP340Scheme`, `FrostTaprootScheme` |
| Suite | `FrostSecp256k1Sha256V1CipherSuite` |
| Signature | `Secp256k1SchnorrSignature` |
| Verification | `Secp256k1SchnorrVerifier` |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.2.0-SNAPSHOT")
    implementation "org.exploit.anvil:frost-secp256k1"
}
```

```java
import org.exploit.tss.frost.FrostClient;
import org.exploit.tss.frost.secp256k1.FrostBIP340Scheme;
import org.exploit.tss.frost.secp256k1.FrostTaprootScheme;

var bip340Client = new FrostClient<>(
    sessionId,
    frostContext,
    new FrostBIP340Scheme()
);

var taprootClient = new FrostClient<>(
    sessionId,
    frostContext,
    new FrostTaprootScheme(merkleRoot)
);
```

## Signature Forms

`FrostSecp256k1Scheme` builds `Secp256k1SchnorrSignature`.
`FrostBIP340Scheme` and `FrostTaprootScheme` build
`Secp256k1BIP340Signature`.

## Dependencies

This module depends on `t-schnorr`, `ecc-secp256k1`, `ecc-spi`, `bigint`, and
`util`. secp256k1 native runtime requirements come from `ecc-secp256k1`.
