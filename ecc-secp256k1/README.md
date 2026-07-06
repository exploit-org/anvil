# anvil-ecc-secp256k1

Coordinates:

```text
org.exploit.anvil:ecc-secp256k1:0.2.0-SNAPSHOT
```

Java package:

```text
org.exploit.ecc.secp256k1
```

`ecc-secp256k1` provides secp256k1 keys, point operations, ECDSA, recoverable
ECDSA, BIP340 Schnorr signatures, Taproot key tweaking helpers, and
XMD:SHA-256 hash-to-curve mapping.

## Primary API

| Area | Types |
| --- | --- |
| Native loader | `LibSecp256k1` |
| Keys | `Secp256k1KeyFactory`, `Secp256k1PrivateKey`, `Secp256k1PublicKey`, `Secp256k1KeyPair` |
| Curve and points | `Secp256k1CurveParams`, `Secp256k1PointOps` |
| ECDSA | `Secp256k1ECDSASigner`, `Secp256k1ECDSAVerifier`, `Secp256k1ECDSASignature`, `Secp256k1RecoverableECDSASignature` |
| BIP340 | `Secp256k1BIP340Signer`, `Secp256k1BIP340Verifier`, `Secp256k1BIP340Signature` |
| Taproot | `Secp256k1TaprootSigner`, `Secp256k1TaprootVerifier`, `Taproot`, `TaggedHash` |
| Hash-to-curve | `Secp256k1HashToCurve`, `Secp256k1XmdSha256SSWUROSuite` |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.2.0-SNAPSHOT")
    implementation "org.exploit.anvil:ecc-secp256k1"
}
```

```java
import org.exploit.ecc.secp256k1.factory.Secp256k1KeyFactory;
import org.exploit.ecc.secp256k1.signer.ecdsa.Secp256k1ECDSASigner;
import org.exploit.ecc.secp256k1.signer.ecdsa.Secp256k1ECDSAVerifier;

var keys = new Secp256k1KeyFactory().generate();
var signer = new Secp256k1ECDSASigner();
var verifier = new Secp256k1ECDSAVerifier();

byte[] msg32 = new byte[32];
var signature = signer.sign(msg32, keys.privateKey());
boolean ok = verifier.verify(msg32, signature, keys.publicKey());
```

## Encoding

ECDSA signatures encode as compact `r || s` byte arrays. Recoverable ECDSA
signatures encode as `r || s || recId`. BIP340 signatures encode as 64-byte
signature arrays.

`Secp256k1PointOps.encode(true)` returns compressed SEC1 point bytes.
`Secp256k1PointOps.encode(false)` returns uncompressed SEC1 point bytes.

## Runtime

The module uses libsecp256k1 through Java FFM bindings. `LibSecp256k1.load()`
tries a bundled `natives/{os}-{arch}/` resource first, then falls back to
`System.loadLibrary("secp256k1")`.

Applications that use this module through the class path should launch with:

```bash
--enable-native-access=ALL-UNNAMED
```
