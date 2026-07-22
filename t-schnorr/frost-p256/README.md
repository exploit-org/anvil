# anvil-frost-p256

Coordinates:

```text
org.exploit.anvil:frost-p256:0.2.0
```

Java package:

```text
org.exploit.tss.frost.p256
```

`frost-p256` binds the FROST core module to P-256 point operations and a
SHA-256 cipher suite.

## Primary API

| Type | Purpose |
| --- | --- |
| `FrostP256Scheme` | Builds P-256 Schnorr signatures from aggregated FROST state. |
| `FrostP256Sha256V1CipherSuite` | Scalar serialization and FROST hash functions over SHA-256. |
| `P256SchnorrSignature` | P-256 Schnorr signature representation. |
| `P256SchnorrVerifier` | Verifier for P-256 Schnorr signatures. |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.2.0")
    implementation "org.exploit.anvil:frost-p256"
}
```

```java
import org.exploit.tss.frost.FrostClient;
import org.exploit.tss.frost.p256.FrostP256Scheme;

var client = new FrostClient<>(
    sessionId,
    frostContext,
    new FrostP256Scheme()
);
```

## Dependencies

This module depends on `t-schnorr`, `ecc-p256`, `ecc-spi`, `bigint`, and `util`.
