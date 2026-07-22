# anvil-frost-ed25519

Coordinates:

```text
org.exploit.anvil:frost-ed25519:0.2.0
```

Java package:

```text
org.exploit.tss.frost.ed25519
```

`frost-ed25519` binds the FROST core module to Ed25519 point operations and a
SHA-512 cipher suite.

## Primary API

| Type | Purpose |
| --- | --- |
| `FrostEd25519Scheme` | Builds Ed25519 FROST signatures from aggregated FROST state. |
| `FrostEd25519Sha512V1CipherSuite` | Scalar serialization and FROST hash functions over SHA-512. |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.2.0")
    implementation "org.exploit.anvil:frost-ed25519"
}
```

```java
import org.exploit.tss.frost.FrostClient;
import org.exploit.tss.frost.ed25519.FrostEd25519Scheme;

var client = new FrostClient<>(
    sessionId,
    frostContext,
    new FrostEd25519Scheme()
);
```

## Dependencies

This module depends on `t-schnorr`, `ecc-ed25519`, `ecc-spi`, `bigint`, and
`util`. Ed25519 native runtime requirements come from `ecc-ed25519`.
