# anvil-ecc-p256

Coordinates:

```text
org.exploit.anvil:ecc-p256:0.2.0-SNAPSHOT
```

Java package:

```text
org.exploit.ecc.p256
```

`ecc-p256` provides P-256 keys, point operations, ECDSA, recoverable ECDSA
support, and XMD:SHA-256 hash-to-curve mapping.

## Primary API

| Area | Types |
| --- | --- |
| Keys | `P256KeyFactory`, `P256PrivateKey`, `P256PublicKey`, `P256KeyPair` |
| Curve and points | `P256CurveParams`, `P256PointOps` |
| ECDSA | `P256ECDSASigner`, `P256ECDSAVerifier`, `P256ECDSASignature` |
| Recoverable ECDSA | `P256RecoverableECDSASigner`, `P256RecoverableECDSASignature` |
| Hash-to-curve | `P256HashToCurve`, `P256XmdSha256SSWUROSuite` |
| Field arithmetic | `Secp256R1Field` |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.2.0-SNAPSHOT")
    implementation "org.exploit.anvil:ecc-p256"
}
```

```java
import org.exploit.ecc.p256.factory.P256KeyFactory;
import org.exploit.ecc.p256.signer.P256ECDSASigner;
import org.exploit.ecc.p256.signer.P256ECDSAVerifier;

var keys = new P256KeyFactory().generate();
var signer = new P256ECDSASigner();
var verifier = new P256ECDSAVerifier();

byte[] msg32 = new byte[32];
var signature = signer.sign(msg32, keys.privateKey());
boolean ok = verifier.verify(msg32, signature, keys.publicKey());
```

## Encoding

ECDSA signatures encode as compact `r || s` byte arrays. Recoverable signatures
append a one-byte recovery id. `P256PointOps` supports compressed and
uncompressed SEC1 point encodings.

## Dependencies

This module depends on `ecc-spi`, `util`, and Bouncy Castle `bcprov-jdk18on`.
It uses the shared `bigint` API through `ecc-spi`.
